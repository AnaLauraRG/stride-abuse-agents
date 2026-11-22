# Fase 6 · Capa agéntica

Esta fase implementa la **capa agéntica** (requisito A4) y los **prompts** (B1 a B4c), y completa la memoria de largo plazo con el segmento `ltm_abusos` (A2). El diseño está en [`03-arquitectura.md`](03-arquitectura.md) §5.

| Flujo | Archivo | Nodos | Qué hace |
|---|---|---|---|
| WF-2 · Generación | [`n8n/WF-2-generacion.json`](../n8n/WF-2-generacion.json) | 23 | Recibe de 1 a 5 casos de uso; por cada uno recupera contexto de la memoria, genera casos de abuso, los revisa (con reintentos), propone mitigaciones y registra cada paso |
| WF-3 · Consolidación | [`n8n/WF-3-consolidacion.json`](../n8n/WF-3-consolidacion.json) | 13 | Toma los casos que el analista aprueba de una ejecución de WF-2, les agrega un patrón abstracto y los guarda en `ltm_abusos` |

Otros archivos: [`prompts/`](../prompts) (los cuatro prompts y los esquemas JSON de salida) y [`sql/005_capa_agentica.sql`](../sql/005_capa_agentica.sql) (recuperación con cuotas y la columna `resultado`).

## 1. WF-2 · Generación de casos de abuso

```
Entrada → Configuración → Leer casos de uso (ltm_negocio) → Validar entrada → Crear ejecución (corto plazo)
  → Caso por caso ─┬─► Embedding del caso de uso → Recuperar contexto (ltm_contexto)
                   │     → Preparar generación → Agente generador → Preparar revisión (R1, R2) → Agente revisor
                   │     → Evaluar revisión → ¿Reintentar? ─ sí ─► (vuelve a Preparar generación con las observaciones)
                   │                                      └ no ─► Preparar mitigación → Agente de mitigación
                   │     → Cerrar caso de uso → Guardar pasos (corto plazo) ─► (siguiente caso de uso)
                   └─ al terminar ─► Armar resultado → Cerrar ejecución → Resultado
```

| Nodo | Tipo | Detalle |
|---|---|---|
| Entrada | Datos | `casos_de_uso`: JSON con IDs (`["UC-11","UC-13"]`) u objetos de texto libre (`{"id":"UC-X1","nombre":"…","descripcion":"…"}`) |
| Configuración | Datos | URLs, modelo (`claude-sonnet-5-5`), `max_tokens` 8000, `max_reintentos` 2, `max_casos` 5. Sin secretos |
| Leer casos de uso | Supabase | El texto completo de cada caso de uso sale de la memoria `ltm_negocio`, no de un archivo |
| Validar entrada | Código | IDs existentes, máximo 5 casos, sin repetidos; el texto libre se recorta (3 000 caracteres) |
| Crear ejecución | Supabase | Fila en `ejecuciones` (memoria de corto plazo) con estado `en_curso`; devuelve el `run_id` |
| Caso por caso | Bucle | Un caso de uso a la vez |
| Embedding del caso de uso | Ollama | Vector del caso de uso con bge-m3 |
| Recuperar contexto (LTM) | Supabase | `ltm_contexto`: 6 de negocio, 4 patrones propios, 3 CAPEC, 3 OWASP y hasta 5 casos validados |
| Preparar generación | Código | Arma la petición al generador: prompt público + caso de uso + contexto entre etiquetas + esquema JSON de salida (*structured outputs*). En un reintento agrega `<correcciones>` |
| Agente generador | Claude Sonnet 5.5 | Devuelve los casos de abuso en JSON, según el esquema del generador |
| Preparar revisión | Código | **R1** (el caso cita el caso de uso correcto) y **R2** (campos obligatorios completos), deterministas; normaliza los IDs `AC-UCxx-NN` |
| Agente revisor | Claude Sonnet 5.5 | Evalúa R3 a R7 de cada caso (JSON del esquema del revisor) |
| Evaluar revisión | Código | Aprueba solo con todos los criterios cumplidos. Si hay rechazados y quedan intentos, los devuelve al generador con las observaciones; si no, los marca como descartados |
| ¿Reintentar? | IF | Máximo 2 reintentos por caso de uso (3 llamadas al generador en total) |
| Preparar mitigación / Agente de mitigación | Código / Claude | Riesgo (probabilidad × impacto) y controles por caso aprobado |
| Cerrar caso de uso | Código | Une casos y mitigaciones; arma un registro por paso (recuperador, generador, revisor, mitigación) |
| Guardar pasos | Supabase | Inserta los pasos en `ejecucion_pasos` |
| Armar resultado | Código | Construye el resultado **a partir de lo guardado en la memoria de corto plazo**: JSON + Markdown, resumen y tokens |
| Cerrar ejecución | Supabase | `ejecuciones.estado = completada`, con `resultado` y `tokens` |

