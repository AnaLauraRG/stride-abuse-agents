-- Verificación de la memoria de largo plazo después de ejecutar WF-1 (Fase 5).
-- Ejecutar cada bloque por separado en el SQL Editor de Supabase.

-- 1. Fragmentos por tabla y fuente.
--    Esperado: ltm_negocio 91 (casos_de_uso 16, flujos 30, limites 6, reglas 4, supuestos 35)
--              ltm_amenazas 281 (capec 218, fraude 17, owasp-api 19, owasp-oat 20, stride 7)
select 'ltm_negocio' as tabla, metadata->>'fuente' as fuente, count(*) as fragmentos,
       count(*) filter (where embedding is null) as sin_vector
from public.ltm_negocio group by 2
union all
select 'ltm_amenazas', metadata->>'fuente', count(*), count(*) filter (where embedding is null)
from public.ltm_amenazas group by 2
order by 1, 2;

-- 2. Búsqueda semántica sin LLM: usa el vector del patrón FE-07 (entrega registrada sin haber
--    entregado) como consulta y muestra los 8 fragmentos de amenazas más parecidos.
--    Esperado: el propio FE-07 primero (similitud 1) y después patrones de suplantación,
--    colusión o falsificación de evidencia, no temas ajenos.
select m.metadata->>'fuente' as fuente, m.metadata->>'id' as id, m.metadata->>'nombre' as nombre,
       round(m.similarity::numeric, 3) as similitud
from public.match_ltm_amenazas(
  (select embedding from public.ltm_amenazas where metadata->>'id' = 'FE-07' limit 1), 8, '{}'::jsonb
) m;

-- 3. Lo mismo desde el negocio: el caso de uso UC-11 contra la memoria de amenazas.
--    Muestra qué conocimiento recibiría el generador para UC-11.
select m.metadata->>'fuente' as fuente, m.metadata->>'id' as id, m.metadata->>'nombre' as nombre,
       round(m.similarity::numeric, 3) as similitud
from public.match_ltm_amenazas(
  (select embedding from public.ltm_negocio where metadata->>'id' = 'UC-11' limit 1), 8, '{}'::jsonb
) m;

-- 4. Filtro por metadatos: solo patrones de fraude cercanos a UC-13 (cancelación y devolución).
select m.metadata->>'id' as id, m.metadata->>'nombre' as nombre, round(m.similarity::numeric, 3) as similitud
from public.match_ltm_amenazas(
  (select embedding from public.ltm_negocio where metadata->>'id' = 'UC-13' limit 1), 5, '{"fuente": "fraude"}'::jsonb
) m;
