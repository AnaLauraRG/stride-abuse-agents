# Fase 7 · Ejecución con Claude real y evidencias

Esta fase ejecuta la arquitectura implementada (WF-2 y WF-3) con la API real de Claude sobre los 16 casos de uso y reúne la **evidencia de ejecución** que pide el reto (requisito **A6**). También es la prueba real de los prompts (**B1 a B4c**) y de la memoria de largo plazo (**A2**).

## 1. Ejecuciones

| Ejecución | `run_id` | Casos de uso | Casos de abuso aprobados | Usan patrones AV | Aprobados tras corrección | Tokens (entrada / salida) | Costo estimado* |
|---|---|---|---|---|---|---|---|
| Prueba inicial | `6c18dfda…` | UC-11 | 4 | 0 (memoria vacía) | 2 | 35 732 / 19 587 | 0.27 USD |
| Prueba de memoria | `a084c505…` | UC-12 | 6 | 1 | 2 | 45 048 / 16 921 | 0.26 USD |
| Lote 1 | `bc4a02d5…` | UC-01 a UC-05 | 28 | 8 | 7 | 230 163 / 80 905 | 1.27 USD |
| Lote 2 | `985f00fa…` | UC-06 a UC-10 | 27 | 15 | 6 | 250 064 / 82 708 | 1.33 USD |
| Lote 3 | `f1e3ff28…` | UC-13 a UC-16 | 25 | 14 | 6 | 228 008 / 81 315 | 1.27 USD |
| **Total** | | **16** | **90** | **38** | **23** | | **≈ 4.4 USD** |

\* Calculado con el precio publicado de Claude Sonnet 5.5 (2 USD por millón de tokens de entrada y 10 USD por millón de salida). No incluye las dos ejecuciones que fallaron (sección 4) ni las consolidaciones con Haiku. El costo real está en la consola de Claude (*Usage*).

En las 5 ejecuciones exitosas: **0 casos descartados** y **ningún caso de uso sin caso de abuso**. Cada lote de 5 casos de uso tardó entre 10 y 11 minutos.

### Consolidaciones (WF-3)

| Origen | Consolidados | IDs | Excluidos por el analista |
|---|---|---|---|
| UC-11 | 4 | AV-0001 a AV-0004 | — |
| UC-12 | 6 | AV-0005 a AV-0010 | — |
| Lote 1 | 25 | AV-0011 a AV-0035 | AC-UC03-04, AC-UC05-07, AC-UC05-08 |
| Lote 2 | 26 | AV-0036 a AV-0061 | AC-UC10-06 |
| Lote 3 | 23 | AV-0062 a AV-0084 | AC-UC14-07, AC-UC16-07 |
| **Total** | **84** | **AV-0001 a AV-0084** | **6** |

Los 6 casos excluidos estaban bien redactados y pasaron el revisor, pero quedan **fuera del alcance declarado**:
- **S-22** (denegación de servicio volumétrica): AC-UC03-04, AC-UC05-07, AC-UC10-06, AC-UC14-07 y AC-UC16-07.
- **S-24** (interceptación en la red interna): AC-UC05-08.

Las denegaciones que abusan de la lógica del negocio sí se consolidaron. Por ejemplo, acaparar inventario (AC-UC02-02), ventanas de entrega (AC-UC06-04) o paquetes (AC-UC09-06). Es la revisión humana del diseño (supuesto S-30): el revisor automático evalúa la calidad del caso, y el analista decide qué entra a la memoria.

## 2. Cobertura por caso de uso

