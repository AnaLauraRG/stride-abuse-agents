# Matriz de requisitos · Reto 2: Análisis de flujo

Cada requisito está tomado del documento original del challenge (sección "2. Reto Análisis de Flujo"). La columna **Entregable** indica dónde se cumple y **Estado** se actualiza al avanzar.

Estados: ⬜ pendiente · 🟨 en curso · ✅ completo

## Objetivo general

> Analizar el flujo de venta de productos voluminosos y definir casos de uso y abuso relevantes para la seguridad de la plataforma, **donde la utilización de una LLM es obligatoria para soportar el modelado**.

## A. Arquitectura con agentes de IA (obligatoria)

"Debe ser propuesta una arquitectura con agentes de IA que soporte el levantamiento de casos de abuso conforme el framework de modelado de amenazas STRIDE."

| ID | Requisito | Entregable | Estado |
|---|---|---|---|
| A1 | Componente de **Memoria**, describiendo la segmentación propuesta | Documento de arquitectura | ⬜ |
| A2 | **Long-Term Memory obligatoria**, que el agente consulta para abstraer los casos de abuso | Supabase (pgvector) + documento de arquitectura | ⬜ |
| A3 | Componente de **Fuentes de Datos** y su comunicación con el componente de Memoria | Flujo de ingesta en n8n + documento | ⬜ |
| A4 | **Agentic Layer**, describiendo los agentes que se utilizarán | Flujos de agentes en n8n + documento | ⬜ |
| A5 | **Implementación obligatoria** de la arquitectura (stack a elección; sugerido n8n + Supabase) | Flujos de n8n exportados, scripts de base de datos | ⬜ |
| A6 | **Pruebas de la ejecución** de la implementación | Capturas y salidas de ejecución | ⬜ |
| A7 | El objetivo de la arquitectura es **soportar la proposición de casos de uso/abuso** durante el análisis del flujo | Trazabilidad entre salidas de los agentes e informe | ⬜ |

## B. Prompts (para cualquier LLM pública)

| ID | Requisito | Entregable | Estado |
|---|---|---|---|
| B1 | **No más de 100 palabras** | Prompts con conteo de palabras verificado | ⬜ |
| B2 | Aceptar **uno o más casos de uso** | Prompts + prueba con varios casos | ⬜ |
| B3 | Generar **al menos un caso de abuso por cada caso de uso** | Validación en la salida | ⬜ |
| B4a | La salida **referencia el caso de uso** vinculado | Formato de salida | ⬜ |
| B4b | La salida **explica claramente cómo sucede** el abuso | Formato de salida | ⬜ |
| B4c | La salida propone **vectores con contexto práctico**, no solo un CWE, CVE o riesgo genérico | Formato de salida + revisión | ⬜ |

## C. Análisis del flujo de negocio

| ID | Requisito | Entregable | Estado |
|---|---|---|---|
| C1 | **Diagrama** que modele el caso y las interacciones entre actores y sistemas | Diagrama de flujo de datos con límites de confianza | ⬜ |
| C2 | **Informe de Threat Modelling** con amenazas según **STRIDE** | Informe | ⬜ |
| C2a | Vulnerabilidades en la lógica de los procesos / casos de abuso de **usuarios internos (empleados)** | Informe | ⬜ |
| C2b | Vulnerabilidades en la lógica de los procesos / casos de abuso de **usuarios externos (clientes)** | Informe | ⬜ |
| C2c | **Controles de seguridad y mejores prácticas** para mitigar los riesgos | Informe | ⬜ |
| C2d | **Principales riesgos** de seguridad asociados a los flujos | Informe | ⬜ |
| C3 | **Prompts** responsables de la creación de los casos de abuso, conforme a las restricciones | Ver sección B | ⬜ |
| C4 | **Detallar claramente todos los supuestos** del modelo y del análisis de vulnerabilidades, riesgos y mitigantes | [`docs/01-casos-de-uso-y-supuestos.md`](docs/01-casos-de-uso-y-supuestos.md) (se amplía en cada fase) | 🟨 |

## D. Extra

"Escoger una de las mitigaciones propuestas y crear una solución con el uso de agentes de IA que garantice la efectiva mitigación (stack a elección)."

| ID | Requisito | Entregable | Estado |
|---|---|---|---|
| D1 | Diseño de arquitectura con **Componente de Memoria** y su segmentación | Documento del extra | ⬜ |
| D2 | **Componente de Fuentes de Datos** y su comunicación con la Memoria | Documento del extra | ⬜ |
| D3 | **Agentic Layer** con los agentes utilizados | Documento del extra | ⬜ |
| D4 | **Prompts de cada agente** (sin límite de tamaño) | Documento del extra | ⬜ |

## Contexto del caso que debe respetarse

**Flujo:** búsqueda y selección del producto voluminoso → carrito → pago con datos de envío y contacto → elección de envío (entrega a domicilio o recolección en tienda) → registro de la orden → preparación y empaquetado en almacén → recolección por el proveedor logístico → tránsito por centros de distribución y puntos de control → llegada a la dirección → recepción por el cliente → posible cancelación después de recibir, desde la misma aplicación.

**Reglas de negocio:**

1. Cada cliente debe tener un **único registro** en la plataforma.
2. El **costo de envío se calcula según el perfil** del usuario.
3. El entregador debe **estar en la localización de entrega** cuando registra la entrega (entregas a domicilio).
4. El usuario puede utilizar **cupones de descuento**.

**Contexto adicional:** existe una integración con la empresa que realiza la logística entre los centros de distribución y la entrega al cliente.

**Componentes del diagrama:** Marketplace, `clients-admin-front`, `clients-api`, `cupons-frontend`, `cupons-api`, `delivery-api`, `delivery-admin-front`, `logistic` (empresa de logística) y la red de logística.
