# STRIDE Abuse Agents

Reto 2 del Challenge Cybersecurity Engineer (BISO): análisis de seguridad del flujo de venta de productos voluminosos en un ecommerce, con una arquitectura de agentes de IA que soporta la generación de casos de abuso según el modelo STRIDE.

> Estado: Fase 1 completa (casos de uso y supuestos). El resto de las fases está en curso.

## Stack

| Pieza | Herramienta |
|---|---|
| Flujos y agentes | n8n |
| LLM de los agentes | Claude (API de Anthropic) |
| Embeddings | Ollama (modelo local) |
| Memoria de largo plazo | Supabase con pgvector |

## Contenido

| Archivo | Descripción |
|---|---|
| [`REQUISITOS.md`](REQUISITOS.md) | Matriz con cada requisito del reto, su entregable y su estado |
| [`docs/01-casos-de-uso-y-supuestos.md`](docs/01-casos-de-uso-y-supuestos.md) | Actores, componentes, límites de confianza, 16 casos de uso y 25 supuestos |
| [`data/casos_de_uso.json`](data/casos_de_uso.json) | Casos de uso en formato estructurado, entrada de los agentes |

## Fases

| Fase | Entregable | Estado |
|---|---|---|
| 1 | Casos de uso y supuestos | ✅ |
| 2 | Diagrama del flujo con límites de confianza | ⬜ |
| 3 | Diseño de la arquitectura de agentes | ⬜ |
| 4 | Infraestructura: n8n, Supabase, Ollama, API de Claude | ⬜ |
| 5 | Carga de la memoria de largo plazo | ⬜ |
| 6 | Agentes y prompts | ⬜ |
| 7 | Ejecución y evidencias | ⬜ |
| 8 | Informe de threat modeling STRIDE | ⬜ |
| 9 | Extra: mitigación con agentes | ⬜ |
| 10 | Documentación y entrega | ⬜ |
