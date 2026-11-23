# Matriz de requisitos · Reto 2: Análisis de flujo

Cada requisito está tomado del documento original del challenge (sección "2. Reto Análisis de Flujo"). La columna **Entregable** indica dónde se cumple y **Estado** se actualiza al avanzar.

Estados: ⬜ pendiente · 🟨 en curso · ✅ completo. El extra (sección D) es opcional y no se realizó.

## Objetivo general

> Analizar el flujo de venta de productos voluminosos y definir casos de uso y abuso relevantes para la seguridad de la plataforma, **donde la utilización de una LLM es obligatoria para soportar el modelado**.

## A. Arquitectura con agentes de IA (obligatoria)

"Debe ser propuesta una arquitectura con agentes de IA que soporte el levantamiento de casos de abuso conforme el framework de modelado de amenazas STRIDE."

| ID | Requisito | Entregable | Estado |
|---|---|---|---|
| A1 | Componente de **Memoria**, describiendo la segmentación propuesta | Documento de arquitectura: [`docs/03-arquitectura.md`](docs/03-arquitectura.md) §4 | ✅ diseño |
| A2 | **Long-Term Memory obligatoria**, que el agente consulta para abstraer los casos de abuso | Supabase (pgvector) + documento de arquitectura: [`docs/03-arquitectura.md`](docs/03-arquitectura.md) §4.4–4.5 | ✅ 84 casos validados en `ltm_abusos`; 38 de 90 casos abstraídos desde la memoria ([`docs/07-ejecucion.md`](docs/07-ejecucion.md)) |
| A3 | Componente de **Fuentes de Datos** y su comunicación con el componente de Memoria | Flujo de ingesta en n8n + documento: [`docs/03-arquitectura.md`](docs/03-arquitectura.md) §3 | ✅ fuentes y WF-1 ejecutado ([`docs/05-memoria.md`](docs/05-memoria.md)) |
| A4 | **Agentic Layer**, describiendo los agentes que se utilizarán | Flujos de agentes en n8n + documento: [`docs/03-arquitectura.md`](docs/03-arquitectura.md) §5 | ✅ WF-2 ejecutado con Claude real ([`docs/07-ejecucion.md`](docs/07-ejecucion.md)) |
| A5 | **Implementación obligatoria** de la arquitectura (stack a elección; sugerido n8n + Supabase) | Flujos de n8n exportados, scripts de base de datos: infraestructura en [`docs/04-infraestructura.md`](docs/04-infraestructura.md) | ✅ WF-1, WF-2 y WF-3 implementados y ejecutados ([`docs/05-memoria.md`](docs/05-memoria.md), [`docs/06-agentes.md`](docs/06-agentes.md)) |
| A6 | **Pruebas de la ejecución** de la implementación | Capturas y salidas de ejecución | ✅ Capturas, resultados JSON y registros de Supabase de 5 ejecuciones ([`docs/07-ejecucion.md`](docs/07-ejecucion.md)) |
| A7 | El objetivo de la arquitectura es **soportar la proposición de casos de uso/abuso** durante el análisis del flujo | Trazabilidad entre salidas de los agentes e informe | ✅ 90 casos de abuso sobre los 16 casos de uso ([`docs/07-ejecucion.md`](docs/07-ejecucion.md)) |
## B. Prompts (para cualquier LLM pública)

| ID | Requisito | Entregable | Estado |
|---|---|---|---|
| B1 | **No más de 100 palabras** | Prompts con conteo de palabras verificado | ✅ 96 palabras ([`prompts/README.md`](prompts/README.md)) |
| B2 | Aceptar **uno o más casos de uso** | Prompts + prueba con varios casos | ✅ Ejecuciones con 1, 4 y 5 casos de uso |
| B3 | Generar **al menos un caso de abuso por cada caso de uso** | Validación en la salida | ✅ Ningún caso de uso sin caso de abuso (16 de 16) |
| B4a | La salida **referencia el caso de uso** vinculado | Formato de salida | ✅ 90 de 90 casos citan su caso de uso (R1) |
| B4b | La salida **explica claramente cómo sucede** el abuso | Formato de salida | ✅ De 4 a 7 pasos concretos por caso |
| B4c | La salida propone **vectores con contexto práctico**, no solo un CWE, CVE o riesgo genérico | Formato de salida + revisión | ✅ Acción, herramienta y dato manipulado en todos los casos |
## C. Análisis del flujo de negocio