| Caso de uso | Casos de abuso | Categorías STRIDE | Actores | Fuera de alcance |
|---|---|---|---|---|
| UC-01 Registro y cuenta | 6 | S, I, E | 6 externos | — |
| UC-02 Producto y carrito | 3 | T, I, D | 3 externos | — |
| UC-03 Datos de envío y contacto | 6 | S, T, R, I, D, E | 6 externos | 1 |
| UC-04 Cupón | 5 | S, T, I, E | 4 externos, 1 interno | — |
| UC-05 Costo de envío | 8 | S, T, D, E | 6 externos, 2 internos | 2 |
| UC-06 Modalidad de entrega | 4 | T, D, E | 4 externos | — |
| UC-07 Pago y orden | 7 | S, T, R, I, E | 6 externos, 1 interno | — |
| UC-08 Preparación en almacén | 3 | T, E | 3 internos | — |
| UC-09 Transporte logístico | 6 | S, T, R, I, D | 5 internos de tercero, 1 externo | — |
| UC-10 Estados por integración | 7 | S, T, R, D, E | 5 externos, 2 internos de tercero | 1 |
| UC-11 Entrega con geolocalización | 4 | S, T, R | 2 externos, 2 internos de tercero | — |
| UC-12 Recolección en tienda | 6 | S, T, R, I, D | 5 externos, 1 interno | — |
| UC-13 Cancelación y devolución | 6 | T, R, E | 4 externos, 1 interno, 1 interno de tercero | — |
| UC-14 Backoffice de clientes | 7 | S, T, R, I, D, E | 6 internos, 1 externo | 1 |
| UC-15 Backoffice de cupones | 5 | S, R, I, D, E | 3 internos, 1 externo, 1 interno de tercero | — |
| UC-16 Backoffice de entregas | 7 | S, T, I, D, E | 6 internos, 1 externo | 1 |
| **Total** | **90** | T 28 · S 15 · E 15 · R 11 · I 11 · D 10 | 55 externos · 24 internos · 11 internos de tercero | **6** |

## 3. Qué demuestra cada requisito

| Requisito | Evidencia |
|---|---|
| **A6** Pruebas de la ejecución | Capturas de cada ejecución en n8n con todos los nodos en verde; resultados completos en JSON; filas en `ejecuciones` y `ejecucion_pasos` de Supabase |
| **A2** Memoria de largo plazo para abstraer casos de abuso | 38 de 90 casos citan patrones `AV-…` de ejecuciones anteriores, y la proporción crece lote a lote (0 → 1 de 6 → 8 de 28 → 15 de 27 → 14 de 25). Ver los ejemplos abajo |
| **B2, B3** Uno o más casos de uso, al menos un caso de abuso por cada uno | Ejecuciones con 1, 4 y 5 casos de uso; ninguno quedó sin casos de abuso |
| **B4a** Referencia al caso de uso | 90 de 90 casos citan el caso de uso correcto (criterio R1, comprobado por código) |
| **B4b** Cómo sucede | Todos traen de 4 a 7 pasos concretos sobre componentes, flujos (F1–F30) y reglas (RN-1 a RN-4) |
| **B4c** Vectores prácticos | Todos describen acción, herramienta y dato manipulado. Ninguno se queda en un CWE, CVE o riesgo genérico, y ninguno trae comandos ni código |

### Ejemplos de abstracción desde la memoria

- **AC-UC12-04** (el cliente niega haber retirado en tienda) cita **AV-0004** ("una prueba que acredita la presencia de una parte no acredita que otra parte haya recibido") y explica la diferencia: "en la entrega a domicilio la app al menos adjunta GPS y marca de tiempo; en la recolección en tienda no hay ni geolocalización ni foto".
- **AC-UC10-02** (un empleado del proveedor fabrica eventos de entrega) cita **AV-0006** (personal de tienda que marca "entregado" sin entregar) y **AV-0001** (GPS simulado), y se distingue de ambos por el actor y por el canal.
- **AV-0003** (datos alterados en tránsito, abstraído de UC-11) se aplicó al perfil, a la cotización y a la tarifa en UC-01, UC-03 y UC-05.
- **AV-0032** (manipulación de la tarifa, de UC-05) se aplicó a la modalidad de entrega y al pago en UC-06 y UC-07.

### El revisor sí filtra

23 de los 90 casos se aprobaron **después de una corrección**, y 3 necesitaron los 3 intentos permitidos. Las observaciones del revisor quedan en `ejecucion_pasos`. Por ejemplo, pidió precondiciones más precisas, que se diferenciara un caso de otro ya validado, o que el vector dijera qué dato se manipula.

