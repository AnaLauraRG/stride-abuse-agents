-- Verificación del esquema (Fase 4). Ejecutar en el SQL Editor de Supabase después de 001_esquema.sql.
-- Resultado esperado: 5 tablas con RLS activado, 4 funciones, extensión vector instalada.

-- 1. Tablas y RLS (esperado: 5 filas, rls_activado = true en todas)
select tablename as tabla, rowsecurity as rls_activado
from pg_tables
where schemaname = 'public'
  and tablename in ('ltm_negocio', 'ltm_amenazas', 'ltm_abusos', 'ejecuciones', 'ejecucion_pasos')
order by tablename;

-- 2. Funciones (esperado: 4 filas)
select proname as funcion
from pg_proc
where pronamespace = 'public'::regnamespace
  and proname in ('match_ltm_negocio', 'match_ltm_amenazas', 'match_ltm_abusos', 'ltm_borrar_fuente')
order by proname;

-- 3. Extensión pgvector (esperado: 1 fila, esquema extensions)
select extname as extension, extversion as version, extnamespace::regnamespace as esquema
from pg_extension
where extname = 'vector';

-- 4. Dimensión de los vectores (esperado: 3 filas con vector(1024))
select table_name as tabla, format_type(a.atttypid, a.atttypmod) as tipo
from information_schema.columns c
join pg_attribute a
  on a.attrelid = ('public.' || c.table_name)::regclass and a.attname = c.column_name
where c.table_schema = 'public' and c.column_name = 'embedding'
order by table_name;

-- 5. La reingesta rechaza ltm_abusos (esperado: ERROR "Tabla no permitida: ltm_abusos").
--    Ejecutar esta línea sola, aparte de las consultas anteriores.
-- select public.ltm_borrar_fuente('ltm_abusos', 'prueba');
