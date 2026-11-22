-- =====================================================================
-- Esquema de la memoria del sistema de agentes (Reto 2)
-- Ejecutar una vez en Supabase: SQL Editor → New query → pegar → Run.
-- Es idempotente: se puede volver a ejecutar sin borrar datos.
--
-- Memoria de largo plazo (pgvector, bge-m3 = 1024 dimensiones):
--   ltm_negocio   contexto del caso (casos de uso, flujos, supuestos, reglas, límites)
--   ltm_amenazas  conocimiento general (STRIDE, CAPEC, OWASP, fraude)
--   ltm_abusos    casos de abuso validados y su patrón abstracto
-- Memoria de corto plazo (tablas normales):
--   ejecuciones, ejecucion_pasos
-- =====================================================================

create extension if not exists vector with schema extensions;

-- ---------------------------------------------------------------------
-- Memoria de largo plazo
-- Columnas content / metadata / embedding: las que usa el nodo
-- "Supabase Vector Store" de n8n.
-- ---------------------------------------------------------------------
create table if not exists public.ltm_negocio (
  id        bigserial primary key,
  content   text  not null,
  metadata  jsonb not null default '{}'::jsonb,
  embedding extensions.vector(1024)
);

create table if not exists public.ltm_amenazas (
  id        bigserial primary key,
  content   text  not null,
  metadata  jsonb not null default '{}'::jsonb,
  embedding extensions.vector(1024)
);

create table if not exists public.ltm_abusos (
  id        bigserial primary key,
  content   text  not null,
  metadata  jsonb not null default '{}'::jsonb,
  embedding extensions.vector(1024)
);

-- Índices de búsqueda por similitud (coseno) y por metadatos.
create index if not exists ltm_negocio_embedding_idx  on public.ltm_negocio  using hnsw (embedding extensions.vector_cosine_ops);
create index if not exists ltm_amenazas_embedding_idx on public.ltm_amenazas using hnsw (embedding extensions.vector_cosine_ops);
create index if not exists ltm_abusos_embedding_idx   on public.ltm_abusos   using hnsw (embedding extensions.vector_cosine_ops);
create index if not exists ltm_negocio_metadata_idx   on public.ltm_negocio  using gin (metadata);
create index if not exists ltm_amenazas_metadata_idx  on public.ltm_amenazas using gin (metadata);
create index if not exists ltm_abusos_metadata_idx    on public.ltm_abusos   using gin (metadata);

-- Funciones de búsqueda: una por tabla, porque el nodo de n8n la llama por nombre
-- (campo "Query Name"). Firma compatible: (query_embedding, match_count, filter).
create or replace function public.match_ltm_negocio(
  query_embedding extensions.vector(1024),
  match_count int default 6,
  filter jsonb default '{}'::jsonb
) returns table (id bigint, content text, metadata jsonb, similarity float)
language sql stable
set search_path = public, extensions
as $$
  select t.id, t.content, t.metadata, 1 - (t.embedding <=> query_embedding) as similarity
  from public.ltm_negocio t
  where t.metadata @> filter
  order by t.embedding <=> query_embedding
  limit match_count;
$$;

create or replace function public.match_ltm_amenazas(
  query_embedding extensions.vector(1024),
  match_count int default 8,
  filter jsonb default '{}'::jsonb
) returns table (id bigint, content text, metadata jsonb, similarity float)
language sql stable
set search_path = public, extensions
as $$
  select t.id, t.content, t.metadata, 1 - (t.embedding <=> query_embedding) as similarity
  from public.ltm_amenazas t
  where t.metadata @> filter
  order by t.embedding <=> query_embedding
  limit match_count;
$$;

create or replace function public.match_ltm_abusos(
  query_embedding extensions.vector(1024),
  match_count int default 5,
  filter jsonb default '{}'::jsonb
) returns table (id bigint, content text, metadata jsonb, similarity float)
language sql stable
set search_path = public, extensions
as $$
  select t.id, t.content, t.metadata, 1 - (t.embedding <=> query_embedding) as similarity
  from public.ltm_abusos t
  where t.metadata @> filter
  order by t.embedding <=> query_embedding
  limit match_count;
