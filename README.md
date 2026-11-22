# STRIDE Abuse Agents

Reto 2 del Challenge Cybersecurity Engineer (BISO): análisis de seguridad del flujo de venta de productos voluminosos en un ecommerce, con una arquitectura de agentes de IA que soporta la generación de casos de abuso según el modelo STRIDE.

> Estado: Fases 1 a 8 completas: arquitectura implementada y ejecutada con Claude sobre los 16 casos de uso, e informe STRIDE con 84 casos de abuso. Sigue la entrega final.

## Stack

| Pieza | Herramienta |
|---|---|
| Flujos y agentes | n8n |
| LLM de los agentes | Claude Sonnet 5.5 y Haiku 5.5 (API de Anthropic) |
| Embeddings | Ollama con bge-m3 (modelo local, multilingüe) |
| Memoria de largo plazo | Supabase con pgvector |

## Contenido

| Archivo | Descripción |
|---|---|
| [`REQUISITOS.md`](REQUISITOS.md) | Matriz con cada requisito del reto, su entregable y su estado |
| [`docs/01-casos-de-uso-y-supuestos.md`](docs/01-casos-de-uso-y-supuestos.md) | Actores, componentes, límites de confianza, 16 casos de uso y 27 supuestos |
| [`docs/02-diagrama.md`](docs/02-diagrama.md) | Diagrama de flujo de datos en tres vistas, zonas, límites de confianza y catálogo de flujos F1–F30 |
| [`docs/03-arquitectura.md`](docs/03-arquitectura.md) | Arquitectura de agentes: fuentes de datos, memoria segmentada, capa agéntica, contratos, seguridad y costos |
| [`docs/04-infraestructura.md`](docs/04-infraestructura.md) | Instalación de n8n, Ollama y Supabase, credenciales y evidencias |
| [`docs/05-memoria.md`](docs/05-memoria.md) | Fuentes de datos, fragmentos y flujo WF-1 de carga de la memoria de largo plazo |
| [`docs/06-agentes.md`](docs/06-agentes.md) | Capa agéntica: WF-2 (generación, revisión, mitigación) y WF-3 (consolidación en `ltm_abusos`) |
| [`docs/07-ejecucion.md`](docs/07-ejecucion.md) | Ejecución con Claude real: resultados, uso de la memoria, incidencias y evidencias |
| [`docs/08-informe-stride.md`](docs/08-informe-stride.md) | **Informe STRIDE**: abusos de internos y externos, controles, riesgos principales, supuestos y detalle de los 84 casos |
| [`data/casos_de_abuso.json`](data/casos_de_abuso.json) | Catálogo de los 90 casos generados (84 consolidados como AV-0001 a AV-0084, 6 fuera de alcance) |
| [`n8n/`](n8n) | Flujos de n8n exportados: WF-1 ingesta, WF-2 generación, WF-3 consolidación |
| [`prompts/`](prompts) | Prompt público de ≤100 palabras, prompts internos y esquemas de salida |
| [`scripts/`](scripts) | Generación de las fuentes del negocio y de los fragmentos de memoria |
| [`infra/`](infra) | Compose de n8n y Ollama (`.env.example` como plantilla) |
| [`sql/`](sql) | Esquema de la memoria en Supabase y consultas de verificación |
| [`diagrams/`](diagrams) | Fuentes Graphviz (`.dot`) de los diagramas y sus exportaciones SVG y PNG |
| [`data/casos_de_uso.json`](data/casos_de_uso.json) | Casos de uso en formato estructurado, entrada de los agentes |

## Fases

| Fase | Entregable | Estado |
|---|---|---|
| 1 | Casos de uso y supuestos | ✅ |
| 2 | Diagrama del flujo con límites de confianza | ✅ |
| 3 | Diseño de la arquitectura de agentes | ✅ |
| 4 | Infraestructura: n8n, Supabase, Ollama, API de Claude | ✅ |
| 5 | Carga de la memoria de largo plazo | ✅ |
| 6 | Agentes y prompts | ✅ |
| 7 | Ejecución y evidencias | ✅ |
| 8 | Informe de threat modeling STRIDE | ✅ |
| 9 | Extra: mitigación con agentes | ⬜ |
| 10 | Documentación y entrega | ⬜ |
