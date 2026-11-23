# Componentes, quién los ejecuta y esquema de permisos

Este documento reúne, en un solo lugar, qué hace cada flujo y cada agente del sistema, quién puede ejecutarlo y qué puede leer o escribir cada parte. El diseño detallado está en [`03-arquitectura.md`](03-arquitectura.md) y la implementación en [`06-agentes.md`](06-agentes.md).

## 1. Flujos: qué hace cada uno y quién lo ejecuta

Los tres flujos de n8n se ejecutan a mano, con su disparador manual. Solo puede hacerlo quien tiene la cuenta de propietario de n8n, que escucha únicamente en `127.0.0.1`: en este sistema, el **analista de seguridad**.

| Flujo | Qué hace | Entrada | Salida | Quién lo ejecuta y cuándo |
|---|---|---|---|---|
| **WF-1 · Ingesta** | Carga la memoria de largo plazo: lee los fragmentos de `data/memoria/`, calcula su vector con bge-m3 y los guarda en `ltm_negocio` y `ltm_amenazas`. Antes de cargar una fuente borra sus fragmentos anteriores, así que se puede repetir sin duplicar | Ninguna: lee los archivos del repositorio | 372 fragmentos con vector (91 de negocio y 281 de amenazas) | El analista, una vez al instalar y cada vez que cambian las fuentes de datos |
| **WF-2 · Generación** | Por cada caso de uso: recupera contexto de la memoria, genera casos de abuso STRIDE, los revisa (con hasta 2 reintentos), propone controles y estima el riesgo. Registra cada paso | De 1 a 5 casos de uso, por ID (`["UC-11"]`) o como texto libre | `run_id` y casos de abuso con controles, en JSON y Markdown | El analista, cada vez que quiere analizar casos de uso |
| **WF-3 · Consolidación** | Toma los casos de abuso que el analista aprueba de una ejecución de WF-2, les agrega un patrón abstracto y los guarda en `ltm_abusos`, para que las siguientes ejecuciones los usen | `run_id`, la lista de casos aprobados y quién aprueba | Casos consolidados con su ID `AV-NNNN` | El analista, **después de revisar** el resultado de WF-2: es el paso de aprobación humana |

## 2. Agentes: qué hace cada uno

Los agentes viven dentro de WF-2 y WF-3. Ninguno tiene herramientas: no leen ni escriben en la base, no llaman a otros sistemas y no ejecutan código. Reciben texto que prepara el orquestador y devuelven JSON validado contra un esquema. Todas las lecturas y escrituras las hace el orquestador de n8n.

| Componente | Flujo | Tipo | Qué hace | Recibe | Devuelve |
|---|---|---|---|---|---|
| Orquestador | WF-2, WF-3 | Lógica determinista de n8n | Valida la entrada, crea la ejecución, recorre los casos de uso, controla los reintentos, lee y escribe en la memoria | La entrada del analista | El resultado final |
| Recuperador de contexto | WF-2 | Embeddings (bge-m3) + función `ltm_contexto` | Busca en los tres segmentos de la memoria los fragmentos más parecidos al caso de uso, con cuotas por fuente | El caso de uso | Hasta 21 fragmentos de contexto |
| Agente generador | WF-2 | Claude Sonnet 5.5 | Genera al menos un caso de abuso por caso de uso, con el prompt público de 96 palabras | Caso de uso, contexto y, en un reintento, las observaciones del revisor | Casos de abuso en JSON |
| Agente revisor | WF-2 | Claude Sonnet 5.5 + validaciones deterministas | Aprueba o rechaza cada caso según los criterios R1 a R7 | Caso de uso y casos generados | Veredicto y observaciones por caso |
| Agente de mitigación | WF-2 | Claude Sonnet 5.5 | Propone controles preventivos, detectivos y correctivos con responsable, y estima probabilidad e impacto | Casos aprobados | Controles y riesgo por caso |
| Agente de abstracción | WF-3 | Claude Haiku 5.5 | Redacta el patrón abstracto y las palabras clave de cada caso aprobado | Casos aprobados por el analista | Patrón y palabras clave por caso |

## 3. Esquema de permisos

### 3.1 Actores

| Actor | Quién es | Cómo se autentica |
|---|---|---|
| Analista de seguridad | La persona que opera el sistema | Cuenta de propietario de n8n, local |
| n8n (los flujos) | El orquestador | Clave secreta de Supabase (`sb_secret_…`) y clave de la API de Claude, guardadas cifradas en sus credenciales |
| Agentes (Claude) | Los modelos de lenguaje | No se autentican contra nada: solo reciben texto de n8n |
| Ollama | El modelo de embeddings | Ninguna: no publica puertos y solo lo alcanza n8n por la red interna |
| `anon` y `authenticated` | Los roles públicos de la API de Supabase | Clave pública del proyecto |

