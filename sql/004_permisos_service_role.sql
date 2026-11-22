-- Corrección de la Fase 5: da a service_role (la clave secreta usada por n8n) los permisos
-- sobre las tablas de memoria. Necesario en proyectos de Supabase que no otorgan permisos
-- automáticos a las tablas nuevas. Idempotente. Ya está incluido en 001_esquema.sql.
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

-- Comprobación (esperado: 5 filas con select, insert, update y delete en true)
select c.relname as tabla,
       has_table_privilege('service_role', c.oid, 'select') as sel,
       has_table_privilege('service_role', c.oid, 'insert') as ins,
       has_table_privilege('service_role', c.oid, 'update') as upd,
       has_table_privilege('service_role', c.oid, 'delete') as del,
       has_table_privilege('anon', c.oid, 'select') as anon_sel
from pg_class c
where c.relnamespace = 'public'::regnamespace
  and c.relname in ('ltm_negocio','ltm_amenazas','ltm_abusos','ejecuciones','ejecucion_pasos')
order by 1;