| ID | Requisito | Entregable | Estado |
|---|---|---|---|
| C1 | **Diagrama** que modele el caso y las interacciones entre actores y sistemas | Diagrama de flujo de datos con límites de confianza: [`docs/02-diagrama.md`](docs/02-diagrama.md) | ✅ |
| C2 | **Informe de Threat Modelling** con amenazas según **STRIDE** | Informe STRIDE: [`docs/08-informe-stride.md`](docs/08-informe-stride.md) | ✅ 84 casos de abuso en alcance, matriz STRIDE por caso de uso y por límite de confianza |
| C2a | Vulnerabilidades en la lógica de los procesos / casos de abuso de **usuarios internos (empleados)** | [`docs/08-informe-stride.md`](docs/08-informe-stride.md) §4 | ✅ 34 casos de empleados propios y del proveedor logístico, por rol |
| C2b | Vulnerabilidades en la lógica de los procesos / casos de abuso de **usuarios externos (clientes)** | [`docs/08-informe-stride.md`](docs/08-informe-stride.md) §5 | ✅ 51 casos de clientes y atacantes externos |
| C2c | **Controles de seguridad y mejores prácticas** para mitigar los riesgos | [`docs/08-informe-stride.md`](docs/08-informe-stride.md) §6 y anexo A | ✅ Controles prioritarios por riesgo, buenas prácticas transversales y 397 controles por caso |
| C2d | **Principales riesgos** de seguridad asociados a los flujos | [`docs/08-informe-stride.md`](docs/08-informe-stride.md) §7 | ✅ 8 riesgos principales priorizados y mapa de calor |
| C3 | **Prompts** responsables de la creación de los casos de abuso, conforme a las restricciones | [`prompts/README.md`](prompts/README.md) | ✅ Prompt público de 96 palabras y prompts internos; probados en la Fase 7 |
| C4 | **Detallar claramente todos los supuestos** del modelo y del análisis de vulnerabilidades, riesgos y mitigantes | [`docs/01-casos-de-uso-y-supuestos.md`](docs/01-casos-de-uso-y-supuestos.md) §6, [`docs/03-arquitectura.md`](docs/03-arquitectura.md) §10, [`docs/08-informe-stride.md`](docs/08-informe-stride.md) §9 y anexo B | ✅ S-01 a S-35, supuestos del análisis de riesgos y supuestos derivados por caso |
## D. Extra

"Escoger una de las mitigaciones propuestas y crear una solución con el uso de agentes de IA que garantice la efectiva mitigación (stack a elección)."

| ID | Requisito | Entregable | Estado |
|---|---|---|---|
| D1 | Diseño de arquitectura con **Componente de Memoria** y su segmentación | Documento del extra | No realizado (opcional) |
| D2 | **Componente de Fuentes de Datos** y su comunicación con la Memoria | Documento del extra | No realizado (opcional) |
| D3 | **Agentic Layer** con los agentes utilizados | Documento del extra | No realizado (opcional) |
| D4 | **Prompts de cada agente** (sin límite de tamaño) | Documento del extra | No realizado (opcional) |

## Contexto del caso que debe respetarse

**Flujo:** búsqueda y selección del producto voluminoso → carrito → pago con datos de envío y contacto → elección de envío (entrega a domicilio o recolección en tienda) → registro de la orden → preparación y empaquetado en almacén → recolección por el proveedor logístico → tránsito por centros de distribución y puntos de control → llegada a la dirección → recepción por el cliente → posible cancelación después de recibir, desde la misma aplicación.

**Reglas de negocio:**

1. Cada cliente debe tener un **único registro** en la plataforma.
2. El **costo de envío se calcula según el perfil** del usuario.
3. El entregador debe **estar en la localización de entrega** cuando registra la entrega (entregas a domicilio).
4. El usuario puede utilizar **cupones de descuento**.

**Contexto adicional:** existe una integración con la empresa que realiza la logística entre los centros de distribución y la entrega al cliente.

**Componentes del diagrama:** Marketplace, `clients-admin-front`, `clients-api`, `cupons-frontend`, `cupons-api`, `delivery-api`, `delivery-admin-front`, `logistic` (empresa de logística) y la red de logística.