### Salida estructurada

Cada petición a Claude lleva el esquema JSON del agente ([`prompts/esquemas.json`](../prompts/esquemas.json)) en `output_config.format` (*structured outputs* de la API de Claude). La API restringe la respuesta a ese esquema, así que siempre es JSON válido con los campos del contrato de [`03-arquitectura.md`](03-arquitectura.md) §5.2, sin depender de que el modelo "respete un formato" escrito en el prompt. El código de n8n además revisa `stop_reason` (`refusal`, `max_tokens`) antes de leer el JSON.

La primera versión forzaba una herramienta con `tool_choice`, pero la API respondió que Sonnet 5.5 no admite `tool_choice` de tipo `tool` o `any`. Se cambió a *structured outputs*, que es el mecanismo documentado para obtener la respuesta en un esquema JSON.

### Memoria de corto plazo

Cada ejecución deja en Supabase:
- una fila en `ejecuciones`, con la entrada, los modelos, el estado, el resultado final y los tokens;
- una fila por paso en `ejecucion_pasos`. Por ejemplo, para un caso de uso con un reintento: recuperador → generador (1) → revisor (1) → generador (2) → revisor (2) → mitigación.

Es la evidencia de cada ejecución y lo que permite saber qué contexto recibió el generador, qué rechazó el revisor y por qué.

### Rechazos de la API (*refusal*)

La API de Claude puede devolver `stop_reason: "refusal"` cuando sus filtros de seguridad consideran que una respuesta se acerca demasiado a instrucciones de ataque operativas. En el primer lote real (UC-01 a UC-05), el revisor recibió un *refusal* en UC-03 y la ejecución se detuvo. Se hicieron dos cambios:

1. **Nivel de detalle.** El mensaje al generador pide describir cada vector "a nivel de acción, herramienta y dato manipulado, como en un modelado de amenazas", sin comandos, código, *payloads* ni instrucciones operativas de explotación. Así se sigue cumpliendo B4c (vectores prácticos) sin producir un manual de ataque. El prompt público de 96 palabras no cambia.
2. **Un *refusal* ya no detiene el lote.** Si lo recibe el generador o el revisor, los casos de ese intento se marcan como rechazados con una observación que pide reformularlos con ese nivel de detalle, y se reintenta (dentro del límite de 2 reintentos). Si lo recibe el agente de mitigación, los casos quedan sin controles. En todos los casos el paso queda registrado en `ejecucion_pasos` con `refusal: true`.

Prueba: con la API simulada devolviendo *refusal* al revisor en el primer intento de UC-03, el flujo reintentó, aprobó los casos en el intento 2 y terminó en `success`.

## 2. WF-3 · Consolidación en la memoria de largo plazo

| Nodo | Detalle |
|---|---|
| Selección del analista | `run_id` de la ejecución de WF-2, `aprobar` (`"todos"` o `["AC-UC11-01", …]`) y `aprobado_por` |
| Leer ejecución / Leer ltm_abusos | La ejecución debe estar `completada`; se leen los casos ya guardados |
| Validar selección | Solo casos de esa ejecución; **no consolida dos veces el mismo caso**; asigna IDs `AV-0001`, `AV-0002`… |
| Agente de abstracción | Claude Haiku 5.5 redacta el patrón abstracto y las palabras clave (JSON del esquema de abstracción) |
| Armar fragmentos / Embeddings / Insertar | Fragmento = caso concreto + patrón; vector con bge-m3; inserción en `ltm_abusos` con metadatos (`origen`, `run_id`, `aprobado_por`, `fecha`, `patron`, `stride`…) |
| Registrar en memoria de corto plazo | Paso `abstraccion` en `ejecucion_pasos` |