## 4. Incidencias durante la ejecución

| Incidencia | Causa | Solución |
|---|---|---|
| `tool_choice: type "tool" and "any" are not supported for this model` | Sonnet 5.5 no admite forzar una herramienta | Salidas estructuradas (`output_config.format`) con los esquemas ajustados a sus restricciones ([`06-agentes.md`](06-agentes.md) §1) |
| `refusal` del revisor en UC-03 (primer intento del lote 1) | Un filtro de seguridad de la API rechazó una respuesta con un vector demasiado detallado | Vectores descritos a nivel de acción, herramienta y dato, sin comandos ni código; un `refusal` ya no detiene el lote. La ejecución cortada se marcó `fallida` y el lote se repitió completo |
| `max_tokens` en WF-3 al consolidar 25 casos | Límite de 4 000 tokens de salida del agente de abstracción | Límite de 16 000. No se guardó nada a medias: la validación detuvo el flujo antes de insertar |
| Error de DNS al guardar pasos (lote 2) | Fallo momentáneo de red de la VM tras un reinicio | Reintentos automáticos (3 intentos, 5 s) en todas las llamadas a Supabase y Ollama. La ejecución cortada se marcó `fallida` y el lote se repitió |
| Entrada vacía en WF-2 y WF-3 | El valor se escribió en la caja del nombre del campo | Se corrigió en la interfaz; la validación de WF-2 ahora acepta más formatos y muestra el valor recibido |

## 5. Observaciones para el informe

- **Sesgo del prompt de abstracción:** el patrón AV-0001 es casi igual al ejemplo del prompt de abstracción. Es una abstracción correcta, pero el ejemplo influyó en el texto. En una versión siguiente convendría quitar el ejemplo del prompt o usar uno de otro dominio.
- **Un solo actor por caso:** el esquema admite un actor. En las colusiones (AC-UC11-03) se registró solo uno; el informe los presenta como actores combinados.
- **Referencias y responsables:** hay algunos detalles menores, como OAT-012 donde OAT-021 sería más preciso, o un control asignado a la pasarela cuando corresponde a soporte. Se corrigen en el informe, no en los resultados guardados.
- **Supuestos del modelo:** los agentes declararon supuestos propios (criterio R6), como "no hay detección de ubicación simulada" o la existencia de una agencia externa con acceso al backoffice. El informe los agrupa como supuestos derivados.
- **Casos parecidos entre casos de uso:** algunos casos se repiten entre casos de uso del mismo lote, como la lectura de datos ajenos cambiando el identificador (AC-UC01-06, AC-UC03-02, AC-UC07-06). Pasa porque la memoria solo los conoce después de consolidar el lote. El informe los agrupa.

## 6. Archivos de evidencia

En [`evidencias/fase7/`](evidencias/fase7):

| Archivo | Contenido |
|---|---|
| `01-wf2-uc11-ejecucion.png` | WF-2 con UC-11 |
| `02-resultado-uc11.json` | Resultado completo de UC-11 |
| `03-wf3-consolidacion-uc11.png` | WF-3 con UC-11 |
| `04-ltm-abusos-patrones.png` | Patrones abstractos AV-0001 a AV-0004 |
| `05-resultado-uc12.json` | Resultado de UC-12 (usa AV-0004 y AV-0002) |
| `06-wf2-lote1-ejecucion.png`, `07-resultado-lote1-uc01-uc05.json` | Lote 1 |
| `08-wf2-lote2-ejecucion.png`, `09-resultado-lote2-uc06-uc10.json` | Lote 2 |
| `10-wf2-lote3-ejecucion.png`, `11-resultado-lote3-uc13-uc16.json` | Lote 3 |
| `12-wf3-consolidacion-lote3.png` | WF-3 con el lote 3 (AV-0062 en adelante) |

Además, en [`evidencias/fase6/`](evidencias/fase6): la recuperación con cuotas (`ltm_contexto`) para UC-11 con datos reales.