### 3.2 Matriz de permisos sobre la memoria

**L** = lee, **E** = escribe, **—** = sin acceso.

| Recurso | WF-1 | WF-2 | WF-3 | Agentes | `anon` / `authenticated` |
|---|---|---|---|---|---|
| `ltm_negocio` (largo plazo) | E | L | — | — | — |
| `ltm_amenazas` (largo plazo) | E | L | — | — | — |
| `ltm_abusos` (largo plazo) | — | L | L y E | — | — |
| `ejecuciones` (corto plazo) | — | E | L | — | — |
| `ejecucion_pasos` (corto plazo) | — | E | E | — | — |
| Funciones de búsqueda (`match_ltm_*`, `ltm_contexto`) | — | Ejecuta | — | — | — |
| `ltm_borrar_fuente` | Ejecuta | — | — | — | — |
| API de Claude | — | Llama | Llama | — | — |

Reglas que se desprenden de la matriz:

- **La memoria de casos validados (`ltm_abusos`) solo crece con aprobación humana.** WF-3 es el único flujo que la escribe y siempre a partir de la selección del analista. WF-1 no puede tocarla: `ltm_borrar_fuente` solo acepta `ltm_negocio` y `ltm_amenazas`.
- **Los agentes no tienen acceso a nada.** Aunque un caso de uso de texto libre intentara inyectarles instrucciones, no tienen herramientas con las que actuar; además, su salida se valida contra un esquema antes de usarse.
- **Todo deja rastro.** Cada ejecución y cada paso (entrada, salida, modelo y tokens) quedan en la memoria de corto plazo, y cada caso consolidado guarda `aprobado_por` y el `run_id` de origen.

### 3.3 Cómo se aplica

| Control | Dónde | Efecto |
|---|---|---|
| RLS activado en las cinco tablas, sin políticas | [`sql/001_esquema.sql`](../sql/001_esquema.sql) | Los roles públicos de Supabase no ven ni escriben ninguna fila |
| Permisos solo para `service_role` y retirados a `public`, `anon` y `authenticated` | [`sql/001_esquema.sql`](../sql/001_esquema.sql), [`sql/004_permisos_service_role.sql`](../sql/004_permisos_service_role.sql), [`sql/005_capa_agentica.sql`](../sql/005_capa_agentica.sql) | Solo la clave secreta puede leer, escribir y ejecutar las funciones |
| Lista blanca en `ltm_borrar_fuente` | [`sql/001_esquema.sql`](../sql/001_esquema.sql) | La reingesta no puede borrar casos validados |
| Claves solo en las credenciales de n8n, cifradas con `N8N_ENCRYPTION_KEY` | [`infra/.env`](../infra/.env.example), fuera del repositorio | Las claves no aparecen en el repositorio, en los flujos exportados ni en capturas |
| n8n publicado solo en `127.0.0.1` y con cuenta de propietario | [`infra/docker-compose.yml`](../infra/docker-compose.yml) | Nadie desde la red puede ejecutar los flujos |
| Ollama sin puertos publicados | [`infra/docker-compose.yml`](../infra/docker-compose.yml) | Solo n8n genera embeddings |
| Nodos de archivos restringidos a `/files`, con `data/` de solo lectura | [`infra/docker-compose.yml`](../infra/docker-compose.yml) | WF-1 solo puede leer las fuentes del repositorio |
| Límite de gasto en la consola de Claude, máximo 5 casos de uso por ejecución y 2 reintentos | Consola de Claude y nodo Configuración | Un error o una entrada enorme no generan un gasto descontrolado |

### 3.4 Limitaciones y mejoras para producción

- **Una sola clave para los tres flujos.** Los tres usan la clave secreta de Supabase, que tiene todos los permisos de `service_role`. La separación de la matriz la garantiza el diseño de cada flujo, no la base de datos. En producción se crearía un rol de PostgreSQL por flujo (por ejemplo, uno de ingesta que solo escriba en `ltm_negocio` y `ltm_amenazas`, y uno de consolidación que sea el único con `insert` en `ltm_abusos`) y se conectaría cada flujo con su propio rol.
- **Un solo analista.** n8n tiene una cuenta de propietario. Con un equipo se usarían usuarios separados, de modo que quien genera casos de abuso y quien los aprueba en WF-3 puedan ser personas distintas.
- **Aprobación por nombre.** `aprobado_por` es un texto que escribe el analista. Con usuarios separados, se tomaría de la sesión de n8n en lugar de escribirse a mano.