WF-3 es el **único camino de escritura** a `ltm_abusos` y siempre pasa por la decisión de una persona (supuesto S-30). En la siguiente ejecución de WF-2, `ltm_contexto` recupera esos casos y patrones para cualquier caso de uso parecido, y el generador recibe la instrucción de no repetirlos.

## 3. Prompts

Están en [`prompts/README.md`](../prompts/README.md), con la tabla que muestra cómo el prompt público (96 palabras) cumple B1 a B4c.

## 4. Pruebas antes de la entrega

Los flujos se ejecutaron en n8n 2.48.6 (la misma versión del contenedor) contra PostgreSQL 16 + pgvector con el esquema `001` a `005`, servido por PostgREST, con Ollama simulado y con una **API de Claude simulada**. La simulación devuelve respuestas con la misma forma que la API real (bloque de texto con el JSON, `usage`, `stop_reason`) y **rechaza con error 400** cualquier petición que use `tool_choice` o que no traiga `output_config.format`, igual que la API real con Sonnet 5.5. No se usó la API real en estas pruebas: no se gastaron créditos y la clave nunca salió de la VM.

| Prueba | Resultado |
|---|---|
| WF-2 con `["UC-11","UC-13"]`; el generador simulado devuelve un caso bueno y uno con vector genérico | `success`. El revisor rechaza el genérico (R4), el generador lo corrige en el intento 2, se aprueba. 4 casos aprobados, 0 descartados |
| Encabezados hacia Claude | `x-api-key` (de la credencial), `anthropic-version: 2023-06-01`, modelo `claude-sonnet-5-5`; *system prompt* del generador de 96 palabras |
| Memoria de corto plazo | `ejecuciones` en `completada`, con resultado y tokens; 6 pasos por caso de uso en `ejecucion_pasos` |
| WF-2 con un caso de uso en texto libre cuyo vector sigue siendo genérico tras 2 correcciones | El generador se llama 3 veces; el caso queda en "descartados" con la observación del revisor; la ejecución termina bien |
| WF-3 aprobando 2 casos | `success`: `AV-0001` y `AV-0002` en `ltm_abusos` con vector, patrón y `aprobado_por`; paso `abstraccion` registrado |
| WF-3 repetido con la misma selección | Error controlado: "No hay casos nuevos que consolidar". No duplica |
| WF-2 después de consolidar | `ltm_contexto` devuelve los casos validados y el generador los recibe en `<casos_validados>` |

La calidad real de los casos de abuso (que no sean genéricos, que los vectores sean prácticos) solo se puede evaluar con Claude real: es la Fase 7.

## 5. Instalación en la VM

1. En Supabase, SQL Editor: ejecutar [`sql/005_capa_agentica.sql`](../sql/005_capa_agentica.sql). La consulta final debe mostrar 16 filas para UC-11: 6 de negocio y 10 de amenazas (4 propias, 3 CAPEC, 3 OWASP).
2. En n8n, importar `n8n/WF-2-generacion.json` y `n8n/WF-3-consolidacion.json`.
3. En cada flujo:
   - **Configuración:** poner la Project URL en `supabase_url`.
   - **Nodos de Supabase:** elegir la credencial de Supabase (WF-2: 6 nodos; WF-3: 4 nodos).
   - **Nodos de agentes:** elegir la credencial de Anthropic (WF-2: generador, revisor y mitigación; WF-3: abstracción).
4. Guardar ambos flujos.

## 6. Costo

Por caso de uso, sin reintentos: unas 3 llamadas a Sonnet 5.5, con unos 12 000 tokens de entrada y 6 000 de salida, es decir, entre 0.08 y 0.12 USD. Con reintentos, hasta el doble. La consolidación con Haiku cuesta menos de un centavo por ejecución. El límite de gasto configurado en la consola de Claude (Fase 4) protege de un bucle inesperado; además, WF-2 limita a 5 casos de uso y 2 reintentos por ejecución.