$$;

-- Reingesta idempotente (WF-1): borra los fragmentos de una fuente antes de volver a insertarlos.
-- Solo acepta las dos tablas que alimenta WF-1; ltm_abusos solo la escribe WF-3.
create or replace function public.ltm_borrar_fuente(p_tabla text, p_fuente text)
returns integer
language plpgsql
set search_path = public
as $$
declare
  borrados integer;
begin
  if p_tabla not in ('ltm_negocio', 'ltm_amenazas') then
    raise exception 'Tabla no permitida: %', p_tabla;
  end if;
  execute format('delete from public.%I where metadata->>''fuente'' = $1', p_tabla)
    using p_fuente;
  get diagnostics borrados = row_count;
  return borrados;
end;
$$;

-- ---------------------------------------------------------------------
-- Memoria de corto plazo
-- ---------------------------------------------------------------------
create table if not exists public.ejecuciones (
  run_id  uuid primary key default gen_random_uuid(),
  creada  timestamptz not null default now(),
  entrada jsonb not null,
  estado  text not null default 'en_curso'
          check (estado in ('en_curso', 'completada', 'fallida')),
  modelos jsonb,
  tokens  jsonb
);

create table if not exists public.ejecucion_pasos (
  id          bigserial primary key,
  run_id      uuid not null references public.ejecuciones(run_id) on delete cascade,
  caso_de_uso text,
  agente      text not null
              check (agente in ('recuperador', 'generador', 'revisor', 'mitigacion', 'abstraccion')),
  intento     int  not null default 1,
  entrada     jsonb,
  salida      jsonb,
  creada      timestamptz not null default now()
);

create index if not exists ejecucion_pasos_run_idx on public.ejecucion_pasos (run_id);

-- ---------------------------------------------------------------------
-- Acceso
-- RLS activado y sin políticas: las claves públicas (anon / publishable) no ven nada.
-- Solo la clave secreta (rol service_role), que vive en las credenciales de n8n, accede.
-- ---------------------------------------------------------------------
alter table public.ltm_negocio     enable row level security;
alter table public.ltm_amenazas    enable row level security;
alter table public.ltm_abusos      enable row level security;
alter table public.ejecuciones     enable row level security;
alter table public.ejecucion_pasos enable row level security;

-- Permisos explícitos sobre las tablas: los proyectos nuevos de Supabase pueden no dar permisos
-- automáticos a las tablas creadas desde el SQL Editor. Solo service_role los recibe.
grant usage on schema public, extensions to service_role;
grant select, insert, update, delete on
  public.ltm_negocio, public.ltm_amenazas, public.ltm_abusos,
  public.ejecuciones, public.ejecucion_pasos
  to service_role;
grant usage, select on all sequences in schema public to service_role;
revoke all on
  public.ltm_negocio, public.ltm_amenazas, public.ltm_abusos,
  public.ejecuciones, public.ejecucion_pasos
  from anon, authenticated;

revoke all on function public.match_ltm_negocio(extensions.vector, int, jsonb)  from public, anon, authenticated;
revoke all on function public.match_ltm_amenazas(extensions.vector, int, jsonb) from public, anon, authenticated;
revoke all on function public.match_ltm_abusos(extensions.vector, int, jsonb)   from public, anon, authenticated;
revoke all on function public.ltm_borrar_fuente(text, text)                     from public, anon, authenticated;
grant execute on function public.match_ltm_negocio(extensions.vector, int, jsonb)  to service_role;
grant execute on function public.match_ltm_amenazas(extensions.vector, int, jsonb) to service_role;
grant execute on function public.match_ltm_abusos(extensions.vector, int, jsonb)   to service_role;
grant execute on function public.ltm_borrar_fuente(text, text)                     to service_role;
