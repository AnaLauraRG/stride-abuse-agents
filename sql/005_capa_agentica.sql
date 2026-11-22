-- =====================================================================
-- Fase 6 · Capa agéntica. Ejecutar una vez en el SQL Editor de Supabase. Idempotente.
--
-- 1. ltm_contexto: recupera el contexto de un caso de uso desde los tres segmentos de la
--    memoria de largo plazo, con CUOTAS POR FUENTE. En la Fase 5 se vio que, sin cuotas,
--    los fragmentos en español (patrones propios) desplazan por completo a CAPEC y OWASP.
-- 2. ejecuciones.resultado: guarda la salida final de cada ejecución de WF-2, que WF-3
--    usa para consolidar los casos aprobados por el analista.
-- =====================================================================

create or replace function public.ltm_contexto(
  query_embedding extensions.vector(1024),
  excluir_id text default null
) returns table (segmento text, fuente text, id text, content text, similarity float)
language sql stable
set search_path = public, extensions
as $$
  -- Negocio: flujos, supuestos, reglas y límites cercanos (el caso de uso pedido ya se envía completo).
  (select 'negocio', n.metadata->>'fuente', n.metadata->>'id', n.content,
          1 - (n.embedding <=> query_embedding)
   from public.ltm_negocio n
   where n.metadata->>'id' is distinct from excluir_id
   order by n.embedding <=> query_embedding limit 6)
  union all
  -- Amenazas: patrones propios (fraude y STRIDE).
  (select 'amenazas', a.metadata->>'fuente', a.metadata->>'id', a.content,
          1 - (a.embedding <=> query_embedding)
   from public.ltm_amenazas a
   where a.metadata->>'fuente' in ('fraude', 'stride')
   order by a.embedding <=> query_embedding limit 4)
  union all
  -- Amenazas: MITRE CAPEC.
  (select 'amenazas', a.metadata->>'fuente', a.metadata->>'id', a.content,
          1 - (a.embedding <=> query_embedding)
   from public.ltm_amenazas a
   where a.metadata->>'fuente' = 'capec'
   order by a.embedding <=> query_embedding limit 3)
  union all
  -- Amenazas: OWASP API Top 10 y Automated Threats.
  (select 'amenazas', a.metadata->>'fuente', a.metadata->>'id', a.content,
          1 - (a.embedding <=> query_embedding)
   from public.ltm_amenazas a
   where a.metadata->>'fuente' in ('owasp-api', 'owasp-oat')
   order by a.embedding <=> query_embedding limit 3)
  union all
  -- Casos de abuso validados y sus patrones abstractos.
  (select 'abusos', b.metadata->>'fuente', b.metadata->>'id', b.content,
          1 - (b.embedding <=> query_embedding)
   from public.ltm_abusos b
   order by b.embedding <=> query_embedding limit 5)
$$;

revoke all on function public.ltm_contexto(extensions.vector, text) from public, anon, authenticated;
grant execute on function public.ltm_contexto(extensions.vector, text) to service_role;

alter table public.ejecuciones add column if not exists resultado jsonb;

-- Comprobación: el contexto de UC-11 (esperado: 6 negocio, 4 propios, 3 capec, 3 owasp y,
-- mientras ltm_abusos esté vacía, 0 abusos).
select c.segmento, c.fuente, c.id, round(c.similarity::numeric, 3) as similitud
from public.ltm_contexto(
  (select embedding from public.ltm_negocio where metadata->>'id' = 'UC-11' limit 1), 'UC-11'
) c;
