# Fase 8 · Informe de modelado de amenazas STRIDE

Informe de los requisitos **C2** (modelado de amenazas con STRIDE), **C2a** (abusos de usuarios internos), **C2b** (abusos de usuarios externos), **C2c** (controles y buenas prácticas) y **C2d** (principales riesgos). Se genera con `scripts/generar_informe.py` a partir de [`../data/casos_de_abuso.json`](../data/casos_de_abuso.json), el catálogo de los casos de abuso producidos y consolidados en la Fase 7.

**Contenido:** 1 Resumen · 2 Alcance y método · 3 Matriz STRIDE · 4 Abusos de usuarios internos · 5 Abusos de usuarios externos · 6 Controles · 7 Principales riesgos · 8 Fuera de alcance · 9 Supuestos · 10 Limitaciones · Anexo A Detalle de los casos · Anexo B Supuestos derivados

## 1. Resumen ejecutivo

Se modeló con STRIDE el flujo de venta de productos voluminosos (16 casos de uso, 30 flujos de datos y 6 límites de confianza) y se obtuvieron **84 casos de abuso** dentro del alcance, más 6 fuera de alcance que se documentan aparte. Los casos los generó la capa de agentes (Claude con memoria de largo plazo), los revisó un agente revisor y los aprobó un analista.

| | |
|---|---|
| Casos de abuso en alcance | **84**, en los 16 casos de uso |
| Por categoría STRIDE | S 14 · T 28 · R 11 · I 11 · D 5 · E 15 |
| Por actor | 51 de actores externos · 34 de empleados (propios o del proveedor logístico); la colusión AC-UC11-03 cuenta en ambos |
| Riesgo alto | 48 casos |
| Controles propuestos | 397 (preventivos, detectivos y correctivos) |

**Hallazgo central.** La mayoría de los abusos no necesita una vulnerabilidad técnica clásica: explotan que el sistema **confía en datos que controla quien se beneficia**: el precio y el envío que manda el cliente, el GPS del repartidor, el estado que marca un operador, el evento que envía el proveedor con una credencial compartida. Los riesgos principales son:

1. **R3 · Privilegios internos sin segregación ni trazabilidad** (18 casos, 9 de riesgo alto)
2. **R1 · Evidencia y registros que no prueban lo que ocurrió** (14 casos, 9 de riesgo alto)
3. **R7 · Exposición de datos personales y de negocio** (12 casos, 9 de riesgo alto)
4. **R2 · Montos y beneficios calculados con datos que controla el cliente** (14 casos, 6 de riesgo alto)

**Primeras medidas recomendadas:** recalcular y firmar en el servidor todo valor monetario; exigir una prueba que no controle quien se beneficia (código del cliente, escaneo conjunto, segunda aprobación) para cerrar entregas, retiros, inspecciones y cambios manuales; individualizar y firmar la integración logística; y aplicar autorización por objeto y por función en cada API interna.

## 2. Alcance y método

**Alcance.** Lógica de negocio e integraciones del flujo descrito en [`01-casos-de-uso-y-supuestos.md`](01-casos-de-uso-y-supuestos.md), sobre el diagrama de [`02-diagrama.md`](02-diagrama.md). Fuera de alcance (S-22): denegación de servicio volumétrica, infraestructura de nube y seguridad física, salvo cuando afectan la lógica del flujo. Las APIs internas no están expuestas a internet (S-24).

**Método.**
1. **STRIDE por elemento del DFD.** Entidades externas: S, R. Procesos: S, T, R, I, D, E. Almacenes de datos: T, R, I, D. Flujos: T, I, D. La búsqueda se concentró en los flujos que cruzan un límite de confianza (LC-1 a LC-6) y tocan una regla de negocio (RN-1 a RN-4).
2. **Generación asistida por LLM** (requisito del reto). WF-2 ([`06-agentes.md`](06-agentes.md)) recupera para cada caso de uso el contexto de la memoria de largo plazo (negocio, CAPEC, OWASP, patrones de fraude y casos ya validados), y el agente generador propone casos de abuso con el prompt público de 96 palabras ([`../prompts/README.md`](../prompts/README.md)).
3. **Revisión en dos niveles.** El agente revisor exige pasos concretos, vector práctico, categoría STRIDE correcta, coherencia con los supuestos y que no se repitan casos validados; los rechazados vuelven al generador con observaciones. Después, el analista decide qué se consolida ([`07-ejecucion.md`](07-ejecucion.md)).
4. **Riesgo.** Probabilidad e impacto de 1 a 3 estimados por el agente de mitigación; nivel = producto (1–2 bajo, 3–4 medio, 6–9 alto). Los temas de riesgo de la sección 7 son la agrupación del analista.

**Ajustes del analista** sobre la salida de los agentes:

- **AC-UC11-01:** Responsable: la atestación del dispositivo se implementa en la app del repartidor, que es del proveedor logístico.
- **AC-UC11-03:** Actor combinado: el esquema admite un solo actor; se agrega el repartidor (interno de tercero) como participante.
- **AC-UC12-06:** Referencia: OWASP OAT-012 (Cashing Out) se sustituye por OAT-021 (Denial of Inventory), que describe el abuso.
- **AC-UC12-04:** Responsable: la revisión del reclamo la hace soporte del ecommerce, no la pasarela.

## 3. Matriz STRIDE

Número de casos de abuso por caso de uso y categoría principal. Cada caso aparece una vez, en su categoría principal; las secundarias están en el anexo A.

| Caso de uso | S | T | R | I | D | E | Total | Internos | Externos |
|---|---|---|---|---|---|---|---|---|---|
| UC-01 Registro y gestión de la cuenta del cliente | 3 | · | · | 2 | · | 1 | **6** | 0 | 6 |
| UC-02 Selección del producto y carrito | · | 1 | · | 1 | 1 | · | **3** | 0 | 3 |
| UC-03 Captura de datos de envío y contacto | 1 | 1 | 1 | 1 | · | 1 | **5** | 0 | 5 |
| UC-04 Aplicación de cupón de descuento | 1 | 2 | · | 1 | · | 1 | **5** | 1 | 4 |
| UC-05 Cálculo del costo de envío según el perfil | · | 3 | · | · | · | 3 | **6** | 2 | 4 |
| UC-06 Elección de la modalidad de entrega | · | 2 | · | · | 1 | 1 | **4** | 0 | 4 |
| UC-07 Pago y registro de la orden | 1 | 3 | 1 | 1 | · | 1 | **7** | 1 | 6 |
| UC-08 Preparación y empaquetado en almacén | · | 2 | · | · | · | 1 | **3** | 3 | 0 |
| UC-09 Recolección y transporte por el proveedor logístico | 1 | 2 | 1 | 1 | 1 | · | **6** | 5 | 1 |
| UC-10 Actualización de estados por la integración logística | 1 | 3 | 1 | · | · | 1 | **6** | 2 | 4 |
| UC-11 Registro de entrega a domicilio con geolocalización | 1 | 1 | 2 | · | · | · | **4** | 3 | 2 |
| UC-12 Recolección en tienda | 2 | 1 | 1 | 1 | 1 | · | **6** | 1 | 5 |
| UC-13 Cancelación posterior a la recepción y devolución | · | 2 | 2 | · | · | 2 | **6** | 2 | 4 |
| UC-14 Administración interna de clientes y perfiles | 1 | 2 | 1 | 1 | · | 1 | **6** | 5 | 1 |
| UC-15 Administración interna de cupones | 1 | · | 1 | 1 | 1 | 1 | **5** | 4 | 1 |
| UC-16 Administración interna de órdenes de entrega | 1 | 3 | · | 1 | · | 1 | **6** | 5 | 1 |
| **Total** | **14** | **28** | **11** | **11** | **5** | **15** | **84** | **34** | **51** |

El caso AC-UC11-03 (colusión cliente–repartidor) cuenta en las dos columnas de actores.

**Por límite de confianza** (un caso puede cruzar varios):

| Límite | Casos | Descripción |
|---|---|---|
| LC-1 | 41 | Internet ↔ Marketplace: el cliente (no confiable) interactúa con la plataforma. |
| LC-2 | 28 | Marketplace ↔ APIs internas (clients-api, cupons-api, delivery-api). |
| LC-3 | 18 | Empleados ↔ frontends administrativos internos ↔ APIs internas. |
| LC-4 | 20 | Empresa de logística (tercero) ↔ delivery-api, mediante la integración logistic. |
| LC-5 | 22 | Mundo físico ↔ sistemas: dispositivo del repartidor, escaneos en almacén y centros de distribución, entrega y recolección física. |
| LC-6 | 10 | Plataforma ↔ pasarela de pago externa. |

## 4. Abusos de usuarios internos (empleados)

Abusos cometidos por **empleados del ecommerce** (backoffice, almacén, tienda) y por **personal del proveedor logístico** (repartidores, centros de distribución), que en el modelo son internos de un tercero (S-15). En la mayoría el empleado usa permisos legítimos: el problema es que el proceso no limita, no exige una segunda persona o no deja rastro.

### Operador de atención a clientes (6 casos, 3 de riesgo alto)

| Caso | Caso de uso | STRIDE | Abuso | Riesgo | Tema |
|---|---|---|---|---|---|
| [AV-0031](#av-0031) | UC-05 | E (T, R) | Operador de atención cambia atributos de perfil de conocidos para darles envío reducido | medio (2×2) | R3 |
| [AV-0068](#av-0068) | UC-14 | I (R) | Consulta masiva de datos personales de clientes sin caso de soporte para vender o usar la información | alto (2×3) | R7 |
| [AV-0069](#av-0069) | UC-14 | T (S, E) | Operador reemplaza correo o teléfono de un cliente para tomar o vender su cuenta | alto (2×3) | R3 |
| [AV-0070](#av-0070) | UC-14 | R (T) | Cambios de perfil sin autoría fiable por cuenta compartida o historial modificable | medio (2×2) | R3 |
| [AV-0071](#av-0071) | UC-14 | E (T) | Operador envía directamente a clients-api campos que el front no expone para ampliar sus privilegios o los de terceros | alto (2×3) | R3 |
| [AV-0072](#av-0072) | UC-14 | T (E) | Edición de identificadores del perfil para duplicar o fusionar registros y eludir la unicidad del cliente | medio (2×2) | R3 |

### Operador de marketing y promociones (5 casos, 2 de riesgo alto)

| Caso | Caso de uso | STRIDE | Abuso | Riesgo | Tema |
|---|---|---|---|---|---|
| [AV-0029](#av-0029) | UC-04 | E (T, R) | Cupón sin límite creado en UC-15 por un operador interno y canjeado en el checkout de UC-04 por cuentas allegadas | alto (2×3) | R3 |
| [AV-0035](#av-0035) | UC-05 | E (T, R) | Cupón de envío con descuento excesivo o sin límite creado por un operador de marketing | medio (1×3) | R3 |
| [AV-0076](#av-0076) | UC-15 | R (T) | Operador modifica un cupón activo y borra la evidencia de su cambio para negar la autoría | medio (2×2) | R3 |
| [AV-0077](#av-0077) | UC-15 | D (T) | Operador descontento desactiva o altera masivamente cupones de una campaña vigente | bajo (1×2) | R3 |
| [AV-0078](#av-0078) | UC-15 | E (T, R) | Operador de marketing excede los topes de su rol al enviar por F28 una definición de cupón que cupons-api no autoriza | alto (2×3) | R3 |

### Operador de entregas (5 casos, 4 de riesgo alto)

| Caso | Caso de uso | STRIDE | Abuso | Riesgo | Tema |
|---|---|---|---|---|---|
| [AV-0079](#av-0079) | UC-16 | T (E, R) | Operador redirige una orden ya pagada a una dirección controlada por un cómplice mediante el cambio de dirección de excepción | alto (2×3) | R3 |
| [AV-0080](#av-0080) | UC-16 | T (E) | Operador cambia la tienda o la dirección de una orden para reducir o anular el costo de envío de un conocido | medio (2×2) | R3 |
| [AV-0081](#av-0081) | UC-16 | I (R) | Operador de entregas recolecta direcciones, teléfonos y horarios de entrega de órdenes de alto valor para venderlos o planear robos | alto (3×3) | R7 |
| [AV-0082](#av-0082) | UC-16 | T (E, R) | Operador marca como fallido o reprograma una orden ya entregada para provocar un segundo envío a un cómplice | alto (2×3) | R3 |
| [AV-0084](#av-0084) | UC-16 | E (T) | Operador de solo consulta o de otra región modifica órdenes fuera de su alcance manipulando las peticiones entre delivery-admin-front y delivery-api | alto (2×3) | R3 |

### Personal de almacén (4 casos, 2 de riesgo alto)

| Caso | Caso de uso | STRIDE | Abuso | Riesgo | Tema |
|---|---|---|---|---|---|
| [AV-0047](#av-0047) | UC-08 | T (R) | Registro de peso y dimensiones falsos en el empaquetado para desviar costos de transporte y ocultar sustituciones | medio (2×2) | R1 |
| [AV-0048](#av-0048) | UC-08 | E (T) | Transición de estado fuera del rol de preparación ejecutada por personal de almacén para cerrar o encubrir órdenes | alto (2×3) | R3 |
| [AV-0049](#av-0049) | UC-08 | T (R) | Sustracción del producto en almacén encubierta con registro falso de empaquetado, peso y estado | alto (2×3) | R1 |
| [AV-0065](#av-0065) | UC-13 | R (T) | Personal de almacén registra una inspección conforme falsa para liberar el reembolso a un cómplice | medio (1×3) | R6 |

### Personal de tienda (1 caso, 1 de riesgo alto)

| Caso | Caso de uso | STRIDE | Abuso | Riesgo | Tema |
|---|---|---|---|---|---|
| [AV-0006](#av-0006) | UC-12 | T (R) | Personal de tienda marca la orden como entregada sin entregar el producto | alto (2×3) | R1 |

### Empleado de operaciones con acceso a órdenes (1 caso, 1 de riesgo alto)

| Caso | Caso de uso | STRIDE | Abuso | Riesgo | Tema |
|---|---|---|---|---|---|
| [AV-0046](#av-0046) | UC-07 | E (T, R) | Empleado con acceso al registro de órdenes que marca una orden como pagada o altera su total para sustraer producto | alto (2×3) | R3 |

### Repartidor (3 casos, 3 de riesgo alto)

| Caso | Caso de uso | STRIDE | Abuso | Riesgo | Tema |
|---|---|---|---|---|---|
| [AV-0001](#av-0001) | UC-11 | S (R, T) | Entrega registrada sin entregar mediante ubicación GPS simulada | alto (3×3) | R1 |
| [AV-0002](#av-0002) | UC-11 | R (T) | Colusión cliente-repartidor para cobrar el reembolso con el producto entregado | alto (2×3) | R1 |
| [AV-0003](#av-0003) | UC-11 | T (S, R) | Reescritura de las coordenadas del registro de entrega en tránsito entre la app del repartidor y logistic | alto (2×3) | R1 |

### Personal del proveedor logístico (8 casos, 2 de riesgo alto)

| Caso | Caso de uso | STRIDE | Abuso | Riesgo | Tema |
|---|---|---|---|---|---|
| [AV-0050](#av-0050) | UC-09 | T (R) | Paquete sustraído en un centro de distribución encubierto con escaneos de tránsito falsos | medio (2×2) | R1 |
| [AV-0051](#av-0051) | UC-09 | R (T) | Negación de recepción del paquete en el traspaso almacén-proveedor | medio (2×2) | R1 |
| [AV-0053](#av-0053) | UC-09 | I | Venta de datos personales del cliente leídos en etiquetas y escaneos durante el transporte | alto (2×3) | R7 |
| [AV-0054](#av-0054) | UC-09 | D (T) | Retención deliberada de paquetes en un centro de distribución para frenar entregas | bajo (1×2) | R3 |
| [AV-0055](#av-0055) | UC-09 | T (R) | Reasignación de ruta y repartidor para desviar un paquete de alto valor a un cómplice, ocultada como cambio operativo normal | medio (1×3) | R3 |
| [AV-0058](#av-0058) | UC-10 | R (T) | Proveedor logístico niega haber reportado una entrega porque los eventos no son atribuibles | medio (2×2) | R4 |
| [AV-0060](#av-0060) | UC-10 | T (S, R) | Empleado del proveedor logístico registra estados de entrega desde su propio sistema sin escaneo físico, a través de la integración logistic | medio (2×2) | R4 |
| [AV-0064](#av-0064) | UC-13 | R (T) | Conductor de la empresa de logística confirma la recolección inversa sin llevar el producto al almacén | alto (2×3) | R6 |

### Agencia de marketing contratada (1 caso, 0 de riesgo alto)

| Caso | Caso de uso | STRIDE | Abuso | Riesgo | Tema |
|---|---|---|---|---|---|
| [AV-0075](#av-0075) | UC-15 | I (E) | Agencia externa con acceso al backoffice exporta segmentos de clientes y cupones personales | medio (2×2) | R7 |

## 5. Abusos de usuarios externos (clientes y atacantes)

Abusos de **clientes** (con su propia cuenta y su propio tráfico) y de **atacantes externos** (con credenciales robadas, automatización o suplantación). El grupo final son ataques externos cuyo objetivo es la cuenta de un empleado.

### Cliente (28 casos, 16 de riesgo alto)

| Caso | Caso de uso | STRIDE | Abuso | Riesgo | Tema |
|---|---|---|---|---|---|
| [AV-0002](#av-0002) | UC-11 | R (T) | Colusión cliente-repartidor para cobrar el reembolso con el producto entregado | alto (2×3) | R1 |
| [AV-0004](#av-0004) | UC-11 | R (S) | Reclamo falso de entrega a otra persona apoyado en que la geolocalización no prueba quién recibió | medio (2×2) | R1 |
| [AV-0010](#av-0010) | UC-12 | R (S) | Cliente retira el producto en tienda y luego repudia el retiro porque el punto de recolección no deja evidencia independiente | alto (2×3) | R1 |
| [AV-0014](#av-0014) | UC-01 | E (T) | Manipulación de atributos del perfil enviados por el cliente para escalar nivel o membresía | medio (2×2) | R2 |
| [AV-0015](#av-0015) | UC-01 | I (T, E) | Acceso a perfil y direcciones de otro cliente cambiando el identificador en las llamadas a clients-api | alto (2×3) | R7 |
| [AV-0017](#av-0017) | UC-02 | T (E) | Manipulación de precio, cantidad o variante en la petición del carrito | alto (3×3) | R2 |
| [AV-0020](#av-0020) | UC-03 | T (E) | Alteración del código postal y las coordenadas enviados a delivery-api para abaratar el envío o forzar la cobertura | medio (2×2) | R2 |
| [AV-0021](#av-0021) | UC-03 | I (E) | Lectura de direcciones guardadas, nombres y teléfonos de otros clientes cambiando el identificador en clients-api | alto (2×3) | R7 |
| [AV-0022](#av-0022) | UC-03 | R (S) | Cliente que niega haber capturado la dirección y el contacto de la orden para reclamar la entrega fallida | medio (2×2) | R1 |
| [AV-0024](#av-0024) | UC-03 | E (T, I) | Texto malicioso en nombre de contacto y referencias de entrega que se ejecuta con la sesión privilegiada de un empleado en un panel interno | alto (2×3) | R7 |
| [AV-0026](#av-0026) | UC-04 | T (E) | Uso simultáneo de un cupón de un solo uso en varias órdenes antes de que se consuma | medio (2×2) | R2 |
| [AV-0027](#av-0027) | UC-04 | S (E) | Cuentas múltiples para repetir cupones de primera compra o con límite por cliente | alto (3×2) | R8 |
| [AV-0028](#av-0028) | UC-04 | T (E) | Manipulación del total o de las reglas de elegibilidad en la petición de aplicación del cupón | medio (2×2) | R2 |
| [AV-0030](#av-0030) | UC-05 | T (E) | Alteración de atributos de perfil (nivel, membresía, zona) para obtener un envío más barato o gratis | medio (2×2) | R2 |
| [AV-0032](#av-0032) | UC-05 | T (E) | Manipulación de la tarifa cotizada en el tránsito de la respuesta entre delivery-api y el Marketplace | alto (2×3) | R2 |
| [AV-0033](#av-0033) | UC-05 | T (I) | Falsificación de dimensiones, peso o dirección en la solicitud de cotización para abaratar el envío | medio (2×2) | R2 |
| [AV-0034](#av-0034) | UC-05 | E (T) | Abuso de un cupón de envío por cuenta distinta o fuera de condiciones al consultar cupons-api | alto (3×2) | R2 |
| [AV-0036](#av-0036) | UC-06 | T (E) | Alteración del costo de la modalidad de entrega elegida en la petición de selección | alto (3×2) | R2 |
| [AV-0037](#av-0037) | UC-06 | T (E) | Cambio de modalidad o tienda después de calculado el costo para conservar el beneficio de la opción más barata | alto (3×2) | R2 |
| [AV-0039](#av-0039) | UC-06 | E (T) | Asignación de una tienda de recolección fuera de las ofrecidas para obtener una ventana de entrega más corta (acceso fuera de lo autorizado) | medio (2×2) | R2 |
| [AV-0041](#av-0041) | UC-07 | T (S) | Pago de un monto menor al total de la orden aprovechando que el Marketplace no compara el monto confirmado | alto (2×3) | R2 |
| [AV-0042](#av-0042) | UC-07 | T (S, R) | Reutilización de una confirmación de pago legítima de una orden barata para marcar como pagada una orden de alto valor | alto (2×3) | R4 |
| [AV-0043](#av-0043) | UC-07 | T (R) | Cambio del contenido del carrito entre el total mostrado y el registro de la orden | medio (2×2) | R2 |
| [AV-0044](#av-0044) | UC-07 | R (S) | Cliente que desconoce el pago ante la pasarela tras recibir el producto y el comercio no puede probar la vinculación orden-pago-entrega | alto (3×2) | R1 |
| [AV-0045](#av-0045) | UC-07 | I | Consulta de órdenes ajenas modificando el identificador de la orden en la confirmación o el seguimiento posterior al pago | alto (2×3) | R7 |
| [AV-0062](#av-0062) | UC-13 | T (R) | Devolución de un artículo distinto, dañado o una caja con peso equivalente para cobrar el reembolso | alto (2×3) | R6 |
| [AV-0066](#av-0066) | UC-13 | T (D) | Doble reembolso por reenvío concurrente de la solicitud de cancelación | medio (2×2) | R6 |
| [AV-0067](#av-0067) | UC-13 | E | Reutilización de cupón de un solo uso al encadenar compra, cancelación y restitución | medio (2×2) | R6 |

### Atacante externo (20 casos, 12 de riesgo alto)

| Caso | Caso de uso | STRIDE | Abuso | Riesgo | Tema |
|---|---|---|---|---|---|
| [AV-0005](#av-0005) | UC-12 | S (E) | Retiro del producto con el código de otro cliente e identificación falsificada | alto (2×3) | R1 |
| [AV-0007](#av-0007) | UC-12 | I (S) | Consulta de órdenes ajenas en la validación de retiro para obtener códigos y datos personales | alto (2×3) | R7 |
| [AV-0008](#av-0008) | UC-12 | D | Saturación del Punto de recolección con órdenes que nunca se retiran | medio (2×2) | R8 |
| [AV-0009](#av-0009) | UC-12 | S (E) | Suplantación del titular con sesión robada para registrar una persona autorizada inventada y retirar el producto | alto (2×3) | R5 |
| [AV-0011](#av-0011) | UC-01 | S (E) | Registro masivo de cuentas con correos desechables y teléfonos virtuales para eludir la unicidad del cliente | alto (3×2) | R8 |
| [AV-0012](#av-0012) | UC-01 | S (T, I) | Toma de cuenta por relleno de credenciales y cambio de dirección y contacto en el perfil | alto (3×3) | R5 |
| [AV-0013](#av-0013) | UC-01 | I | Enumeración de clientes registrados mediante las respuestas de duplicado del registro | alto (3×2) | R7 |
| [AV-0016](#av-0016) | UC-01 | S (D) | Verificación del teléfono de una víctima adivinando el código de un solo uso en un registro con correo propio del atacante | medio (2×2) | R5 |
| [AV-0018](#av-0018) | UC-02 | D (T) | Denegación de inventario con carritos o reservas masivas de productos voluminosos | medio (2×2) | R8 |
| [AV-0019](#av-0019) | UC-02 | I (D) | Sondeo de disponibilidad con cuenta de cliente para reconstruir el stock exacto por variante y tienda | medio (2×2) | R7 |
| [AV-0023](#av-0023) | UC-03 | S (T) | Cuenta tomada que agrega una dirección nueva y un contacto falsos durante el pago para desviar la compra | alto (3×2) | R5 |
| [AV-0025](#av-0025) | UC-04 | I (E) | Enumeración automatizada de códigos de cupón para obtener descuentos no asignados | medio (2×2) | R8 |
| [AV-0038](#av-0038) | UC-06 | D | Reserva masiva de ventanas de entrega y tiendas por consulta y selección repetida sin completar la compra | medio (2×2) | R8 |
| [AV-0040](#av-0040) | UC-07 | S (T) | Confirmación de pago falsificada enviada al Marketplace para registrar una orden como pagada sin pagar | alto (2×3) | R4 |
| [AV-0052](#av-0052) | UC-09 | S (T) | Retiro del paquete en el almacén por alguien que se hace pasar por el proveedor logístico | alto (2×3) | R1 |
| [AV-0056](#av-0056) | UC-10 | S (T, E) | Evento de estado "entregado" falsificado con la credencial de integración filtrada | alto (2×3) | R4 |
| [AV-0057](#av-0057) | UC-10 | E (T, I) | Credencial de integración con permisos amplios usada para modificar datos más allá de informar estados | alto (2×3) | R4 |
| [AV-0059](#av-0059) | UC-10 | T (I, E) | Contenido malicioso en la ubicación reportada que se muestra al cliente en el Marketplace | alto (2×3) | R4 |
| [AV-0061](#av-0061) | UC-10 | T (D) | Repetición de eventos legítimos de la integración con credencial filtrada para revertir el estado "entregado" de una orden | bajo (1×2) | R4 |
| [AV-0063](#av-0063) | UC-13 | E (I, T) | Cancelación o consulta de devolución sobre órdenes ajenas por referencia directa al identificador | medio (2×2) | R7 |

### Atacante externo contra cuentas de empleados (3 casos, 3 de riesgo alto)

| Caso | Caso de uso | STRIDE | Abuso | Riesgo | Tema |
|---|---|---|---|---|---|
| [AV-0073](#av-0073) | UC-14 | S (I, T, E) | Toma de una cuenta de operador por relleno de credenciales o phishing para leer y editar clientes | alto (2×3) | R5 |
| [AV-0074](#av-0074) | UC-15 | S (E, T) | Toma de cuenta de un operador de marketing para crear cupones de alto valor desde cupons-frontend | alto (2×3) | R5 |
| [AV-0083](#av-0083) | UC-16 | S (T, I, E) | Atacante externo toma la sesión o credenciales de un operador de entregas y gestiona órdenes desde delivery-admin-front | alto (2×3) | R5 |

## 6. Controles de seguridad y buenas prácticas

Los agentes propusieron **397 controles** para los 84 casos (cada caso tiene al menos uno preventivo y uno detectivo; el detalle está en el anexo A). Esta sección los agrupa.

### 6.1 Controles prioritarios por riesgo

**R3 · Privilegios internos sin segregación ni trazabilidad**

- Autorización por función y por objeto en cada API interna, no solo en el frontend; mínimo privilegio y alcance por región, tienda o campaña.
- Doble aprobación para cambios sensibles: cupones de alto valor o sin límite, estados finales, direcciones de órdenes pagadas, atributos de beneficio.
- Motivo obligatorio y vínculo con un caso o ticket en cada cambio manual; acceso a datos personales solo con un caso abierto.
- Cuentas nominales con SSO y MFA; bitácora inmutable (quién, qué, cuándo, desde dónde, valor anterior y nuevo).
- Alertas por concentración: el mismo operador sobre las mismas cuentas, excepciones frecuentes, cambios fuera de horario.

**R1 · Evidencia y registros que no prueban lo que ocurrió**

- Código de confirmación de un solo uso del cliente obligatorio para cerrar entregas y retiros de alto valor; foto o firma solo como complemento.
- Atestación del dispositivo y detección de ubicación simulada en la app del repartidor; registro de entrega firmado en el dispositivo.
- Escaneo conjunto con peso y foto en cada traspaso de custodia (almacén → proveedor → repartidor → cliente o tienda).
- Conciliación diaria entre despachos, escaneos del proveedor, entregas e inventario de tiendas.
- Registro inmutable de la orden con la referencia de pago, la dirección confirmada y la evidencia de entrega, para disputas y contracargos.

**R7 · Exposición de datos personales y de negocio**

- Autorización por objeto en cada consulta (la orden, la dirección o el perfil pertenecen a quien pregunta); identificadores no predecibles.
- Respuestas mínimas y mensajes de error genéricos en registro, cupones y consultas de disponibilidad.
- Enmascaramiento de datos en backoffice, app del repartidor y etiquetas; límites de consulta y alertas de extracción masiva.
- Codificación de salida y política de seguridad de contenido en los paneles internos que muestran datos capturados por clientes.

**R2 · Montos y beneficios calculados con datos que controla el cliente**

- Recalcular en el servidor, al confirmar la orden, todo valor monetario: precio desde el catálogo, envío con delivery-api, descuento con cupons-api.
- Cotización firmada y con vigencia corta, ligada a la orden, la dirección, la modalidad y la tienda; cualquier cambio obliga a recotizar.
- Atributos de beneficio del perfil (nivel, membresía, zona) editables solo por procesos del servidor; listas de campos permitidos en cada API.
- Reserva atómica del cupón (restricción única o bloqueo) antes del cobro, y validación con los datos de la orden final.
- Comparar el monto confirmado por la pasarela con el total registrado de la orden antes de liberarla.

**R5 · Toma de cuentas de clientes y de empleados**

- MFA para empleados siempre y para clientes en acciones sensibles: cambio de dirección o contacto, autorizados de retiro, uso de medios de pago guardados.
- Protección contra relleno de credenciales: límite de intentos, detección de automatización, credenciales filtradas y dispositivos nuevos.
- Códigos de verificación con pocos intentos, expiración corta y bloqueo progresivo.
- Aviso al titular por un canal independiente antes de que surta efecto un cambio de contacto, dirección o autorizado, con opción de revertirlo.

**R4 · Confianza ciega en la integración logística y en las confirmaciones de pago**

- Credenciales por sistema con mTLS o firma de mensajes, rotación y lista de IPs permitidas; permisos de la integración limitados a informar estados.
- Eventos firmados con identificador único, secuencia y marca de tiempo; rechazo de repeticiones y de transiciones de estado imposibles.
- Validar la firma de cada notificación de la pasarela y consultar el estado del pago a la pasarela antes de dar la orden por pagada.
- Referencias de pago de un solo uso, ligadas a la orden y al monto.
- Sanear y codificar los campos de texto de los eventos (ubicación, notas) antes de mostrarlos al cliente o en el backoffice.

**R8 · Abuso de beneficios y de capacidad mediante automatización**

- Unicidad del cliente con señales adicionales (dispositivo, dirección de entrega, medio de pago), no solo correo y teléfono.
- Protección contra automatización y límites por cuenta, dispositivo, dirección y medio de pago.
- Códigos de cupón largos y aleatorios, ligados a la cuenta destinataria; límite de intentos de validación.
- Reservas de inventario, ventanas y capacidad de tienda con expiración corta y tope de pendientes por cliente.

**R6 · Reembolsos y restituciones antes de verificar la devolución**

- Reembolso solo después de la inspección en almacén, con número de serie, peso y fotos comparados con el despacho original.
- Inspecciones de alto valor confirmadas por una segunda persona.
- Cancelación idempotente: un identificador único de reembolso y una máquina de estados que impide reembolsar dos veces.
- Restitución del cupón solo cuando la devolución queda recibida e inspeccionada.

### 6.2 Buenas prácticas transversales

Prácticas que se repiten en los controles propuestos para casos de abuso distintos. El número indica en cuántos casos aparece (búsqueda por palabras clave sobre el texto de los controles; es una aproximación).

| Buena práctica | Casos en que se propone |
|---|---|
| Alertas y monitoreo de patrones de abuso | 79 |
| Conciliación entre registros (despachos, escaneos, entregas, pagos) | 26 |
| Notificación al titular de cambios y eventos sensibles | 23 |
| Código de confirmación o escaneo obligatorio | 21 |
| Doble aprobación o segregación de funciones | 20 |
| Recalcular en el servidor los valores que envía el cliente | 18 |
| Bitácora inmutable de acciones | 17 |
| Firma, mTLS o integridad criptográfica de datos entre partes | 16 |
| Mínimo privilegio y alcance por rol | 13 |
| Idempotencia, identificadores únicos y códigos de un solo uso | 12 |
| Motivo obligatorio o vínculo con un caso de soporte | 11 |
| Límites de frecuencia y protección contra automatización | 10 |
| Autenticación multifactor | 9 |
| Autorización por objeto y por función en las APIs | 7 |

### 6.3 Quién implementa los controles

| Tipo | Ecommerce | Proveedor logístico | Pasarela de pago | Total |
|---|---|---|---|---|
| Preventivo | 157 | 27 | 16 | 200 |
| Detectivo | 89 | 17 | 2 | 108 |
| Correctivo | 74 | 14 | 1 | 89 |

Una parte de los controles depende del **proveedor logístico** (app del repartidor, escaneos, credenciales de la integración). Deben quedar en el contrato como requisitos de seguridad con evidencia verificable, porque el ecommerce no los opera.

## 7. Principales riesgos

Agrupación de los casos de abuso por la debilidad de fondo que explotan, ordenada por número de casos de riesgo alto.

| # | Riesgo | Casos | Riesgo alto | Internos / externos | Casos de uso |
|---|---|---|---|---|---|
| 1 | **R3** Privilegios internos sin segregación ni trazabilidad | 18 | 9 | 18 / 0 | UC-04, UC-05, UC-07, UC-08, UC-09, UC-14, UC-15, UC-16 |
| 2 | **R1** Evidencia y registros que no prueban lo que ocurrió | 14 | 9 | 8 / 7 | UC-03, UC-07, UC-08, UC-09, UC-11, UC-12 |
| 3 | **R7** Exposición de datos personales y de negocio | 12 | 9 | 4 / 8 | UC-01, UC-02, UC-03, UC-07, UC-09, UC-12, UC-13, UC-14, UC-15, UC-16 |
| 4 | **R2** Montos y beneficios calculados con datos que controla el cliente | 14 | 6 | 0 / 14 | UC-01, UC-02, UC-03, UC-04, UC-05, UC-06, UC-07 |
| 5 | **R5** Toma de cuentas de clientes y de empleados | 7 | 6 | 0 / 7 | UC-01, UC-03, UC-12, UC-14, UC-15, UC-16 |
| 6 | **R4** Confianza ciega en la integración logística y en las confirmaciones de pago | 8 | 5 | 2 / 6 | UC-07, UC-10 |
| 7 | **R8** Abuso de beneficios y de capacidad mediante automatización | 6 | 2 | 0 / 6 | UC-01, UC-02, UC-04, UC-06, UC-12 |
| 8 | **R6** Reembolsos y restituciones antes de verificar la devolución | 5 | 2 | 2 / 3 | UC-13 |

### R3 · Privilegios internos sin segregación ni trazabilidad

Operadores de atención, marketing y entregas, personal de almacén y personal del proveedor pueden cambiar perfiles, cupones, direcciones, estados y asignaciones sin motivo, sin segunda aprobación, con cuentas compartidas o con permisos más amplios que su rol. Las APIs internas confían en que el frontend ya filtró lo que el operador puede hacer.

- **Dónde:** LC-3 en F24–F29; LC-4 en F30; RN-1, RN-2 y RN-4.
- **Casos:** [AV-0029](#av-0029), [AV-0031](#av-0031), [AV-0035](#av-0035), [AV-0046](#av-0046), [AV-0048](#av-0048), [AV-0054](#av-0054), [AV-0055](#av-0055), [AV-0069](#av-0069), [AV-0070](#av-0070), [AV-0071](#av-0071), [AV-0072](#av-0072), [AV-0076](#av-0076), [AV-0077](#av-0077), [AV-0078](#av-0078), [AV-0079](#av-0079), [AV-0080](#av-0080), [AV-0082](#av-0082), [AV-0084](#av-0084).
- **Controles prioritarios:** ver 6.1.

### R1 · Evidencia y registros que no prueban lo que ocurrió

Entregas, retiros, traspasos de custodia, inspecciones y confirmaciones se registran con datos que genera o controla la misma parte que se beneficia (GPS del dispositivo, foto, firma ilegible, escaneo opcional, estado marcado a mano). El sistema acepta el registro como prueba del hecho físico, y ante un reclamo nadie puede demostrar qué pasó.

- **Dónde:** LC-5 (mundo físico ↔ sistemas) en F14–F23; RN-3.
- **Casos:** [AV-0001](#av-0001), [AV-0002](#av-0002), [AV-0003](#av-0003), [AV-0004](#av-0004), [AV-0005](#av-0005), [AV-0006](#av-0006), [AV-0010](#av-0010), [AV-0022](#av-0022), [AV-0044](#av-0044), [AV-0047](#av-0047), [AV-0049](#av-0049), [AV-0050](#av-0050), [AV-0051](#av-0051), [AV-0052](#av-0052).
- **Controles prioritarios:** ver 6.1.

### R7 · Exposición de datos personales y de negocio

Perfiles, direcciones, órdenes, códigos de retiro y datos de stock se leen cambiando identificadores en las peticiones (autorización por objeto ausente), enumerando respuestas diferenciadas, abusando del acceso interno de consulta o leyendo etiquetas en el transporte. Un texto malicioso guardado por un cliente puede ejecutarse en el panel de un empleado.

- **Dónde:** LC-1 y LC-2 en F1–F5; LC-3 en F27 y F29; F15–F20.
- **Casos:** [AV-0007](#av-0007), [AV-0013](#av-0013), [AV-0015](#av-0015), [AV-0019](#av-0019), [AV-0021](#av-0021), [AV-0024](#av-0024), [AV-0045](#av-0045), [AV-0053](#av-0053), [AV-0063](#av-0063), [AV-0068](#av-0068), [AV-0075](#av-0075), [AV-0081](#av-0081).
- **Controles prioritarios:** ver 6.1.

### R2 · Montos y beneficios calculados con datos que controla el cliente

Precio, cantidad, costo de envío, modalidad, tienda, atributos del perfil, reglas del cupón y monto del pago viajan en peticiones del cliente o entre servicios sin recalcularse ni firmarse. Quien intercepta su propio tráfico o encadena pasos fuera de orden paga menos o recibe beneficios que no le corresponden.

- **Dónde:** LC-1 y LC-2 en F1, F3–F7, F9, F10; RN-2 y RN-4.
- **Casos:** [AV-0014](#av-0014), [AV-0017](#av-0017), [AV-0020](#av-0020), [AV-0026](#av-0026), [AV-0028](#av-0028), [AV-0030](#av-0030), [AV-0032](#av-0032), [AV-0033](#av-0033), [AV-0034](#av-0034), [AV-0036](#av-0036), [AV-0037](#av-0037), [AV-0039](#av-0039), [AV-0041](#av-0041), [AV-0043](#av-0043).
- **Controles prioritarios:** ver 6.1.

### R5 · Toma de cuentas de clientes y de empleados

Con credenciales filtradas, sesiones robadas o phishing, un atacante entra a la cuenta de un cliente (y cambia dirección o contacto, agrega un autorizado o compra con el medio de pago guardado) o a la de un operador (y lee o modifica clientes, cupones y órdenes). La verificación del teléfono sin límite de intentos permite asociar el número de otra persona.

- **Dónde:** LC-1 en F1 y F3; LC-3 en F24–F26.
- **Casos:** [AV-0009](#av-0009), [AV-0012](#av-0012), [AV-0016](#av-0016), [AV-0023](#av-0023), [AV-0073](#av-0073), [AV-0074](#av-0074), [AV-0083](#av-0083).
- **Controles prioritarios:** ver 6.1.

### R4 · Confianza ciega en la integración logística y en las confirmaciones de pago

delivery-api acepta eventos de estado, entrega y ubicación de logistic con una credencial de servicio compartida y con permisos más amplios que informar estados; el Marketplace acepta confirmaciones de pago sin verificar firma, unicidad ni correspondencia con la orden. Quien obtiene la credencial, o un empleado del proveedor, fabrica o repite eventos que el sistema toma como verdad.

- **Dónde:** LC-4 en F19 y F30; LC-6 en F6 y F7.
- **Casos:** [AV-0040](#av-0040), [AV-0042](#av-0042), [AV-0056](#av-0056), [AV-0057](#av-0057), [AV-0058](#av-0058), [AV-0059](#av-0059), [AV-0060](#av-0060), [AV-0061](#av-0061).
- **Controles prioritarios:** ver 6.1.

### R8 · Abuso de beneficios y de capacidad mediante automatización

Cuentas creadas en masa (correo desechable y teléfono virtual eluden RN-1), enumeración de cupones y scripts que acaparan inventario, ventanas de entrega o espacio en puntos de recolección sin pagar ni retirar. No hace falta romper nada: basta repetir el flujo normal más veces de las previstas.

- **Dónde:** LC-1 en F1, F4 y F5; RN-1 y RN-4.
- **Casos:** [AV-0008](#av-0008), [AV-0011](#av-0011), [AV-0018](#av-0018), [AV-0025](#av-0025), [AV-0027](#av-0027), [AV-0038](#av-0038).
- **Controles prioritarios:** ver 6.1.

### R6 · Reembolsos y restituciones antes de verificar la devolución

El reembolso y la restitución del cupón se disparan con la solicitud de cancelación, con la confirmación de recolección del proveedor o con una inspección que registra una sola persona. El cliente devuelve otra cosa, cancela dos veces en paralelo o reutiliza el cupón; un empleado o un conductor confirma lo que no recibió.

- **Dónde:** F5, F6, F14 y F30 en UC-13; S-11, S-12 y S-19.
- **Casos:** [AV-0062](#av-0062), [AV-0064](#av-0064), [AV-0065](#av-0065), [AV-0066](#av-0066), [AV-0067](#av-0067).
- **Controles prioritarios:** ver 6.1.

### Mapa de calor (probabilidad × impacto)

| Probabilidad \ Impacto | 1 bajo | 2 medio | 3 alto |
|---|---|---|---|
| 3 alta | · | 8 | 4 |
| 2 media | · | 30 | 36 |
| 1 baja | · | 3 | 3 |

Casos en la celda de mayor riesgo (probabilidad 3 e impacto 3): [AV-0001](#av-0001) (Entrega registrada sin entregar mediante ubicación GPS simulada), [AV-0012](#av-0012) (Toma de cuenta por relleno de credenciales y cambio de dirección y contacto en el perfil), [AV-0017](#av-0017) (Manipulación de precio, cantidad o variante en la petición del carrito), [AV-0081](#av-0081) (Operador de entregas recolecta direcciones, teléfonos y horarios de entrega de órdenes de alto valor para venderlos o planear robos).

## 8. Casos fuera de alcance

Pasaron la revisión automática, pero el analista no los consolidó en la memoria por los supuestos de alcance. Su detalle completo está en los resultados de [`evidencias/fase7/`](evidencias/fase7).

| Caso | Caso de uso | STRIDE | Abuso | Motivo |
|---|---|---|---|---|
| AC-UC03-04 | UC-03 | D | Consumo masivo de la consulta de cobertura y costo de envío para saturar delivery-api | S-22: denegación de servicio volumétrica (saturación del endpoint de cotización). |
| AC-UC05-07 | UC-05 | D | Saturación de delivery-api y de sus dependencias con cotizaciones masivas automatizadas | S-22: denegación de servicio volumétrica (cotizaciones masivas). |
| AC-UC05-08 | UC-05 | S (T) | Suplantación de clients-api y cupons-api frente a delivery-api para inyectar atributos de perfil y cupones falsos | S-24: interceptación en la red interna (suplantación ARP de APIs internas). |
| AC-UC10-06 | UC-10 | D (T) | Ráfaga de eventos falsos o masivos que degrada delivery-api y oculta los eventos legítimos | S-22: denegación de servicio volumétrica (ráfaga de eventos). |
| AC-UC14-07 | UC-14 | D | Degradación de clients-api con búsquedas amplias y repetidas desde una sesión de backoffice | S-22: denegación de servicio volumétrica (búsquedas masivas en clients-api). |
| AC-UC16-07 | UC-16 | D (T) | Operador con cuenta propia o comprometida dispara cambios masivos de estado y reprogramación que agotan la capacidad de delivery-api y de la vía hacia el proveedor logístico | S-22: denegación de servicio volumétrica (cambios masivos de estado). |

## 9. Supuestos

Los supuestos del modelo están en [`01-casos-de-uso-y-supuestos.md`](01-casos-de-uso-y-supuestos.md) §6 (S-01 a S-27) y en [`03-arquitectura.md`](03-arquitectura.md) §10 (S-28 a S-35). Además, para que cada caso de abuso sea posible, los agentes declararon **supuestos derivados**: condiciones del sistema que el caso da por ciertas, como la ausencia de un control. Se listan en el anexo B. En una revisión con el equipo del sistema, cada supuesto derivado se confirma o se descarta; si se descarta, el caso baja de riesgo o desaparece.

Supuestos del análisis de riesgos:

- La probabilidad y el impacto los estimó el agente de mitigación con la información del caso, sin datos de incidentes reales; sirven para priorizar, no como medición.
- Los controles describen qué hacer; su costo y su factibilidad no se evaluaron.
- Los productos voluminosos se tratan como de alto valor (S-23), lo que eleva el impacto de los abusos que terminan en pérdida del producto.
- Los temas de riesgo agrupan casos por su debilidad de fondo; un caso se asigna a un solo tema, aunque toque varios.

## 10. Limitaciones

- Los casos de abuso los generó un modelo de lenguaje con el contexto disponible. El revisor automático y el analista filtraron calidad y alcance, pero no se probaron contra un sistema real: son hipótesis de abuso a validar.
- Algunos casos parecidos aparecen en casos de uso distintos del mismo lote (por ejemplo, lectura de datos ajenos cambiando el identificador en AC-UC01-06, AC-UC03-02 y AC-UC07-06), porque la memoria solo los conoce después de consolidar el lote. Se conservaron porque afectan a objetos distintos; los temas de riesgo los agrupan.
- El esquema admite un solo actor por caso; las colusiones se registraron con un actor principal (ver ajustes del analista).
- Las referencias a CAPEC y OWASP son orientativas: el modelo las eligió entre el contexto recuperado.

## Anexo A · Detalle de los casos de abuso

Ordenados por su ID en la memoria de largo plazo (`ltm_abusos`). Entre paréntesis, el ID original de la ejecución de WF-2.

### UC-01 Registro y gestión de la cuenta del cliente

<a id="av-0011"></a>
#### AV-0011 · Registro masivo de cuentas con correos desechables y teléfonos virtuales para eludir la unicidad del cliente

- **ID de origen:** AC-UC01-01 · **Ejecución:** Lote 1 · **Tema de riesgo:** R8
- **STRIDE:** S (E) — Suplantación
- **Actor:** Atacante o grupo organizado que abusa de beneficios por cliente (externo)
- **Elementos del DFD:** F1, F3, Marketplace, clients-api · **Límites:** LC-1, LC-2
- **Precondiciones:**
  - El formulario de registro del Marketplace es público y accesible sin autenticación previa
  - La unicidad del cliente (RN-1) se valida solo por correo y teléfono
  - El código de un solo uso se envía a cualquier correo o número, incluidos desechables y virtuales
  - No hay huella de dispositivo ni protección contra automatización en el registro (S-01, S-07, S-08 no la garantizan)
- **Cómo ocurre:**
  1. El atacante prepara un lote de buzones de correo desechables y números de SMS virtuales de alquiler
  2. Mediante una herramienta de automatización de navegador completa el formulario de registro del Marketplace repetidamente, variando correo, teléfono y nombre
  3. Marketplace envía cada alta a clients-api por F3; clients-api compara solo correo y teléfono y no encuentra duplicados
  4. El atacante lee los códigos de un solo uso en los buzones y paneles de SMS virtuales y verifica cada cuenta
  5. Cada cuenta registra la misma dirección de entrega o una con variaciones menores
  6. Con las cuentas activas reclama el beneficio de primera compra o de nuevo cliente varias veces
- **Vector práctico:** Acción: alta automatizada y en ráfaga de cuentas. Herramienta: automatización de navegador sin interfaz, servicios de correo desechable y de SMS virtual. Dato manipulado: correo y teléfono, únicos identificadores que clients-api usa para la regla RN-1, variados en cada alta mientras la dirección y el dispositivo permanecen constantes.
- **Impacto:** Se rompe la regla de un único registro por cliente, lo que permite cobrar beneficios de primera compra varias veces y ensucia la base de clientes con identidades falsas. También facilita abusos posteriores con cuentas masivas, como los de pedidos y recolección.
- **Riesgo:** alto (3×2). El registro es público y la unicidad (RN-1) depende solo de correo y teléfono, así que automatizar altas con datos desechables es barato y muy probable, aunque el daño se limita a pérdida por beneficios repetidos y a datos de clientes contaminados.
- **Controles:**
  - *preventivo* (ecommerce): Proteger el formulario de registro con captcha o prueba de humanidad adaptativa y límite de tasa por IP, dispositivo y subred, validado en el servidor del Marketplace antes de reenviar por F3 a clients-api.
  - *preventivo* (ecommerce): Rechazar dominios de correo desechable y rangos de numeración de SMS virtual (VoIP) en el alta, con listas actualizadas y verificación del tipo de línea; exigir un teléfono móvil real.
  - *preventivo* (ecommerce): Limitar el beneficio de primera compra a una vez por dirección de entrega normalizada y por medio de pago tokenizado, no solo por cuenta, correo o teléfono.
  - *preventivo* (pasarela de pago): Aplicar un límite de beneficios de nuevo cliente por huella de tarjeta (fingerprint del token) y rechazar la promoción cuando el mismo instrumento ya la usó en otra cuenta.
  - *detectivo* (ecommerce): Alertar por ráfagas de altas desde el mismo dispositivo o ASN y por clusters de cuentas con la misma dirección de entrega normalizada o patrón de correo (por ejemplo, secuencias alfanuméricas).
  - *detectivo* (proveedor logístico): Alertar cuando varios pedidos de cuentas distintas con beneficio de primera compra converjan en la misma dirección de entrega, para detectarlo antes del despacho.
  - *correctivo* (ecommerce): Suspender y fusionar o revocar las cuentas del cluster detectado, anular los beneficios aplicados y retener los pedidos pendientes hasta validar la identidad del cliente.
- **Referencias y patrones:** CAPEC-202, OWASP API6:2023 Unrestricted Access to Sensitive Business Flows, FE-03, AV-0008

<a id="av-0012"></a>
#### AV-0012 · Toma de cuenta por relleno de credenciales y cambio de dirección y contacto en el perfil

- **ID de origen:** AC-UC01-02 · **Ejecución:** Lote 1 · **Tema de riesgo:** R5
- **STRIDE:** S (T, I) — Suplantación
- **Actor:** Atacante con credenciales filtradas de otros servicios (externo)
- **Elementos del DFD:** F1, F3, Marketplace, clients-api · **Límites:** LC-1, LC-2
- **Precondiciones:**
  - Existen clientes que reutilizan contraseña en otros servicios filtrados
  - El inicio de sesión no exige un segundo factor ni limita intentos por cuenta, IP o dispositivo
  - La edición de direcciones y contacto no pide reautenticación ni notifica al titular
- **Cómo ocurre:**
  1. El atacante obtiene un listado de correos y contraseñas filtrados de otros servicios
  2. Con una herramienta de automatización envía intentos de inicio de sesión al Marketplace distribuidos entre muchas IP, probando cada par una sola vez
  3. Al entrar a una cuenta, abre el perfil y lee nombre, teléfono, correo y direcciones guardadas
  4. Edita el teléfono de contacto y agrega una dirección controlada por él; Marketplace envía la actualización a clients-api por F3
  5. clients-api guarda el cambio sin pedir reautenticación y sin avisar al correo o teléfono anteriores
  6. El atacante usa la cuenta para comprar con la dirección nueva, o bloquea al titular cambiando el correo y el teléfono
- **Vector práctico:** Acción: relleno de credenciales seguido de edición del perfil. Herramienta: automatización de solicitudes de inicio de sesión con rotación de IP. Dato manipulado: credenciales de acceso reutilizadas, y luego teléfono, correo y direcciones del perfil, que clients-api acepta sin segundo factor ni aviso al titular.
- **Impacto:** El atacante accede a datos personales del cliente, redirige envíos y se apropia de la cuenta, lo que genera fraude, pérdida del acceso legítimo y exposición de información personal.
- **Riesgo:** alto (3×3). El relleno de credenciales con listas filtradas es muy frecuente, y sin segundo factor, límites de intentos ni avisos permite robar datos personales, desviar envíos y bloquear al titular.
- **Controles:**
  - *preventivo* (ecommerce): Ofrecer autenticación multifactor (OTP o passkey) en el inicio de sesión del Marketplace, obligatoria ante dispositivo o país nuevo, y consultar contraseñas filtradas (listas de contraseñas comprometidas) al crear o cambiar la clave.
  - *preventivo* (ecommerce): Limitar intentos de inicio de sesión por cuenta, IP, dispositivo y a nivel global, con bloqueo progresivo y captcha tras fallos, de modo que la rotación de IP con un intento por par también se detecte por la tasa de fallos distribuidos.
  - *preventivo* (ecommerce): Exigir reautenticación o confirmación con OTP para cambiar correo, teléfono o direcciones en clients-api, y bloquear cambios de dirección en pedidos ya pagados.
  - *preventivo* (pasarela de pago): Exigir 3-D Secure o reingreso del CVV al pagar con un medio de pago guardado desde un dispositivo no reconocido.
  - *detectivo* (ecommerce): Detectar patrones de relleno de credenciales (muchos fallos contra muchas cuentas, inicio de sesión desde dispositivo o país nuevo seguido de cambio de dirección o contacto) y generar alertas de riesgo en tiempo casi real.
  - *detectivo* (ecommerce): Notificar al correo y teléfono anteriores del titular cada cambio de contacto, dirección o credenciales, con enlace para revertir el cambio.
  - *correctivo* (ecommerce): Ante una cuenta tomada, cerrar sesiones, forzar el cambio de contraseña, revertir las modificaciones del perfil, retener los pedidos con dirección modificada y recuperar la cuenta con verificación de identidad.
  - *correctivo* (proveedor logístico): Redirigir o detener envíos en tránsito cuando el Marketplace confirme el desvío, con un canal de cancelación de entrega acordado.
- **Referencias y patrones:** OWASP API2:2023 Broken Authentication, FE-11, AV-0009

<a id="av-0013"></a>
#### AV-0013 · Enumeración de clientes registrados mediante las respuestas de duplicado del registro

- **ID de origen:** AC-UC01-04 · **Ejecución:** Lote 1 · **Tema de riesgo:** R7
- **STRIDE:** I — Divulgación de información
- **Actor:** Atacante que busca perfilar clientes para fraude o phishing (externo)
- **Elementos del DFD:** F1, F3, Marketplace, clients-api · **Límites:** LC-1, LC-2
- **Precondiciones:**
  - clients-api responde de forma distinguible cuando un correo o teléfono ya existe (RN-1)
  - El formulario de registro no tiene límite de tasa ni protección contra automatización
- **Cómo ocurre:**
  1. El atacante reúne listas de correos y teléfonos de objetivos obtenidas de filtraciones o de listas comerciales
  2. Con una herramienta de automatización envía solicitudes de registro con cada identificador a través del Marketplace
  3. clients-api ejecuta la validación de unicidad y el Marketplace devuelve un mensaje o código distinto cuando el identificador ya está registrado
  4. El atacante clasifica qué personas son clientes del Marketplace según la diferencia de respuesta
  5. Usa esa lista para campañas de phishing dirigidas o para priorizar el relleno de credenciales sobre cuentas existentes
- **Vector práctico:** Acción: sondeo masivo del registro para detectar duplicados. Herramienta: script de automatización de solicitudes con rotación de IP. Dato manipulado: correo y teléfono enviados al validador de unicidad, cuya respuesta diferenciada revela la existencia de la cuenta.
- **Impacto:** Se expone qué personas tienen cuenta en la plataforma, lo que facilita phishing dirigido, toma de cuentas y vulneración de la privacidad de los clientes.
- **Riesgo:** alto (3×2). Distinguir respuestas de duplicado es trivial de automatizar con rotación de IP; el impacto es medio porque solo revela que una persona tiene cuenta, pero habilita phishing y relleno de credenciales dirigidos.
- **Controles:**
  - *preventivo* (ecommerce): Unificar la respuesta del registro para identificadores existentes y nuevos (mensaje, código HTTP y tiempo de respuesta), y notificar el duplicado solo por correo al titular real, sin revelarlo en pantalla.
  - *preventivo* (ecommerce): Aplicar límite de tasa y captcha en registro y verificación de unicidad por IP, dispositivo e identificador consultado, con cuotas diarias.
  - *detectivo* (ecommerce): Monitorear volúmenes anómalos de solicitudes de registro con identificadores distintos sin completar la verificación OTP, y la proporción de duplicados por origen.
  - *correctivo* (ecommerce): Bloquear temporalmente orígenes y dispositivos con patrón de sondeo y alertar a los clientes que aparecieron como existentes si se confirma una campaña de phishing asociada.
- **Referencias y patrones:** CAPEC-575, OWASP API6:2023 Unrestricted Access to Sensitive Business Flows, FE-11

<a id="av-0014"></a>
#### AV-0014 · Manipulación de atributos del perfil enviados por el cliente para escalar nivel o membresía

- **ID de origen:** AC-UC01-05 · **Ejecución:** Lote 1 · **Tema de riesgo:** R2
- **STRIDE:** E (T) — Elevación de privilegios
- **Actor:** Cliente registrado con conocimientos técnicos (externo)
- **Elementos del DFD:** F1, F3, Marketplace, clients-api · **Límites:** LC-1, LC-2
- **Precondiciones:**
  - La actualización del perfil viaja del Marketplace a clients-api con un objeto de perfil que puede incluir atributos internos como nivel o membresía
  - clients-api acepta los campos recibidos sin filtrar cuáles puede modificar el cliente
  - El cliente puede interceptar y modificar sus propias solicitudes desde el navegador
- **Cómo ocurre:**
  1. El cliente inicia sesión y edita un dato permitido de su perfil, por ejemplo una dirección
  2. Con un proxy de interceptación observa la solicitud de actualización que envía el Marketplace por F1
  3. Agrega o cambia en el cuerpo de la solicitud campos como nivel, membresía o estado del perfil, que conoce por inferencia o por respuestas previas de la API
  4. Marketplace reenvía el objeto a clients-api por F3, que lo guarda sin comprobar que esos atributos solo los gestiona un empleado desde UC-14
  5. En la siguiente compra el cliente recibe beneficios del nuevo nivel
- **Vector práctico:** Acción: modificación de la solicitud de edición de perfil para añadir atributos protegidos. Herramienta: proxy de interceptación en el navegador. Dato manipulado: campos de nivel o membresía del objeto de perfil enviado a clients-api, que debería reservarse a operadores internos.
- **Impacto:** El cliente obtiene beneficios o precios a los que no tiene derecho, lo que genera pérdida económica y corrompe los atributos de perfil que usan otros procesos.
- **Riesgo:** medio (2×2). Requiere cuenta e interceptación de solicitudes, algo accesible para perfiles técnicos, y el impacto es económico acotado por los beneficios de nivel o membresía.
- **Controles:**
  - *preventivo* (ecommerce): Definir en clients-api una lista blanca de campos editables por el cliente (DTO de entrada), ignorar o rechazar con error cualquier otro campo como nivel, membresía o estado, y asignar esos atributos solo desde el flujo interno de UC-14 con rol de operador.
  - *preventivo* (ecommerce): Calcular el nivel y los beneficios en el servidor al momento de la compra a partir de datos autoritativos, sin confiar en atributos enviados por el cliente.
  - *detectivo* (ecommerce): Registrar y alertar los intentos de enviar campos protegidos en actualizaciones de perfil, y conciliar periódicamente los cambios de nivel o membresía contra operaciones internas autorizadas.
  - *correctivo* (ecommerce): Revertir los niveles asignados sin autorización, recalcular los pedidos con beneficios indebidos y suspender las cuentas reincidentes.
- **Referencias y patrones:** OWASP API3:2023 Broken Object Property Level Authorization, CAPEC-202, AV-0003

<a id="av-0015"></a>
#### AV-0015 · Acceso a perfil y direcciones de otro cliente cambiando el identificador en las llamadas a clients-api

- **ID de origen:** AC-UC01-06 · **Ejecución:** Lote 1 · **Tema de riesgo:** R7
- **STRIDE:** I (T, E) — Divulgación de información
- **Actor:** Cliente autenticado con malas intenciones (externo)
- **Elementos del DFD:** F1, F3, Marketplace, clients-api · **Límites:** LC-1, LC-2
- **Precondiciones:**
  - Las consultas y actualizaciones de perfil y direcciones usan un identificador de cliente o de dirección en la solicitud
  - clients-api no verifica que el recurso pertenezca al cliente autenticado en la sesión
  - Los identificadores son predecibles o secuenciales
- **Cómo ocurre:**
  1. El atacante crea su propia cuenta y abre su perfil, observando con un proxy las solicitudes que Marketplace envía hacia clients-api
  2. Identifica el identificador de cliente o de dirección en la ruta o en el cuerpo
  3. Con una herramienta de automatización sustituye ese identificador por valores cercanos y repite la consulta
  4. clients-api devuelve nombres, teléfonos, correos y direcciones de otros clientes porque solo valida que la sesión sea válida
  5. Para modificar, repite el proceso con la solicitud de actualización y cambia la dirección o el contacto de otra cuenta
- **Vector práctico:** Acción: sustitución secuencial de identificadores de recurso en las solicitudes de perfil y direcciones. Herramienta: proxy de interceptación y automatización de peticiones. Dato manipulado: identificador de cliente o de dirección en la solicitud hacia clients-api, sin verificación de propiedad.
- **Impacto:** Se expone en masa información personal de clientes y se pueden alterar sus direcciones de envío, lo que permite fraude, desvío de pedidos e incumplimiento de normas de protección de datos.
- **Riesgo:** alto (2×3). Basta una cuenta propia y un proxy para probar BOLA con identificadores predecibles; si funciona, expone datos personales en masa y permite alterar direcciones de envío.
- **Controles:**
  - *preventivo* (ecommerce): Verificar en clients-api, en cada consulta o actualización de perfil y direcciones, que el recurso pertenece al cliente autenticado, derivando el identificador de cliente del token de sesión y no del parámetro de la solicitud.
  - *preventivo* (ecommerce): Usar identificadores no secuenciales de alta entropía (UUID v4) para clientes y direcciones, y pruebas automatizadas de autorización por objeto en el pipeline.
  - *detectivo* (ecommerce): Detectar y alertar sesiones que consulten muchos identificadores distintos al propio o acumulen respuestas 403 o 404 por acceso a recursos ajenos, con registro de acceso a datos personales.
  - *correctivo* (ecommerce): Revocar la sesión y bloquear la cuenta atacante, restaurar las direcciones y contactos alterados desde el historial de cambios, notificar a los clientes afectados y activar el protocolo de brecha de datos personales.
  - *correctivo* (proveedor logístico): Retener o redirigir pedidos cuya dirección de entrega haya sido alterada por acceso indebido, cuando el Marketplace lo notifique antes de la entrega.
- **Referencias y patrones:** OWASP API1:2023 Broken Object Level Authorization, FE-11, CAPEC-575

<a id="av-0016"></a>
#### AV-0016 · Verificación del teléfono de una víctima adivinando el código de un solo uso en un registro con correo propio del atacante

- **ID de origen:** AC-UC01-03 · **Ejecución:** Lote 1 · **Tema de riesgo:** R5
- **STRIDE:** S (D) — Suplantación
- **Actor:** Atacante que conoce el número de teléfono de una víctima que aún no tiene cuenta (externo)
- **Elementos del DFD:** F1, F3, Marketplace, clients-api · **Límites:** LC-1, LC-2
- **Precondiciones:**
  - El número de teléfono de la víctima no está registrado en clients-api (RN-1)
  - El código de un solo uso del teléfono es numérico y corto, y el endpoint de verificación de clients-api no limita los intentos fallidos por registro pendiente ni por origen
  - El código sigue siendo válido durante una ventana de varios minutos y no se invalida tras N intentos fallidos
  - El atacante controla un correo desechable propio, con el que supera la verificación del correo sin dificultad
- **Cómo ocurre:**
  1. El atacante abre el formulario de registro del Marketplace e ingresa un correo desechable que controla, el número de teléfono de la víctima y datos personales inventados
  2. clients-api crea el registro pendiente, comprueba que el teléfono no existe (RN-1) y envía el código al teléfono de la víctima; el atacante no lo recibe
  3. El atacante verifica el correo con el código que llega a su buzón desechable
  4. Con un proxy de interceptación captura la petición de verificación del teléfono y la repite de forma automatizada contra el endpoint de verificación de clients-api, recorriendo en orden todo el espacio de códigos posibles dentro de la ventana de validez
  5. clients-api acepta el código correcto en alguna de las peticiones y marca el teléfono como verificado, porque no bloquea tras intentos fallidos
  6. El atacante inicia sesión con la cuenta recién verificada, que queda asociada al teléfono de la víctima, y edita el perfil y las direcciones
- **Vector práctico:** Acción: repetir de forma automatizada las peticiones de verificación del teléfono hasta acertar el código, sin que el endpoint limite los intentos. Herramienta: proxy de interceptación con repetición automatizada de solicitudes sobre el endpoint de verificación expuesto por el Marketplace hacia clients-api. Dato manipulado: el valor del campo del código de un solo uso, enviado junto con el identificador del registro pendiente asociado al teléfono de la víctima.
- **Impacto:** El atacante obtiene una cuenta con el teléfono de la víctima marcado como verificado. Puede hacer pedidos con ese contacto y la víctima recibe notificaciones que no solicitó. Cuando la víctima intenta registrarse, clients-api rechaza el alta por duplicado (RN-1), con riesgo de fraude y daño reputacional para la plataforma.
- **Riesgo:** medio (2×2). La fuerza bruta sobre un OTP corto sin límite de intentos es técnicamente simple, pero exige conocer el teléfono de una víctima sin cuenta; el impacto es medio: cuenta fraudulenta y bloqueo del registro de la víctima.
- **Controles:**
  - *preventivo* (ecommerce): Limitar a 3 a 5 los intentos de verificación del OTP por registro pendiente y por teléfono, invalidando el código y exigiendo uno nuevo tras superar el límite, con un bloqueo por origen y dispositivo además del de registro.
  - *preventivo* (ecommerce): Reducir la validez del OTP a 5 minutos o menos, usar un código de al menos 6 dígitos generado con un CSPRNG, ligarlo al registro pendiente, de un solo uso, y limitar los reenvíos de SMS por teléfono.
  - *preventivo* (ecommerce): Exigir que la verificación de correo y teléfono sea secuencial y esté vinculada a la misma sesión de registro, y no activar la cuenta hasta completar ambas.
  - *detectivo* (ecommerce): Alertar por alto volumen de verificaciones fallidas contra un mismo registro pendiente o teléfono y por registros pendientes con correo desechable y teléfono ya objeto de muchos intentos.
  - *correctivo* (ecommerce): Anular cuentas verificadas tras una ráfaga de intentos fallidos, liberar el teléfono para que su titular real se registre y ofrecer un canal de reclamación de identificadores secuestrados.
- **Referencias y patrones:** OWASP API2:2023 Broken Authentication, OWASP API4:2023 Unrestricted Resource Consumption, CAPEC-49 Password Brute Forcing, FE-03

### UC-02 Selección del producto y carrito

<a id="av-0017"></a>
#### AV-0017 · Manipulación de precio, cantidad o variante en la petición del carrito

- **ID de origen:** AC-UC02-01 · **Ejecución:** Lote 1 · **Tema de riesgo:** R2
- **STRIDE:** T (E) — Manipulación
- **Actor:** Cliente con cuenta que usa un proxy de interceptación (externo)
- **Elementos del DFD:** F1, F2, Marketplace, LC-1 · **Límites:** LC-1
- **Precondiciones:**
  - El cliente puede abrir la ficha de un producto voluminoso y agregarlo al carrito con cuenta propia
  - El Marketplace acepta del navegador campos de precio, subtotal o variante junto con el identificador del producto, o confía en ellos al calcular el subtotal
  - No hay una regla de negocio que limite cantidad o precio mínimo en el carrito
- **Cómo ocurre:**
  1. El cliente abre la ficha del producto voluminoso y agrega una unidad al carrito con un proxy de interceptación activo entre su navegador y el Marketplace
  2. Intercepta la petición de alta al carrito, que cruza LC-1 por F1, y ubica los campos de precio unitario, cantidad y variante
  3. Reemplaza el precio por un valor menor, o asocia el identificador de una variante barata con el producto de una variante cara, o usa una cantidad negativa o cero que reduce el subtotal
  4. El Marketplace recalcula el subtotal con esos datos y devuelve por F2 un carrito con totales alterados
  5. El cliente avanza al pago y, si el Marketplace no recalcula los montos con el catálogo en el servidor, la orden se crea con el total manipulado y se asigna a logística
- **Vector práctico:** El cliente usa un proxy de interceptación sobre la petición de agregar al carrito y modifica los campos de precio unitario, cantidad y variante que el Marketplace toma como válidos. Dato manipulado: precio y relación variante-producto en el cuerpo de la petición de F1. El fallo radica en que el servidor no vuelve a consultar el catálogo para fijar el precio.
- **Impacto:** Venta de productos voluminosos por debajo de su precio, con pérdida económica directa y órdenes con totales que no coinciden con el catálogo. El almacén y la logística ejecutan preparación y envío con costos reales sobre una venta subvaluada, y la reconciliación contable queda inconsistente.
- **Riesgo:** alto (3×3). Interceptar y alterar peticiones del carrito con un proxy es trivial para cualquier cliente con cuenta, y si el servidor confía en el precio recibido cada venta se subvalora con pérdida económica directa y envíos reales a costo del ecommerce.
- **Controles:**
  - *preventivo* (ecommerce): En F1 el Marketplace acepta solo identificador de producto, identificador de variante y cantidad. Ignora y rechaza cualquier campo de precio o subtotal enviado por el navegador. Consulta el precio y la relación variante-producto en el catálogo del servidor en cada alta, cada actualización del carrito y al crear la orden, y recalcula subtotal, envío y total en el servidor.
  - *preventivo* (ecommerce): Validar el esquema de la petición de carrito: cantidad entera mayor que 0 y con tope máximo por producto voluminoso, variante que pertenezca al producto indicado, y rechazo de propiedades no esperadas (mass assignment) con error 400.
  - *preventivo* (pasarela de pago): Al iniciar el cobro, la pasarela de pago recibe el monto calculado por el servidor del ecommerce, y el ecommerce verifica que el monto autorizado coincida con el total recalculado antes de confirmar la orden.
  - *detectivo* (ecommerce): Conciliación automática al crear cada orden: comparar el total con la suma de precios vigentes del catálogo y con el monto autorizado por la pasarela. Alertar y retener la orden si hay diferencia, y registrar en bitácora las peticiones rechazadas por campos de precio o cantidades inválidas, agrupadas por cuenta.
  - *correctivo* (ecommerce): Retener las órdenes marcadas con total inconsistente antes de su asignación a logística, cancelarlas o recalcularlas con el precio correcto y notificar al cliente. Si ya se despacharon, notificar al proveedor logístico para detener el envío. Suspender la cuenta reincidente.
  - *correctivo* (proveedor logístico): Detener la recolección o el despacho de órdenes voluminosas cuando el ecommerce notifique que la orden fue retenida por inconsistencia de total, y devolver el producto al almacén.
- **Referencias y patrones:** CAPEC-39, CAPEC-202, OWASP API3:2023 Broken Object Property Level Authorization, FE-13

<a id="av-0018"></a>
#### AV-0018 · Denegación de inventario con carritos o reservas masivas de productos voluminosos

- **ID de origen:** AC-UC02-02 · **Ejecución:** Lote 1 · **Tema de riesgo:** R8
- **STRIDE:** D (T) — Denegación de servicio
- **Actor:** Atacante o competidor con cuentas de cliente automatizadas (externo)
- **Elementos del DFD:** F1, F2, Marketplace, LC-1 · **Límites:** LC-1
- **Precondiciones:**
  - El Marketplace reserva o descuenta disponibilidad al agregar al carrito, o muestra agotado según carritos activos
  - No existe límite por cuenta, dirección IP o dispositivo en cantidad por producto ni caducidad corta de la reserva
  - El producto voluminoso tiene stock reducido y alta demanda
- **Cómo ocurre:**
  1. El atacante crea o compra varias cuentas de cliente y automatiza con un script de navegador la sesión de cada una
  2. Cada cuenta busca el mismo producto voluminoso y lo agrega al carrito con la cantidad máxima aceptada, por F1
  3. El Marketplace marca como no disponible el stock retenido en esos carritos y lo comunica en F2 a los demás clientes
  4. El atacante renueva periódicamente los carritos antes de que caduquen la reserva y nunca avanza al pago
  5. Los clientes legítimos ven el producto agotado o no pueden agregar la cantidad que necesitan y compran con la competencia
- **Vector práctico:** Un script automatizado sobre cuentas de cliente envía repetidamente la acción de agregar al carrito con la cantidad máxima de un producto voluminoso concreto y la renueva antes de que caduque la reserva. Dato manipulado: cantidad y disponibilidad del producto retenida por carritos que nunca se pagan.
- **Impacto:** El producto aparece agotado para clientes legítimos, con pérdida de ventas y de ingresos y daño a la confianza en la disponibilidad real. El atacante puede ser un competidor, y los datos de disponibilidad dejan de reflejar la demanda real.
- **Riesgo:** medio (2×2). Automatizar carritos con cuentas desechables es sencillo y afecta productos con poco stock y alta demanda, pero el daño es una pérdida de ventas temporal y reversible si se liberan las reservas.
- **Controles:**
  - *preventivo* (ecommerce): Reservar stock solo con caducidad corta (por ejemplo 15 minutos) que no se renueve automáticamente al volver a agregar el mismo producto. Descontar stock definitivo solo al confirmar el pago, o, si hay reserva en el carrito, limitar la fracción del stock de un producto voluminoso que pueden retener los carritos sin pagar.
  - *preventivo* (ecommerce): Limitar por cuenta, dispositivo e IP la cantidad máxima por producto voluminoso y el número de carritos con reserva activa, y aplicar protección anti-automatización (desafío CAPTCHA o similar, huella de dispositivo) al agregar al carrito cuando el comportamiento sea anómalo.
  - *detectivo* (ecommerce): Monitorear la razón entre unidades reservadas en carritos y unidades pagadas por producto, cuentas con muchos carritos que nunca llegan al pago, renovaciones periódicas y ráfagas de altas de cuentas o de peticiones de carrito. Alertar al superar umbrales sobre productos con stock bajo.
  - *correctivo* (ecommerce): Liberar de inmediato las reservas de las cuentas señaladas, bloquear temporalmente a esas cuentas, dispositivos e IP, restituir la disponibilidad real del producto y ajustar los umbrales de reserva según el incidente.
- **Referencias y patrones:** OWASP OAT-021 Denial of Inventory, CAPEC-125, OAT-021, AV-0008

<a id="av-0019"></a>
#### AV-0019 · Sondeo de disponibilidad con cuenta de cliente para reconstruir el stock exacto por variante y tienda

- **ID de origen:** AC-UC02-03 · **Ejecución:** Lote 1 · **Tema de riesgo:** R7
- **STRIDE:** I (D) — Divulgación de información
- **Actor:** Competidor o revendedor que usa una o varias cuentas de cliente registradas para hacer scraping del carrito (externo)
- **Elementos del DFD:** F1, F2, Marketplace, LC-1 · **Límites:** LC-1
- **Precondiciones:**
  - El atacante dispone de una o más cuentas de cliente registradas y con sesión iniciada, porque agregar productos al carrito en UC-02 exige cuenta
  - El carrito o la ficha muestran en F2 el stock exacto, el tope de unidades o un mensaje de disponibilidad por variante y por tienda
  - El Marketplace no limita la tasa de operaciones de carrito por cuenta, por dispositivo ni por dirección IP
- **Cómo ocurre:**
  1. El atacante inicia sesión con una o varias cuentas de cliente y obtiene las sesiones que el rastreador reutilizará
  2. Un rastreador automatizado recorre los identificadores de producto y de variante de los productos voluminosos del catálogo
  3. Para cada variante, el rastreador agrega al carrito cantidades crecientes por F1 y lee en la respuesta de F2 el mensaje de disponibilidad o el tope máximo de unidades aceptado
  4. Repite el sondeo a intervalos regulares y con varias cuentas para esquivar bloqueos por cuenta, y registra el stock exacto por variante y tienda
  5. Con las series de datos reconstruye la rotación y las reposiciones, y fija sus precios, anticipa reposiciones o elige productos con poco stock para otros abusos
- **Vector práctico:** Acción: agregar al carrito cantidades crecientes de cada variante y leer el límite que devuelve el Marketplace. Herramienta: rastreador automatizado con sesiones de cuentas de cliente registradas. Dato manipulado: el parámetro de cantidad de la petición de carrito (F1). Dato obtenido: el stock exacto por variante y tienda que la respuesta de F2 expone mediante el mensaje de disponibilidad o el tope de unidades.
- **Impacto:** Fuga de información comercial sensible sobre niveles de inventario por variante y tienda, y sobre su rotación y reposición. Beneficia a competidores y permite planear abusos dirigidos, como inmovilizar variantes con poco stock. El precio no se considera confidencial porque la ficha ya lo muestra a cualquier cliente. Las operaciones masivas de carrito también generan carga innecesaria sobre el Marketplace.
- **Riesgo:** medio (2×2). El sondeo automatizado con cuentas registradas es factible si no hay límite de tasa y filtra información comercial sensible, pero no expone datos personales ni causa pérdida directa por sí solo.
- **Controles:**
  - *preventivo* (ecommerce): No exponer en F2 el stock exacto ni el tope de unidades por variante y tienda: mostrar solo estados genéricos (disponible, pocas unidades, agotado) y devolver el mismo mensaje de error cuando la cantidad pedida supere el stock, sin revelar el límite numérico.
  - *preventivo* (ecommerce): Aplicar límite de tasa a las operaciones de carrito por cuenta, dispositivo e IP, con tope de variaciones de cantidad sobre la misma variante por sesión, y exigir desafío anti-automatización cuando se detecten recorridos secuenciales de identificadores de producto o variante.
  - *detectivo* (ecommerce): Detectar patrones de sondeo: cuentas que agregan cantidades crecientes a muchas variantes sin llegar al pago, recorrido secuencial de identificadores, uso de varias cuentas desde el mismo dispositivo o IP, y volumen de peticiones de carrito anómalo frente a la línea base. Generar alertas y revisarlas.
  - *correctivo* (ecommerce): Bloquear o limitar de forma progresiva las cuentas, dispositivos e IP identificados como rastreadores, invalidar sus sesiones y revisar la bitácora para estimar qué datos de inventario se pudieron reconstruir, ajustando los mensajes de disponibilidad expuestos.
- **Referencias y patrones:** OWASP OAT-011 Scraping, OWASP API4:2023 Unrestricted Resource Consumption, CAPEC-202 Create Malicious Client, OAT-011, FE-13

### UC-03 Captura de datos de envío y contacto

<a id="av-0020"></a>
#### AV-0020 · Alteración del código postal y las coordenadas enviados a delivery-api para abaratar el envío o forzar la cobertura

- **ID de origen:** AC-UC03-01 · **Ejecución:** Lote 1 · **Tema de riesgo:** R2
- **STRIDE:** T (E) — Manipulación
- **Actor:** Cliente (externo)
- **Elementos del DFD:** F5, Marketplace, delivery-api · **Límites:** LC-1, LC-2
- **Precondiciones:**
  - El cliente tiene una cuenta y un producto voluminoso en el carrito
  - La cotización y la cobertura se calculan con el código postal o las coordenadas que llegan en la petición del navegador
  - delivery-api no contrasta esos datos con la dirección normalizada y guardada en clients-api (S-10)
- **Cómo ocurre:**
  1. El cliente captura una dirección real de una zona de alto costo o sin cobertura
  2. Antes de que la petición llegue al Marketplace, la intercepta con un proxy de depuración (Burp Suite)
  3. Sustituye el código postal y las coordenadas por los de una zona cercana a la tienda, con tarifa baja y cobertura
  4. delivery-api calcula costo y cobertura con los datos alterados y devuelve la cotización favorable
  5. El cliente completa el pago y la orden se registra con la dirección textual real y el costo del código postal falso
- **Vector práctico:** Con un proxy de interceptación en su navegador, el cliente modifica los campos de código postal y coordenadas de la solicitud de cotización (F5) para que no correspondan con la dirección textual de entrega, y obtiene una tarifa menor o una cobertura que no le corresponde.
- **Impacto:** Pérdida económica por envíos subcotizados, pedidos fuera de zona de cobertura que generan fallos de entrega y devoluciones, e incumplimiento de RN-2 en el cálculo del costo.
- **Riesgo:** medio (2×2). Manipular campos con un proxy es trivial y S-10 indica que delivery-api confía en la zona enviada, pero la pérdida se limita al diferencial de tarifa por orden.
- **Controles:**
  - *preventivo* (ecommerce): Que el Marketplace ignore el código postal y las coordenadas del navegador y los derive en servidor de la dirección normalizada y guardada en clients-api, enviando a delivery-api solo el identificador de dirección verificado para cotizar (F5).
  - *preventivo* (ecommerce): Que delivery-api valide que el código postal y las coordenadas recibidos correspondan a la dirección textual mediante geocodificación inversa y rechace la cotización si la distancia entre ambos supera un umbral.
  - *detectivo* (ecommerce): Alertar sobre órdenes cuyo código postal cotizado difiera del código postal de la dirección textual registrada, y sobre clientes con discrepancias repetidas.
  - *correctivo* (ecommerce): Recalcular el costo de envío con la dirección real antes del despacho, cobrar el diferencial o cancelar la orden fuera de cobertura (RN-2), y marcar la cuenta para revisión.
  - *detectivo* (proveedor logístico): Cuando el repartidor detecte que la dirección de entrega queda fuera de la zona cotizada, registrarlo como incidencia y reportarlo al ecommerce para conciliar el costo.
- **Referencias y patrones:** CAPEC-277, OWASP API3:2023, AV-0003

<a id="av-0021"></a>
#### AV-0021 · Lectura de direcciones guardadas, nombres y teléfonos de otros clientes cambiando el identificador en clients-api

- **ID de origen:** AC-UC03-02 · **Ejecución:** Lote 1 · **Tema de riesgo:** R7
- **STRIDE:** I (E) — Divulgación de información
- **Actor:** Cliente autenticado con cuenta propia (externo)
- **Elementos del DFD:** Marketplace, clients-api · **Límites:** LC-1, LC-2
- **Precondiciones:**
  - El cliente puede iniciar sesión y abrir el paso de dirección guardada durante el pago
  - La consulta de direcciones y contactos de clients-api recibe un identificador de dirección o de cliente en la petición
  - clients-api no verifica que el objeto consultado pertenezca a la sesión que lo pide (S-09)
- **Cómo ocurre:**
  1. El cliente abre el paso de selección de dirección y observa en las herramientas del navegador la petición que trae sus direcciones guardadas
  2. La reenvía con Burp Repeater cambiando el identificador de dirección o de cliente por valores consecutivos o inferidos
  3. clients-api devuelve direcciones completas, coordenadas, nombre y teléfono de contacto de otras cuentas
  4. El atacante automatiza la iteración sobre el rango de identificadores y conserva los resultados
  5. Con los datos arma una base de domicilios y teléfonos de clientes que compraron productos de alto valor
- **Vector práctico:** Con un proxy de repetición de peticiones, el cliente cambia el identificador del objeto dirección o cliente en la consulta de direcciones guardadas y recorre el rango de valores para extraer nombre, teléfono y domicilio de terceros.
- **Impacto:** Divulgación masiva de datos personales (domicilio, teléfono, nombre), riesgo de acoso y de robo dirigido a domicilios con compras de alto valor, y exposición regulatoria por protección de datos.
- **Riesgo:** alto (2×3). S-09 deja sin confirmar la autorización por objeto y los identificadores son predecibles, lo que permite extracción masiva de domicilios y teléfonos con impacto regulatorio y de seguridad física.
- **Controles:**
  - *preventivo* (ecommerce): Autorización a nivel de objeto en clients-api: toda consulta de dirección o contacto debe comprobar que el objeto pertenece al cliente de la sesión autenticada, y el identificador de cliente se toma del token y no de la petición.
  - *preventivo* (ecommerce): Reemplazar los identificadores secuenciales de direcciones por UUID aleatorios y devolver una respuesta uniforme 404 cuando el objeto no pertenezca al solicitante.
  - *detectivo* (ecommerce): Alertar cuando una misma sesión o IP consulte muchos identificadores de dirección distintos o acumule respuestas 403/404 en clients-api, y limitar la frecuencia por cuenta.
  - *correctivo* (ecommerce): Ante un acceso indebido confirmado, bloquear la cuenta y las sesiones del atacante, identificar los registros expuestos, notificar a los titulares y a la autoridad de protección de datos, y añadir pruebas automáticas de BOLA al pipeline.
- **Referencias y patrones:** OWASP API1:2023 BOLA, OWASP API3:2023, FE-11

<a id="av-0022"></a>
#### AV-0022 · Cliente que niega haber capturado la dirección y el contacto de la orden para reclamar la entrega fallida

- **ID de origen:** AC-UC03-06 · **Ejecución:** Lote 1 · **Tema de riesgo:** R1
- **STRIDE:** R (S) — Repudio
- **Actor:** Cliente (externo)
- **Elementos del DFD:** Marketplace, clients-api, delivery-api · **Límites:** LC-1, LC-2
- **Precondiciones:**
  - La orden guarda una referencia a la dirección editable y no una copia inmutable con fecha, IP y dispositivo desde el que se confirmó
  - No hay confirmación explícita del cliente sobre la dirección y el contacto finales antes del pago
  - Las disputas se resuelven con el soporte del Marketplace revisando el estado actual de la cuenta
- **Cómo ocurre:**
  1. El cliente compra un producto de alto valor y captura una dirección y un teléfono de un tercero, o los de un domicilio sin vigilancia
  2. Tras el intento de entrega o la entrega a esa dirección, edita o borra la dirección guardada en su perfil
  3. Abre un reclamo en el que afirma que nunca indicó esa dirección ni ese contacto y que la orden fue manipulada
  4. Soporte no encuentra una prueba firmada de lo capturado durante el pago y no puede refutar la afirmación
  5. Se aprueba el reembolso o el reenvío y el cliente conserva el producto
- **Vector práctico:** Desde su perfil en el Marketplace, el cliente edita o elimina la dirección y el contacto guardados después del pago y presenta un reclamo por soporte en el que niega haberlos capturado, apoyándose en que la orden no conserva una copia inmutable con evidencia de la confirmación.
- **Impacto:** Fraude por reembolso o reenvío, pérdida del producto y costo de envío, e imposibilidad de atribuir al cliente la dirección y el contacto de la orden en las disputas.
- **Riesgo:** medio (2×2). La orden guarda una referencia editable a la dirección sin evidencia de confirmación, lo que facilita reclamos falsos, aunque el daño se limita al valor de cada orden.
- **Controles:**
  - *preventivo* (ecommerce): Guardar en la orden una copia inmutable de la dirección y del contacto confirmados, con marca de tiempo, IP, dispositivo y hash, y exigir una confirmación explícita del cliente antes del pago.
  - *preventivo* (proveedor logístico): Exigir código de confirmación al recibir y foto de entrega con marca de tiempo y geolocalización, y entregarlos al ecommerce como evidencia de la entrega a la dirección confirmada.
  - *detectivo* (ecommerce): Alertar cuando una dirección se edite o elimine tras el pago o tras un intento de entrega, y cuando un cliente acumule reclamos por dirección o contacto desconocidos, cruzando historial por cliente, dirección y medio de pago.
  - *correctivo* (ecommerce): Resolver las disputas con el registro inmutable y la evidencia de entrega, rechazar el reembolso cuando coincidan con lo reclamado y limitar los reembolsos o reenvíos futuros de cuentas con reclamos repetidos.
- **Referencias y patrones:** FE-01

<a id="av-0023"></a>
#### AV-0023 · Cuenta tomada que agrega una dirección nueva y un contacto falsos durante el pago para desviar la compra

- **ID de origen:** AC-UC03-03 · **Ejecución:** Lote 1 · **Tema de riesgo:** R5
- **STRIDE:** S (T) — Suplantación
- **Actor:** Atacante con credenciales filtradas del cliente (externo)
- **Elementos del DFD:** Marketplace, clients-api, delivery-api, F5 · **Límites:** LC-1, LC-2
- **Precondiciones:**
  - El atacante tiene credenciales del cliente obtenidas de otra filtración y el inicio de sesión no exige un segundo factor
  - La cuenta tiene un medio de pago tokenizado guardado
  - Agregar una dirección nueva y un teléfono de contacto durante el pago no exige reautenticación ni genera aviso al titular
- **Cómo ocurre:**
  1. El atacante prueba las credenciales filtradas con una herramienta de relleno de credenciales contra el inicio de sesión del Marketplace y entra a la cuenta
  2. Agrega un producto de alto valor al carrito y llega al paso de datos de envío de UC-03
  3. Captura como dirección nueva un domicilio de paso o un punto de reexpedición controlado por él, con un nombre y un teléfono de contacto propios
  4. clients-api guarda la dirección y el contacto en el perfil, y el Marketplace envía la dirección a delivery-api (F5), que valida la cobertura y calcula el costo
  5. Paga con el medio de pago guardado y la orden de entrega se genera hacia la dirección del atacante sin que el titular reciba ninguna notificación
- **Vector práctico:** Con credenciales reutilizadas y una herramienta de relleno de credenciales, el atacante inicia sesión y, desde el formulario normal de envío del Marketplace, registra una dirección y un teléfono de contacto propios (datos manipulados: dirección de entrega y contacto de la orden). Con ellos compra con el medio de pago tokenizado de la víctima. Se diferencia de AV-0009 (UC-12), donde el atacante registra una persona autorizada para retirar en tienda. Aquí el dato suplantado es la dirección y el contacto de envío capturados en el pago (UC-03), y el producto se desvía por entrega a domicilio sin que intervenga ninguna persona autorizada ni un código de retiro.
- **Impacto:** Compra fraudulenta con cargo al titular, contracargos, pérdida del producto y exposición de las direcciones y los contactos guardados en la cuenta comprometida.
- **Riesgo:** alto (3×2). El relleno de credenciales es frecuente y no hay segundo factor ni aviso por direcciones nuevas; el daño es por orden fraudulenta (contracargo y producto perdido), aunque escalable.
- **Controles:**
  - *preventivo* (ecommerce): Exigir reautenticación o segundo factor al agregar una dirección o teléfono nuevos durante el pago, y MFA o verificación de riesgo en el inicio de sesión desde dispositivo o país nuevo, con protección contra relleno de credenciales (límites por IP, dispositivo y bot detection).
  - *preventivo* (pasarela de pago): Exigir autenticación reforzada (3-D Secure) del titular cuando se paga con un token guardado y la dirección de envío es nueva para esa cuenta.
  - *detectivo* (ecommerce): Reglas de riesgo que marquen órdenes de alto valor con dirección y teléfono nuevos tras un inicio de sesión desde un dispositivo nuevo, y detectar ráfagas de inicios fallidos contra muchas cuentas.
  - *detectivo* (ecommerce): Enviar al titular una notificación por correo o SMS ante cada dirección o contacto nuevos y retener la orden unos minutos para permitir cancelarla.
  - *correctivo* (ecommerce): Cancelar o retener el despacho de órdenes marcadas, restablecer credenciales y revocar sesiones de la cuenta, y gestionar el contracargo con la evidencia del dispositivo y la dirección.
- **Referencias y patrones:** OWASP API2:2023 Broken Authentication, CAPEC-49 Password Brute Forcing (relleno de credenciales), FE-11, AV-0009

<a id="av-0024"></a>
#### AV-0024 · Texto malicioso en nombre de contacto y referencias de entrega que se ejecuta con la sesión privilegiada de un empleado en un panel interno

- **ID de origen:** AC-UC03-05 · **Ejecución:** Lote 1 · **Tema de riesgo:** R7
- **STRIDE:** E (T, I) — Elevación de privilegios
- **Actor:** Cliente malintencionado (externo)
- **Elementos del DFD:** Marketplace, clients-api, delivery-api, F5 · **Límites:** LC-1, LC-2
- **Precondiciones:**
  - Los campos de nombre de contacto, calle y referencias de entrega aceptan texto libre sin validar longitud ni caracteres
  - Algún panel interno que consume los datos de la orden desde delivery-api (por ejemplo, soporte o preparación de pedidos) los muestra sin codificar
  - Ese panel se usa con sesiones de empleados con privilegios elevados sobre órdenes de otros clientes
- **Cómo ocurre:**
  1. El cliente captura una dirección nueva y, en nombre de contacto y en referencias de entrega, escribe una cadena con una etiqueta de script incrustada en lugar de datos reales
  2. El Marketplace envía la dirección a delivery-api (F5), clients-api guarda el perfil con ese texto sin alterarlo y la orden de entrega lo conserva igual
  3. Un agente de soporte o un operador abre la orden en su panel interno y el navegador interpreta el texto como código
  4. El script corre con la sesión del empleado: consulta órdenes de otros clientes que ese empleado puede ver y envía su contenido a un dominio controlado por el atacante
  5. El atacante recibe nombres, teléfonos y direcciones de terceros, o consigue que se ejecuten acciones sobre pedidos ajenos con los permisos del empleado
- **Vector práctico:** El cliente usa el formulario normal de dirección del Marketplace desde su navegador, sin herramientas especiales. Guarda en los campos de nombre de contacto y referencias de entrega una cadena con una etiqueta de script incrustada. Esa cadena, al renderizarse en el panel interno, lee las órdenes ajenas visibles para el empleado y las envía a un dominio del atacante. El dato manipulado es el texto libre de la dirección y del contacto, que cruza LC-1 y LC-2 sin saneamiento. Se clasifica como elevación de privilegios porque el texto del cliente termina ejecutándose con la autoridad de la sesión del empleado, y la divulgación de datos de otras órdenes es consecuencia de eso.
- **Impacto:** Divulgación de datos personales y de entrega de otros clientes, acciones no autorizadas sobre pedidos y reembolsos con los permisos del empleado, y pérdida de confianza entre clientes, soporte y logística.
- **Riesgo:** alto (2×3). Los campos de texto libre llegan sin sanear a paneles internos con sesiones privilegiadas, y una ejecución exitosa expone datos de muchos clientes y permite acciones con permisos de empleado.
- **Controles:**
  - *preventivo* (ecommerce): Validar en servidor longitud y juego de caracteres de nombre, calle y referencias de entrega en el Marketplace y en clients-api, y codificar por contexto toda salida en los paneles internos de soporte y preparación de pedidos, sin renderizar HTML crudo.
  - *preventivo* (ecommerce): Aplicar una Content-Security-Policy estricta y cookies HttpOnly y SameSite en los paneles internos, para que un script inyectado no lea la sesión ni envíe datos a dominios externos.
  - *detectivo* (ecommerce): Registrar y alertar sobre direcciones o contactos con etiquetas HTML o patrones de script, y reportes CSP de violaciones y de conexiones salientes a dominios no autorizados desde los paneles.
  - *correctivo* (ecommerce): Ante una ejecución confirmada, sanear o eliminar los registros afectados, revocar las sesiones del empleado, revisar el acceso a órdenes ajenas y notificar a los titulares expuestos.
- **Referencias y patrones:** CAPEC-63 Cross-Site Scripting (XSS), OWASP Top 10 2021 A03 Injection

### UC-04 Aplicación de cupón de descuento

<a id="av-0025"></a>
#### AV-0025 · Enumeración automatizada de códigos de cupón para obtener descuentos no asignados

- **ID de origen:** AC-UC04-01 · **Ejecución:** Lote 1 · **Tema de riesgo:** R8
- **STRIDE:** I (E) — Divulgación de información
- **Actor:** Atacante externo con automatización y cuenta de cliente (externo)
- **Elementos del DFD:** F4, Marketplace, cupons-api, F12 · **Límites:** LC-1, LC-2
- **Precondiciones:**
  - Los códigos de cupón siguen un patrón corto o predecible (prefijo de campaña más número consecutivo).
  - La validación de cupón en checkout no limita los intentos fallidos por cuenta, IP o dispositivo.
  - El atacante tiene una cuenta de cliente válida y un carrito que cumple el monto mínimo.
  - Algunos cupones no están ligados a la cuenta destinataria, o su segmento es amplio.
- **Cómo ocurre:**
  1. El atacante observa un cupón legítimo recibido por correo o publicado en una campaña y deduce la estructura del código (prefijo de campaña y secuencia).
  2. Captura con un proxy de interceptación la petición de validación del Marketplace a cupons-api (F4), que lleva código, cliente y carrito.
  3. Automatiza con una herramienta de repetición de peticiones la variación del sufijo del código sobre esa petición, desde varias IP.
  4. Distingue por la respuesta de cupons-api los códigos válidos de los inválidos y registra los válidos, incluidos los de alto valor o de otros segmentos.
  5. Usa los códigos en sus propias órdenes, o los revende a otros clientes, y cada uso se consume al confirmar el pago.
- **Vector práctico:** Un script con una herramienta de repetición de peticiones, apoyado en un proxy de interceptación, manipula el campo código de cupón en la validación del checkout (F4) y lee las diferencias en la respuesta de cupons-api para identificar códigos válidos no otorgados.
- **Impacto:** Pérdida de margen por descuentos otorgados a quien no era destinatario, agotamiento del presupuesto de campañas, reventa de códigos y sobrecarga de cupons-api por validaciones masivas.
- **Riesgo:** medio (2×2). Un script con una cuenta válida puede probar sufijos si los códigos son predecibles y no hay límite de intentos, pero cada descuento obtenido es acotado y se puede cortar al detectarlo.
- **Controles:**
  - *preventivo* (ecommerce): Generar los códigos de cupón nuevos con al menos 10 caracteres aleatorios criptográficamente seguros, sin prefijo de campaña ni secuencia, y ligar a la cuenta destinataria los cupones personales o de segmento pequeño para que cupons-api rechace su uso por otras cuentas.
  - *preventivo* (ecommerce): Limitar en cupons-api los intentos de validación fallidos por cuenta, IP y dispositivo (por ejemplo 5 por 10 minutos), con retraso progresivo y CAPTCHA o desafío anti-bot en el checkout tras superar el umbral.
  - *preventivo* (ecommerce): Devolver la misma respuesta genérica y con tiempo similar para códigos inexistentes, vencidos o no elegibles, de modo que la respuesta de F4 no permita distinguir códigos válidos de inválidos.
  - *detectivo* (ecommerce): Alertar cuando una cuenta, IP o dispositivo acumule muchas validaciones fallidas, y cuando un cupón personal sea canjeado por una cuenta distinta a la destinataria. Revisar las alertas en el SOC.
  - *correctivo* (ecommerce): Bloquear temporalmente las cuentas y dispositivos implicados, invalidar y reemplazar los códigos que se hayan enumerado y revisar o revertir las órdenes que los usaron antes del despacho.
- **Referencias y patrones:** OWASP OAT-002 Token Cracking, CAPEC-112 Brute Force, OWASP API6:2023 Unrestricted Access to Sensitive Business Flows, FE-04

<a id="av-0026"></a>
#### AV-0026 · Uso simultáneo de un cupón de un solo uso en varias órdenes antes de que se consuma

- **ID de origen:** AC-UC04-02 · **Ejecución:** Lote 1 · **Tema de riesgo:** R2
- **STRIDE:** T (E) — Manipulación
- **Actor:** Cliente con un cupón de un solo uso o de usos limitados (externo)
- **Elementos del DFD:** F4, F12, cupons-api, Marketplace · **Límites:** LC-1, LC-2
- **Precondiciones:**
  - El cliente posee un cupón válido de un solo uso o con pocos usos por cliente.
  - El uso del cupón se consume al confirmar el pago (paso 4), no al validarlo.
  - No hay reserva atómica ni restricción única que ligue el cupón a una orden antes del cobro.
  - El cliente puede abrir varias sesiones de checkout con carritos distintos.
- **Cómo ocurre:**
  1. El cliente prepara varios carritos en sesiones paralelas del Marketplace y aplica el mismo cupón en cada uno; cupons-api responde que es válido en todos porque aún figura sin usar.
  2. Con una herramienta de envío de peticiones concurrentes, lanza casi a la vez las confirmaciones de pago de los carritos hacia la pasarela y el Marketplace.
  3. Cada confirmación llega a cupons-api antes de que el contador de usos se actualice en F12, por lo que todas se aceptan.
  4. El descuento queda aplicado en todas las órdenes y se crean las órdenes de entrega en delivery-api.
  5. El cliente repite la maniobra en cada campaña que tenga cupones de un solo uso.
- **Vector práctico:** Con una herramienta de peticiones concurrentes o dos o más pestañas sincronizadas, el cliente envía en paralelo las confirmaciones de varias órdenes que referencian el mismo código de cupón, aprovechando que la marca de usado se escribe después de la validación.
- **Impacto:** Un cupón de un solo uso se aplica a varias órdenes, con pérdida económica directa en descuentos, incumplimiento de las reglas de RN-4 y consumo del presupuesto de campaña por encima de lo aprobado.
- **Riesgo:** medio (2×2). La condición de carrera se explota con peticiones concurrentes simples porque el uso se consume tras el pago, y la pérdida es directa por cupón pero limitada a cupones de un solo uso.
- **Controles:**
  - *preventivo* (ecommerce): Reservar el cupón de forma atómica en cupons-api al iniciar la confirmación de la orden, con restricción única sobre cupón y orden (o cupón y cliente) o con bloqueo transaccional, y consumirlo definitivamente solo cuando el pago quede confirmado.
  - *preventivo* (pasarela de pago): Exigir una clave de idempotencia por orden en las peticiones de pago y rechazar confirmaciones duplicadas o concurrentes para la misma intención de pago.
  - *detectivo* (ecommerce): Ejecutar una conciliación periódica y una alerta que detecten cupones de un solo uso asociados a más de una orden confirmada, o con usos que superan el límite de la regla, y revisen cupones aplicados en órdenes con segundos de diferencia.
  - *correctivo* (ecommerce): Cancelar o retener las órdenes excedentes antes del despacho y generar la orden de entrega en delivery-api solo si la reserva del cupón es válida. Liberar las reservas que expiren sin pago para no bloquear a clientes legítimos.
- **Referencias y patrones:** OWASP API6:2023 Unrestricted Access to Sensitive Business Flows, CAPEC-26 Leveraging Race Conditions, FE-13

<a id="av-0027"></a>
#### AV-0027 · Cuentas múltiples para repetir cupones de primera compra o con límite por cliente

- **ID de origen:** AC-UC04-03 · **Ejecución:** Lote 1 · **Tema de riesgo:** R8
- **STRIDE:** S (E) — Suplantación
- **Actor:** Cliente o grupo organizado que crea cuentas desechables (externo)
- **Elementos del DFD:** F4, F12, cupons-api, Marketplace · **Límites:** LC-1, LC-2
- **Precondiciones:**
  - Existe un cupón de primera compra o con límite de usos por cliente.
  - La unicidad del cliente (RN-1) se valida solo por correo y teléfono.
  - El registro permite correos desechables y números virtuales sin protección contra automatización.
  - El historial de uso por cliente se calcula por identificador de cuenta.
- **Cómo ocurre:**
  1. El atacante crea en ráfaga cuentas con correos desechables y números virtuales usando una herramienta de automatización de registro.
  2. Cada cuenta nueva figura sin historial de uso en cupons-api, por lo que cumple la elegibilidad del cupón.
  3. Con cada cuenta arma un carrito sobre el monto mínimo y aplica el mismo cupón; cupons-api valida el límite de usos por cliente contra el historial de esa cuenta (F12).
  4. Paga con el mismo medio de pago o con tarjetas virtuales y recibe todo en la misma dirección de entrega.
  5. El grupo repite el proceso en cada campaña y revende los productos o los usa en reventa.
- **Vector práctico:** Un script de registro automatizado, con correos desechables y números virtuales como dato de identidad, genera cuentas nuevas que eluden RN-1 y reinician el contador de usos por cliente que cupons-api consulta en el historial.
- **Impacto:** El límite por cliente deja de funcionar: se multiplican los descuentos de primera compra, se pierde margen y se distorsionan las métricas de adquisición de las campañas.
- **Riesgo:** alto (3×2). Crear cuentas desechables es barato y común cuando la unicidad solo depende de correo y teléfono, aunque el impacto por cuenta es bajo y acotado al valor del cupón.
- **Controles:**
  - *preventivo* (ecommerce): Aplicar en el registro protección contra automatización (CAPTCHA, límite de altas por IP y dispositivo), bloquear dominios de correo desechable y exigir verificación por código de un teléfono real, rechazando rangos de números virtuales conocidos.
  - *preventivo* (ecommerce): Validar los cupones de primera compra y con límite por cliente contra la huella de dispositivo, la dirección de entrega normalizada y el medio de pago (token o huella de tarjeta), y no solo contra el identificador de cuenta.
  - *preventivo* (pasarela de pago): Proveer una huella estable del instrumento de pago y aplicar verificación 3-D Secure o autenticación reforzada en el primer pago con cupón. Rechazar tarjetas virtuales prepago de alto riesgo según el scoring del emisor.
  - *detectivo* (ecommerce): Alertar cuando varias cuentas compartan dirección de entrega, dispositivo, tarjeta o patrón de correo, o cuando se creen cuentas en ráfagas, y cruzar los canjes de primera compra con esas señales.
  - *correctivo* (ecommerce): Retener para revisión manual las órdenes con cupón de primera compra que coincidan con las señales, cancelar las del grupo detectado antes del despacho, suspender las cuentas vinculadas y añadir sus identificadores a listas de bloqueo.
- **Referencias y patrones:** OWASP API6:2023 Unrestricted Access to Sensitive Business Flows, CAPEC-94 Adversary in the Middle (no aplicable); CAPEC-210 Abuse Existing Functionality, FE-03

<a id="av-0028"></a>
#### AV-0028 · Manipulación del total o de las reglas de elegibilidad en la petición de aplicación del cupón

- **ID de origen:** AC-UC04-04 · **Ejecución:** Lote 1 · **Tema de riesgo:** R2
- **STRIDE:** T (E) — Manipulación
- **Actor:** Cliente que intercepta las peticiones del checkout (externo)
- **Elementos del DFD:** F4, Marketplace, cupons-api, delivery-api · **Límites:** LC-1, LC-2
- **Precondiciones:**
  - El checkout envía a cupons-api o a delivery-api valores como subtotal, costo de envío o destino del descuento (producto o envío) que provienen del cliente.
  - El servidor no recalcula montos ni vuelve a verificar el monto mínimo antes de confirmar el pago.
  - El cliente puede interceptar su propio tráfico con un proxy.
- **Cómo ocurre:**
  1. El cliente arma un carrito con productos de alto valor y aplica un cupón con monto mínimo bajo, o con descuento sobre el envío.
  2. Intercepta con un proxy de interceptación la petición de validación o de cotización (F4) y cambia el subtotal, la cantidad o el costo de envío a valores que cumplen el mínimo o inflan el descuento.
  3. Una vez aceptado el cupón, restaura el carrito real o cambia la cantidad o la modalidad de entrega, de modo que el descuento queda aplicado a una orden que no cumpliría las reglas.
  4. Si el descuento sobre el envío se calcula con un costo enviado por el cliente, el cupón se aplica a un valor alterado.
  5. El Marketplace muestra el total final reducido, el cliente paga y la orden se registra con el descuento indebido.
- **Vector práctico:** Con un proxy de interceptación, el cliente modifica los campos de subtotal, cantidad, costo de envío o modalidad en la petición de aplicación del cupón y en la de confirmación, para que cupons-api valide con datos distintos a los de la orden final.
- **Impacto:** Descuentos superiores a los permitidos, envío gratuito sin derecho a él, órdenes cuyo total no coincide con el catálogo y pérdida de margen por validaciones evadidas.
- **Riesgo:** medio (2×2). Interceptar y alterar peticiones con un proxy es trivial para un cliente, pero el descuento indebido se limita a una orden y desaparece si el servidor recalcula los montos.
- **Controles:**
  - *preventivo* (ecommerce): Recalcular en el servidor subtotal, cantidades, costo de envío y descuento a partir del catálogo y de la cotización almacenada, ignorando cualquier importe enviado por el cliente. Revalidar vigencia, elegibilidad y monto mínimo con el carrito final justo antes de confirmar el pago.
  - *preventivo* (proveedor logístico): Firmar o guardar en servidor la cotización de envío (modalidad, costo, vigencia) y verificar en el pago que la modalidad y el costo coincidan. Si el cliente cambia carrito o modalidad tras aplicar el cupón, revalidar el cupón desde cero.
  - *detectivo* (ecommerce): Comparar el total de cada orden con el recalculado desde catálogo, cupón y envío, y alertar sobre diferencias, sobre cambios de carrito o modalidad entre la validación del cupón y el pago, y sobre descuentos de envío superiores al costo real.
  - *correctivo* (ecommerce): Bloquear la orden cuyo total no coincida y pedir al cliente que confirme el total recalculado. Si el pago ya se hizo, ajustar la diferencia o cancelar y reembolsar antes del despacho.
- **Referencias y patrones:** CAPEC-39 Manipulating Opaque Client-based Data Tokens, OWASP API6:2023, FE-13

<a id="av-0029"></a>
#### AV-0029 · Cupón sin límite creado en UC-15 por un operador interno y canjeado en el checkout de UC-04 por cuentas allegadas

- **ID de origen:** AC-UC04-05 · **Ejecución:** Lote 1 · **Tema de riesgo:** R3
- **STRIDE:** E (T, R) — Elevación de privilegios
- **Actor:** Operador de marketing y promociones con acceso a cupons-frontend (interno)
- **Elementos del DFD:** cupons-frontend, cupons-api, F12, F4, Marketplace · **Límites:** LC-3, LC-2
- **Precondiciones:**
  - El operador está autenticado en cupons-frontend y puede crear o editar cupones, como describe UC-15, el caso de uso donde nace el abuso.
  - Según S-11, las reglas del cupón (valor, vigencia, usos totales, usos por cliente, monto mínimo y segmento) las define el empleado en cupons-frontend y las valida cupons-api. Por eso cualquier regla alterada en origen se acepta como legítima en el checkout de UC-04.
  - Supuesto nuevo: no hay aprobación de una segunda persona para cupones de alto descuento o sin límite de usos, ni topes de descuento por rol.
  - Supuesto nuevo: no hay alertas por uso concentrado de un cupón ni una bitácora inmutable que atribuya los cambios al operador.
- **Cómo ocurre:**
  1. En cupons-frontend (UC-15, LC-3) el operador crea un cupón con descuento alto, sin límite de usos totales y con segmento amplio. También puede ampliar la vigencia de un cupón existente o quitarle el monto mínimo.
  2. El operador activa el cupón y cupons-api lo guarda en el almacén de cupones y usos (F12) como disponible para validación en el checkout.
  3. El operador entrega el código a conocidos o lo vende por canales externos.
  4. Los beneficiarios, con cuentas distintas, escriben el código en el checkout del Marketplace (UC-04). El Marketplace envía a cupons-api el código, el cliente y el carrito (F4, LC-2).
  5. cupons-api valida el cupón con las reglas ya alteradas: vigencia, elegibilidad, monto mínimo y usos disponibles. El resultado es válido, el descuento se aplica al producto o al envío y el uso se consume al confirmar el pago, de modo que parece un canje legítimo.
  6. El abuso solo se detecta al revisar los márgenes de la campaña. Sin bitácora inmutable ni aprobación doble, es difícil atribuir el cambio al operador y distinguirlo de un canje normal.
- **Vector práctico:** El operador usa la pantalla de creación y edición de cupones de cupons-frontend para modificar el valor del descuento, el límite de usos, la vigencia y el segmento del cupón. Después distribuye el código fuera de la campaña aprobada. Cada canje pasa por la validación de cupons-api en el checkout de UC-04 como si el cupón perteneciera a una campaña autorizada.
- **Impacto:** Pérdida económica por descuentos no autorizados y sin tope, consumo del presupuesto de campaña en beneficio personal y reventa del código. Los canjes legítimos de la campaña se confunden con los fraudulentos y el responsable es difícil de identificar sin aprobación doble ni bitácora inmutable.
- **Riesgo:** alto (2×3). Un operador interno con permisos amplios y sin aprobación ni alertas puede crear cupones sin límite, y la pérdida puede ser grande y difícil de atribuir hasta revisar márgenes.
- **Controles:**
  - *preventivo* (ecommerce): Exigir en cupons-frontend aprobación doble por una segunda persona autorizada para crear o editar cupones con descuento sobre un umbral, sin límite de usos totales, con vigencia ampliada o con segmento amplio, y aplicar topes de descuento, usos y vigencia por rol.
  - *preventivo* (ecommerce): Impedir que cupons-api active para el checkout cupones sin campaña aprobada asociada, y rechazar reglas fuera de rango (descuento máximo, usos totales obligatorios) aunque el operador las haya guardado.
  - *detectivo* (ecommerce): Registrar en una bitácora inmutable (append-only) cada creación o cambio de cupón con operador, valores anteriores y nuevos. Alertar sobre cupones creados fuera de campañas y sobre uso concentrado en pocas cuentas relacionadas o con tasa de canje anómala.
  - *correctivo* (ecommerce): Desactivar de inmediato el cupón sospechoso, retener las órdenes canjeadas pendientes de despacho, revisar los canjes con la bitácora, revocar o limitar los permisos del operador e iniciar el proceso disciplinario o de recuperación de pérdidas.
- **Referencias y patrones:** CAPEC-122 Privilege Abuse, OWASP API6:2023 Unrestricted Access to Sensitive Business Flows, FE-05

### UC-05 Cálculo del costo de envío según el perfil

<a id="av-0030"></a>
#### AV-0030 · Alteración de atributos de perfil (nivel, membresía, zona) para obtener un envío más barato o gratis

- **ID de origen:** AC-UC05-01 · **Ejecución:** Lote 1 · **Tema de riesgo:** R2
- **STRIDE:** T (E) — Manipulación
- **Actor:** Cliente con cuenta en el Marketplace (externo)
- **Elementos del DFD:** Marketplace, clients-api, delivery-api, F9, F5 · **Límites:** LC-1, LC-2
- **Precondiciones:**
  - El cliente tiene una cuenta activa y puede editar su perfil desde el Marketplace
  - clients-api acepta cambios sobre atributos de beneficio (nivel, membresía, zona) sin distinguir los editables por el cliente de los reservados al servidor
  - delivery-api confía en los atributos que devuelve clients-api (S-03) y no los contrasta con otra fuente
  - La cotización no se recalcula al confirmar el pago
- **Cómo ocurre:**
  1. El cliente inicia sesión en el Marketplace y observa la petición de actualización de perfil con un proxy de interceptación
  2. Agrega o modifica en esa petición los campos de nivel de cliente, membresía o zona, con valores de un nivel superior o de una zona de tarifa reducida
  3. clients-api acepta el cambio y lo persiste en el almacén de clientes, sin validar que el atributo es solo de servidor
  4. El cliente agrega al carrito un producto voluminoso y el Marketplace pide la cotización a delivery-api (F5)
  5. delivery-api consulta a clients-api (F9), recibe los atributos alterados y aplica la tarifa preferencial según RN-2
  6. El Marketplace muestra el envío reducido o gratis y el cliente paga la orden con ese costo
  7. Tras la compra, el cliente restaura los valores originales del perfil para no dejar rastro
- **Vector práctico:** Con un proxy de interceptación sobre su propia sesión, el cliente modifica en la petición de actualización de perfil los campos de nivel, membresía y zona que clients-api acepta sin validación. delivery-api los consume después como verdaderos para calcular la tarifa.
- **Impacto:** Pérdida de ingresos por envíos de productos voluminosos cobrados por debajo de la tarifa real, con costos de logística no recuperados. Se incumple RN-2 y se distorsionan las métricas de membresía y zonas. El abuso se replica si se difunde entre otros clientes.
- **Riesgo:** medio (2×2). Interceptar la petición de perfil es trivial, pero depende de que clients-api acepte esos campos sin validar (por confirmar); cada orden pierde solo el diferencial de envío.
- **Controles:**
  - *preventivo* (ecommerce): En clients-api, lista blanca de campos editables por el cliente en la petición de perfil: rechazar con 403 y no persistir nivel, membresía y zona (mass assignment, API3:2023). Esos atributos solo los cambian procesos del servidor con credencial de servicio.
  - *preventivo* (ecommerce): Recalcular la cotización de envío con los atributos vigentes al confirmar el pago, y cobrar el valor recalculado, no el mostrado antes.
  - *detectivo* (ecommerce): Auditar cada cambio de nivel, membresía o zona con origen (cliente, operador, proceso) y alertar si hay un cambio de beneficio seguido de compra en menos de N minutos, o si el atributo se restaura tras la compra.
  - *correctivo* (ecommerce): Revertir los atributos alterados, recotizar o facturar el diferencial de envío de las órdenes afectadas y bloquear la edición de perfil de las cuentas reincidentes.
- **Referencias y patrones:** CAPEC-39, CAPEC-202, OWASP API3:2023 Broken Object Property Level Authorization, FE-06

<a id="av-0031"></a>
#### AV-0031 · Operador de atención cambia atributos de perfil de conocidos para darles envío reducido

- **ID de origen:** AC-UC05-02 · **Ejecución:** Lote 1 · **Tema de riesgo:** R3
- **STRIDE:** E (T, R) — Elevación de privilegios
- **Actor:** Operador de atención al cliente con acceso de edición a perfiles en clients-api (interno)
- **Elementos del DFD:** clients-api, delivery-api, F9 · **Límites:** LC-1
- **Precondiciones:**
  - El operador puede editar atributos de perfil de clientes desde una herramienta administrativa
  - No hay justificación obligatoria ni aprobación de un segundo usuario para cambiar nivel, membresía o zona
  - La bitácora de cambios es insuficiente o editable, o no se revisa
  - delivery-api consulta los atributos en cada cotización (F9) y no verifica su origen
- **Cómo ocurre:**
  1. Un conocido del operador le pide una tarifa de envío menor para una compra de producto voluminoso
  2. El operador abre el perfil en la herramienta administrativa y sube el nivel o la membresía, o cambia la zona a una de tarifa menor
  3. clients-api guarda el cambio sin pedir justificación ni aprobación
  4. Cuando el conocido solicita la cotización, delivery-api consulta clients-api (F9) y calcula un costo reducido o nulo por RN-2
  5. El conocido paga la orden con el envío reducido
  6. El operador revierte los atributos, o repite el patrón con otras cuentas, sin que el cambio quede asociado a un caso de soporte
- **Vector práctico:** El operador usa la herramienta administrativa de perfiles para sobrescribir nivel, membresía o zona en cuentas de conocidos. delivery-api los toma en la cotización sin verificar su origen.
- **Impacto:** Descuentos de envío no autorizados y sostenidos en el tiempo, con pérdida económica difícil de detectar porque el costo se calcula de forma legítima sobre atributos adulterados. Si no hay bitácora fiable, no se puede atribuir el cambio al operador.
- **Riesgo:** medio (2×2). El operador tiene acceso legítimo y no hay doble aprobación confirmada, así que el abuso es plausible y difícil de ver, pero el descuento por orden es acotado.
- **Controles:**
  - *preventivo* (ecommerce): En la herramienta administrativa, exigir un ticket de soporte asociado y justificación obligatoria para cambiar nivel, membresía o zona, con aprobación de un segundo usuario (cuatro ojos) y permiso separado por rol para editar atributos de beneficio.
  - *preventivo* (ecommerce): Bitácora inmutable (append-only, fuera del control del operador) que registre quién cambió qué atributo, el valor anterior y el nuevo, y el ticket asociado.
  - *detectivo* (ecommerce): Reporte y alerta de cambios de atributos de beneficio hechos por el mismo operador sobre varias cuentas, de cuentas que compran justo tras el cambio y de reversiones posteriores a la compra. Revisión mensual por una función independiente.
  - *correctivo* (ecommerce): Revocar el permiso de edición al operador implicado, revertir los atributos y recuperar el diferencial de envío según el proceso disciplinario.
- **Referencias y patrones:** CAPEC-39, FE-06

<a id="av-0032"></a>
#### AV-0032 · Manipulación de la tarifa cotizada en el tránsito de la respuesta entre delivery-api y el Marketplace

- **ID de origen:** AC-UC05-03 · **Ejecución:** Lote 1 · **Tema de riesgo:** R2
- **STRIDE:** T (E) — Manipulación
- **Actor:** Cliente que controla su navegador y sus peticiones (externo)
- **Elementos del DFD:** Marketplace, delivery-api, F5 · **Límites:** LC-1, LC-2
- **Precondiciones:**
  - El Marketplace conserva en el cliente (campo de formulario, parámetro o estado del carrito) la tarifa cotizada y la reenvía al confirmar la orden
  - delivery-api o el Marketplace no recalculan ni verifican la firma de la tarifa al crear la orden de entrega o al cobrar
  - El cliente puede ver y modificar las peticiones de su propia sesión
- **Cómo ocurre:**
  1. El cliente arma un carrito con un producto voluminoso y solicita la cotización de envío
  2. Con un proxy de interceptación identifica la respuesta con la tarifa y la petición posterior de confirmación que la incluye
  3. Intercepta la petición de confirmación del pedido y reemplaza el valor de la tarifa por uno menor o cero
  4. El Marketplace acepta la tarifa recibida, la registra en la orden y cobra el total reducido
  5. La orden de entrega se crea en delivery-api (F5) con el costo manipulado y se despacha con normalidad
- **Vector práctico:** Con un proxy de interceptación, el cliente reemplaza en la petición de confirmación el campo de tarifa de envío cotizada por un valor menor. El servidor la acepta como autoritativa porque no hay firma ni recálculo.
- **Impacto:** Envíos de productos voluminosos cobrados por debajo del costo real, con pérdidas directas por orden y riesgo de explotación masiva mediante automatización. Los registros de órdenes quedan inconsistentes con las reglas RN-2 y RN-4.
- **Riesgo:** alto (2×3). Reemplazar un campo en la confirmación es muy simple si el servidor confía en él (S-10 por confirmar), y es automatizable, con pérdida directa en cada orden.
- **Controles:**
  - *preventivo* (ecommerce): No aceptar la tarifa de envío enviada por el cliente: el Marketplace recalcula el envío en el servidor con delivery-api al crear la orden, o valida una cotización con ID, vigencia corta y firma HMAC emitida por delivery-api y ligada al carrito, a la dirección y al perfil.
  - *preventivo* (pasarela de pago): Calcular el monto de la autorización de pago en el servidor desde el total de la orden recalculado, y rechazar cualquier importe enviado por el navegador.
  - *detectivo* (ecommerce): Conciliar por orden la tarifa cobrada contra la que delivery-api calcularía con los mismos datos y alertar de diferencias; registrar los intentos de firma inválida o de tarifa alterada.
  - *correctivo* (ecommerce): Retener las órdenes con tarifa inconsistente antes del despacho, cobrar el diferencial o cancelarlas y bloquear las cuentas con intentos repetidos.
- **Referencias y patrones:** CAPEC-39, CAPEC-202, OWASP API6:2023, AV-0003, FE-06

<a id="av-0033"></a>
#### AV-0033 · Falsificación de dimensiones, peso o dirección en la solicitud de cotización para abaratar el envío

- **ID de origen:** AC-UC05-04 · **Ejecución:** Lote 1 · **Tema de riesgo:** R2
- **STRIDE:** T (I) — Manipulación
- **Actor:** Cliente que controla los parámetros de su solicitud (externo)
- **Elementos del DFD:** Marketplace, delivery-api, F5 · **Límites:** LC-1, LC-2
- **Precondiciones:**
  - La solicitud de cotización incluye peso, volumen o código postal enviados por el cliente o por el frontend del Marketplace
  - delivery-api calcula con los datos recibidos y no los contrasta con el catálogo ni con la dirección guardada
  - El cliente puede interceptar y modificar sus peticiones
- **Cómo ocurre:**
  1. El cliente agrega un producto voluminoso y dispara la cotización de envío
  2. Con un proxy de interceptación captura la petición Marketplace → delivery-api y localiza los campos de peso, volumen y código postal o coordenadas
  3. Reduce el peso y el volumen a los de un artículo pequeño, o cambia el código postal por uno cercano al almacén, solo en la cotización
  4. delivery-api calcula la tarifa con esos datos según peso, volumen y distancia (RN-4) y devuelve un costo bajo
  5. El cliente continúa la compra con el costo bajo y la dirección real de entrega se registra aparte
  6. Al llegar el producto, logística se enfrenta a un costo real mayor al cobrado
- **Vector práctico:** Con un proxy de interceptación, el cliente reduce los campos de peso y volumen y cambia el código postal en la solicitud de cotización. delivery-api calcula la tarifa con esos valores sin contrastarlos con el catálogo ni con la dirección de la orden.
- **Impacto:** Subcobro sistemático del envío de productos voluminosos y pérdida de margen. Puede generar conflictos operativos si el transportista rechaza o recobra la carga real, y datos erróneos de planificación de rutas y capacidad.
- **Riesgo:** medio (2×2). Es fácil si delivery-api usa peso, volumen y código postal enviados por el cliente (por confirmar), pero el transportista acaba detectando la diferencia.
- **Controles:**
  - *preventivo* (ecommerce): delivery-api recibe solo SKU y cantidad y obtiene peso y volumen del catálogo interno. La dirección de destino sale de la dirección guardada o validada de la orden, nunca de campos libres de la cotización.
  - *preventivo* (ecommerce): Validar en el servidor el esquema y los rangos de la solicitud de cotización, y rechazar campos de dimensión o peso que no esperaba recibir.
  - *detectivo* (proveedor logístico): Comparar peso y volumen medidos en la recolección o el hub con los de la orden y reportar las desviaciones por encima del umbral acordado.
  - *detectivo* (ecommerce): Alertar si el código postal de la cotización difiere del de la entrega final, o si una misma cuenta hace cotizaciones del mismo SKU con dimensiones o códigos postales distintos.
  - *correctivo* (proveedor logístico): Cobrar al cliente el recargo por diferencia de peso o volumen según los términos del servicio, o recotizar antes de entregar, y marcar la cuenta para revisión.
- **Referencias y patrones:** CAPEC-39, CAPEC-202, FE-06

<a id="av-0034"></a>
#### AV-0034 · Abuso de un cupón de envío por cuenta distinta o fuera de condiciones al consultar cupons-api

- **ID de origen:** AC-UC05-05 · **Ejecución:** Lote 1 · **Tema de riesgo:** R2
- **STRIDE:** E (T) — Elevación de privilegios
- **Actor:** Cliente que obtiene o reutiliza códigos de cupón de envío (externo)
- **Elementos del DFD:** delivery-api, cupons-api, Marketplace, F5 · **Límites:** LC-2
- **Precondiciones:**
  - delivery-api pregunta a cupons-api si hay un cupón de envío aplicable y toma su respuesta como válida (S-03)
  - La aplicabilidad del cupón (vigencia, perfil, producto, usos) se valida de forma incompleta o solo en el frontend
  - El cliente dispone de códigos filtrados, de campañas dirigidas a otro perfil o de uno ya consumido
  - El código se envía como dato de la solicitud de cotización
- **Cómo ocurre:**
  1. El cliente consigue un código de cupón de envío gratuito de una campaña de otro segmento o ya agotado
  2. Agrega un producto voluminoso y solicita la cotización incluyendo el código en la petición hacia el Marketplace
  3. El Marketplace pasa el código a delivery-api (F5), que consulta a cupons-api si aplica
  4. cupons-api responde que es aplicable porque no verifica el perfil, el producto o el contador de usos de forma atómica
  5. delivery-api resta el beneficio y devuelve un envío gratis o reducido
  6. El cliente repite la operación en varias órdenes o con cuentas distintas con el mismo código
- **Vector práctico:** El cliente envía en la solicitud de cotización un código de cupón de envío que no le corresponde o ya fue usado, repitiéndolo desde varias cuentas o sesiones. cupons-api lo valida sin vincularlo al perfil ni descontar usos, y delivery-api aplica el descuento.
- **Impacto:** Pérdida de ingresos por envíos gratuitos o rebajados a quienes no cumplen las condiciones de la campaña. Erosiona el presupuesto de promociones y favorece la reventa de cupones.
- **Riesgo:** alto (3×2). Reutilizar o compartir códigos es habitual y fácil de automatizar, y la validación de cupons-api es incompleta o no atómica (por confirmar); cada uso causa una pérdida limitada.
- **Controles:**
  - *preventivo* (ecommerce): cupons-api valida en el servidor vigencia, segmento o perfil, SKU aplicable y cupo de usos, vinculando el cupón al cliente (o a la campaña) con las reglas de la campaña. delivery-api envía el ID de cliente autenticado, no uno aportado por el cliente.
  - *preventivo* (ecommerce): Descontar los usos de forma atómica (reserva con transacción o un contador con operación condicional) al confirmar la orden, y liberarlos si se cancela, para evitar carreras entre solicitudes concurrentes.
  - *detectivo* (ecommerce): Alertar por un mismo cupón usado desde varias cuentas, IP o dispositivos, por usos que superan el cupo o por muchas validaciones fallidas de códigos.
  - *correctivo* (ecommerce): Revocar el cupón filtrado, anular o facturar el descuento de las órdenes fraudulentas, y emitir códigos nuevos nominales a los destinatarios legítimos.
- **Referencias y patrones:** OWASP API6:2023, CAPEC-202, FE-05

<a id="av-0035"></a>
#### AV-0035 · Cupón de envío con descuento excesivo o sin límite creado por un operador de marketing

- **ID de origen:** AC-UC05-06 · **Ejecución:** Lote 1 · **Tema de riesgo:** R3
- **STRIDE:** E (T, R) — Elevación de privilegios
- **Actor:** Operador de marketing con acceso al backoffice de cupones (interno)
- **Elementos del DFD:** cupons-api, delivery-api · **Límites:** LC-1
- **Precondiciones:**
  - El backoffice permite crear o ampliar cupones de envío sin aprobación de una segunda persona
  - No hay topes por rol ni alertas de uso concentrado
  - delivery-api aplica sin verificar límites razonables el cupón que cupons-api da como aplicable (S-03)
- **Cómo ocurre:**
  1. El operador crea en el backoffice un cupón de envío del 100 % sin límite de usos o amplía la vigencia de uno existente
  2. Se lo da o vende a conocidos o lo usa con cuentas propias
  3. Los beneficiarios piden cotizaciones de productos voluminosos con ese código
  4. delivery-api consulta a cupons-api, que lo da como aplicable, y calcula envío gratis para cada orden
  5. El abuso continúa hasta que alguien revisa los márgenes de logística
  6. El operador puede negar la creación si la bitácora no es inmutable
- **Vector práctico:** El operador usa el formulario del backoffice de cupones para crear o modificar un cupón de envío con descuento total, vigencia ampliada y sin tope de usos. delivery-api aplica ese cupón en las cotizaciones de las cuentas beneficiarias.
- **Impacto:** Fuga de margen por envíos de productos voluminosos sin cobrar, sostenida y repetible. Dificultad para atribuir responsabilidad si la bitácora es débil, y pérdida de confianza en el control de campañas.
- **Riesgo:** medio (1×3). Exige un operador interno malicioso, pero un cupón de 100 % sin límite se repite y se sostiene hasta que alguien revisa los márgenes.
- **Controles:**
  - *preventivo* (ecommerce): En el backoffice, aprobación doble para cupones de envío con descuento superior al umbral, sin tope de usos o con vigencia ampliada, y topes máximos de descuento, usos y vigencia por rol.
  - *preventivo* (ecommerce): cupons-api impone campos obligatorios (tope de usos, vigencia máxima, campaña aprobada asociada) y rechaza cupones que no cumplan, aunque venga del backoffice.
  - *detectivo* (ecommerce): Alertas en tiempo casi real por cupones fuera de campañas aprobadas, descuentos fuera de rango, uso concentrado en pocas cuentas relacionadas y crecimiento anómalo del costo de envío subsidiado.
  - *detectivo* (ecommerce): Bitácora inmutable de creación y modificación de cupones, con usuario, valores anteriores y aprobador, que el operador no pueda editar ni borrar.
  - *correctivo* (ecommerce): Desactivar de inmediato el cupón y las campañas asociadas, cuantificar el subsidio indebido y recuperar el importe según el procedimiento interno.
- **Referencias y patrones:** CAPEC-202, FE-05

### UC-06 Elección de la modalidad de entrega

<a id="av-0036"></a>
#### AV-0036 · Alteración del costo de la modalidad de entrega elegida en la petición de selección

- **ID de origen:** AC-UC06-01 · **Ejecución:** Lote 2 · **Tema de riesgo:** R2
- **STRIDE:** T (E) — Manipulación
- **Actor:** Cliente que controla su navegador y las peticiones de selección de modalidad (externo)
- **Elementos del DFD:** Marketplace, delivery-api, F5, Costo de cada opción, Modalidad de entrega · **Límites:** LC-1, LC-2
- **Precondiciones:**
  - El cliente tiene un carrito con un producto voluminoso y llega al paso de elección de modalidad
  - La petición de selección enviada al Marketplace incluye, además del identificador de modalidad, el costo y la ventana que mostró la interfaz
  - El Marketplace no vuelve a consultar a delivery-api el costo de la opción elegida antes de registrarla ni antes de cobrar (supuesto)
- **Cómo ocurre:**
  1. El cliente abre el paso de elección de modalidad y delivery-api devuelve las opciones con costo y fecha estimada (envío a domicilio caro, recolección gratis o barata)
  2. Con un proxy de interceptación en su navegador, el cliente localiza la petición de selección y los campos de modalidad, costo y ventana
  3. Selecciona entrega a domicilio, que es la que necesita, pero reemplaza el campo de costo por el valor de la opción de recolección, o por cero
  4. El Marketplace acepta el costo recibido, lo asocia a la modalidad de entrega a domicilio y lo suma al total mostrado
  5. El cliente paga el total reducido; la orden de entrega se crea en delivery-api con modalidad domicilio y costo manipulado, y la logística la despacha con normalidad
- **Vector práctico:** Con un proxy de interceptación (por ejemplo Burp Suite), el cliente modifica en la petición Marketplace → delivery-api el campo de costo de la opción elegida, dejando intacto el identificador de la modalidad de entrega a domicilio, para pagar el costo de otra opción o cero.
- **Impacto:** Pérdida económica por envíos cobrados por debajo de su tarifa real, que la empresa o el proveedor logístico absorben; incumplimiento de RN-2 y descuadre entre el total cobrado y el costo logístico; el abuso es escalable a muchas órdenes de producto voluminoso.
- **Riesgo:** alto (3×2). Alterar un campo de costo con un proxy es trivial si el Marketplace reenvía el valor del cliente (S-10), y la pérdida por envío subcobrado es moderada pero repetible en muchas órdenes de producto voluminoso.
- **Controles:**
  - *preventivo* (ecommerce): El Marketplace ignora cualquier costo o ventana recibidos del cliente: la petición de selección solo lleva el identificador de la opción, y el costo se toma de la cotización que delivery-api guardó en servidor para esa orden (RN-2).
  - *preventivo* (pasarela de pago): Antes de iniciar el pago, el Marketplace recalcula el costo de la opción elegida contra delivery-api y fija el monto total en servidor; la pasarela solo autoriza el monto de la sesión de pago creada por el servidor del ecommerce y rechaza importes que no coincidan.
  - *detectivo* (ecommerce): Registrar como evento de seguridad toda petición de selección cuyo campo de costo recibido difiera del calculado por delivery-api, con alerta por cuenta o IP reincidente.
  - *detectivo* (proveedor logístico): Conciliación diaria entre el costo de envío cobrado en cada orden y la tarifa que delivery-api y el proveedor logístico calcularon para esa orden, con alerta ante diferencias.
  - *correctivo* (ecommerce): Retener el despacho de las órdenes con diferencia detectada, cobrar la diferencia al cliente o cancelar la orden, y suspender cuentas que manipulen el costo de forma reiterada.
- **Referencias y patrones:** OWASP API3:2023 Broken Object Property Level Authorization, OWASP API6:2023 Unrestricted Access to Sensitive Business Flows, AV-0032, AV-0020

<a id="av-0037"></a>
#### AV-0037 · Cambio de modalidad o tienda después de calculado el costo para conservar el beneficio de la opción más barata

- **ID de origen:** AC-UC06-02 · **Ejecución:** Lote 2 · **Tema de riesgo:** R2
- **STRIDE:** T (E) — Manipulación
- **Actor:** Cliente que conserva una cotización favorable y cambia la modalidad en pasos posteriores (externo)
- **Elementos del DFD:** Marketplace, delivery-api, Modalidad de entrega, Tienda de recolección, Costo de cada opción, Orden de entrega · **Límites:** LC-1, LC-2
- **Precondiciones:**
  - La modalidad y la tienda de recolección se guardan en la orden mediante peticiones separadas del cálculo del costo
  - El costo no se recalcula cuando se modifica la modalidad o la tienda después de la cotización (supuesto)
- **Cómo ocurre:**
  1. El cliente selecciona recolección en una tienda cercana a su perfil y el sistema registra un costo bajo o nulo
  2. Con un proxy de interceptación, el cliente identifica la petición que asigna modalidad y tienda a la orden, y también la petición final de confirmación del pedido
  3. Antes de pagar, cambia en la petición de confirmación el identificador de modalidad a entrega a domicilio, manteniendo el costo ya cotizado para recolección
  4. El Marketplace registra la orden con modalidad domicilio y el costo de recolección, sin recalcular en delivery-api
  5. delivery-api crea la orden de entrega a domicilio con una tarifa que no corresponde al peso, volumen, distancia y perfil
- **Vector práctico:** Con un proxy de interceptación, el cliente modifica el campo de modalidad (o el identificador de tienda) en la petición de confirmación de la orden, tras haber obtenido la cotización de la otra opción, de modo que la orden se registra con una modalidad distinta de la que originó el costo cobrado.
- **Impacto:** Envío a domicilio de un producto voluminoso cobrado como recolección gratuita o barata; pérdida directa por costo logístico no cobrado; órdenes inconsistentes entre modalidad, costo y ventana que generan reprocesos operativos.
- **Riesgo:** alto (3×2). Cambiar la modalidad en la petición de confirmación es fácil con un proxy cuando el costo no se recalcula (S-10), y el impacto es una pérdida directa por envíos a domicilio cobrados como recolección.
- **Controles:**
  - *preventivo* (ecommerce): Atar la cotización a la orden con un identificador de cotización firmado en servidor que incluya modalidad, tienda, costo y ventana, con vigencia corta. La confirmación solo acepta ese identificador y no un campo de modalidad o tienda suelto.
  - *preventivo* (ecommerce): Invalidar la cotización y recalcular el costo en delivery-api cada vez que cambie la modalidad o la tienda (S-18), y volver a recalcular al confirmar, justo antes del pago.
  - *preventivo* (ecommerce): Al crear la orden de entrega, delivery-api valida la coherencia entre modalidad, costo y ventana, y rechaza la orden si la tarifa es inferior a la que corresponde al peso, volumen y distancia.
  - *detectivo* (ecommerce): Registrar y alertar los cambios de modalidad o tienda ocurridos entre la cotización y la confirmación, en especial recolección a domicilio, y los patrones repetidos por cuenta.
  - *detectivo* (proveedor logístico): El proveedor logístico concilia la tarifa de las órdenes a domicilio despachadas contra su tarifario y reporta las órdenes con tarifa inferior a la esperada.
  - *correctivo* (ecommerce): Detener el despacho de órdenes inconsistentes antes de la recolección por el proveedor, y cobrar la diferencia, reprocesar la orden con la modalidad correcta o cancelarla y reembolsar.
- **Referencias y patrones:** OWASP API6:2023 Unrestricted Access to Sensitive Business Flows, AV-0032

<a id="av-0038"></a>
#### AV-0038 · Reserva masiva de ventanas de entrega y tiendas por consulta y selección repetida sin completar la compra

- **ID de origen:** AC-UC06-04 · **Ejecución:** Lote 2 · **Tema de riesgo:** R8
- **STRIDE:** D — Denegación de servicio
- **Actor:** Atacante externo o cliente que automatiza la selección de modalidad con varias cuentas (externo)
- **Elementos del DFD:** Marketplace, delivery-api, Ventana de entrega, Tienda de recolección, F5 · **Límites:** LC-1, LC-2
- **Precondiciones:**
  - La selección de modalidad y tienda reserva capacidad de entrega o recolección sin pago previo (supuesto)
  - No hay límites de frecuencia ni expiración corta de la reserva por cuenta, dispositivo o IP
  - delivery-api calcula costo y ventana en cada consulta contra su proveedor logístico
- **Cómo ocurre:**
  1. El atacante crea varias cuentas de cliente y agrega un producto voluminoso al carrito en cada una
  2. Con un script de peticiones repetidas hacia el Marketplace, consulta las opciones de delivery-api y selecciona las ventanas más próximas y las tiendas con mayor demanda
  3. Repite la selección en múltiples órdenes y nunca llega al pago, de modo que las reservas siguen retenidas
  4. Las ventanas y la capacidad de recolección de las tiendas objetivo se agotan, y otros clientes solo ven opciones tardías o ninguna
  5. delivery-api acumula carga de cálculo de costos y consultas al proveedor logístico
- **Vector práctico:** Con un script de peticiones automatizadas, el atacante invoca en volumen la selección de modalidad y tienda desde varias cuentas, con el identificador de la ventana de entrega como dato que bloquea la capacidad, sin completar el pago.
- **Impacto:** Indisponibilidad de ventanas de entrega y recolección para clientes legítimos, pérdida de ventas de producto voluminoso, mayor consumo de delivery-api y del proveedor logístico, y posible sabotaje dirigido por un competidor.
- **Riesgo:** medio (2×2). Exige automatización y varias cuentas, pero es sencillo de ejecutar si la reserva se hace sin pago y sin límites, y bloquea ventas y capacidad logística de forma visible.
- **Controles:**
  - *preventivo* (ecommerce): La reserva de ventana o de capacidad de tienda es temporal, con vencimiento corto ligado al checkout (por ejemplo 10 a 15 minutos) y liberación automática si no hay pago; solo se confirma tras el pago aprobado.
  - *preventivo* (ecommerce): Limitar la frecuencia de consultas de opciones y de selecciones por cuenta, dispositivo e IP, con tope de reservas activas por cuenta y desafío anti-automatización (CAPTCHA) al superar umbrales o en cuentas nuevas.
  - *preventivo* (proveedor logístico): Almacenar en caché las cotizaciones de delivery-api por zona y producto durante un tiempo corto, y aplicar cuotas por cliente de API en las consultas al proveedor logístico, para que las repeticiones no generen cálculo ni consultas ilimitadas.
  - *detectivo* (ecommerce): Monitorear la relación entre reservas y pagos completados por cuenta, IP y dispositivo, y la ocupación anómala de ventanas y tiendas, con alertas ante picos de reservas sin pago.
  - *correctivo* (ecommerce): Liberar en bloque las reservas de las cuentas o IP marcadas, bloquear o limitar esas cuentas y ajustar de inmediato los límites y el tiempo de vencimiento.
- **Referencias y patrones:** OWASP API4:2023 Unrestricted Resource Consumption, OWASP API6:2023 Unrestricted Access to Sensitive Business Flows

<a id="av-0039"></a>
#### AV-0039 · Asignación de una tienda de recolección fuera de las ofrecidas para obtener una ventana de entrega más corta (acceso fuera de lo autorizado)

- **ID de origen:** AC-UC06-03 · **Ejecución:** Lote 2 · **Tema de riesgo:** R2
- **STRIDE:** E (T) — Elevación de privilegios
- **Actor:** Cliente que accede a una tienda de recolección no autorizada para su orden, sustituyendo el identificador de tienda en la petición de asignación (externo)
- **Elementos del DFD:** Marketplace, delivery-api, Tienda de recolección, Ventana de entrega, Orden de entrega · **Límites:** LC-1, LC-2
- **Precondiciones:**
  - El cliente elige recolección y selecciona la tienda desde la lista de opciones que delivery-api devuelve con su ventana de entrega
  - delivery-api devuelve ventanas de entrega distintas por tienda y solo ofrece al cliente las tiendas que corresponden a su zona o a su orden (supuesto nuevo SN-01, no documentado en UC-06)
  - delivery-api asigna a la orden el identificador de tienda recibido sin verificar que pertenezca al conjunto de tiendas ofrecidas para esa orden (supuesto, relacionado con S-18)
  - Existe al menos una tienda fuera de la lista ofrecida al cliente cuya ventana de entrega es más corta que la de las tiendas ofrecidas
- **Cómo ocurre:**
  1. El cliente agrega un producto voluminoso, elige recolección y recibe de delivery-api la lista de tiendas ofrecidas, cada una con su ventana de entrega
  2. El cliente compara las ventanas y ve que todas las tiendas ofrecidas tienen una fecha estimada más lejana de la que necesita
  3. Con un proxy de interceptación captura la petición que asigna la tienda a la orden y sustituye el identificador de tienda por el de una tienda que no estaba en la lista y que conoce por otra cuenta, otra zona o por prueba de valores cercanos
  4. delivery-api acepta el identificador porque no lo contrasta con el conjunto de tiendas autorizado para esa orden, asigna esa tienda y le atribuye la ventana de entrega propia de esa tienda, más corta que las ofrecidas
  5. El cliente completa el pago con la tienda sustituida y recibe una fecha de recolección anticipada a la que la política le asignaría; la orden de entrega queda registrada en delivery-api con esa tienda y esa ventana
- **Vector práctico:** Con un proxy de interceptación en su navegador, el cliente reemplaza en la petición de asignación de tienda el campo del identificador de tienda de recolección por el de una tienda no incluida en la respuesta de opciones, para acceder a una asignación que no le fue autorizada y quedarse con la ventana de entrega más corta de esa tienda; el dato manipulado es el identificador de tienda.
- **Impacto:** El cliente accede a una tienda y a una fecha de recolección que no le corresponden por su zona u orden, y la asignación salta la regla de qué tiendas se ofrecen a cada cliente. La tienda fuera de zona recibe órdenes que no le corresponden y puede incumplir la ventana prometida, lo que genera reclamos, y la información de ventanas por tienda queda disponible para quien pruebe valores.
- **Riesgo:** medio (2×2). Sustituir el identificador de tienda es fácil si delivery-api no lo contrasta con las tiendas ofrecidas (S-18), pero depende del supuesto SN-01 aún sin confirmar y el beneficio es una fecha anticipada con efecto operativo moderado.
- **Controles:**
  - *preventivo* (ecommerce): delivery-api guarda el conjunto de tiendas ofrecidas a cada orden y, al asignar, valida que el identificador recibido pertenezca a ese conjunto (autorización a nivel de objeto y de propiedad); si no pertenece, rechaza la asignación.
  - *preventivo* (ecommerce): La ventana de entrega se calcula en servidor a partir de la tienda ya validada, sin aceptar ventana ni identificadores secuenciales del cliente. Los identificadores de tienda no deben ser predecibles.
  - *detectivo* (ecommerce): Alertar sobre intentos de asignar tiendas no ofrecidas o fuera de zona y sobre cuentas que prueban identificadores de tienda cercanos, correlacionando por cuenta e IP.
  - *detectivo* (proveedor logístico): El punto de recolección reporta las órdenes de recolección asignadas que no corresponden a su zona o cobertura, para detectar asignaciones indebidas que no se vieron en línea.
  - *correctivo* (ecommerce): Reasignar la orden a una tienda válida para el cliente, recalcular la ventana, notificar el cambio y ofrecer cancelación con reembolso. Limitar la cuenta si el intento fue deliberado.
- **Referencias y patrones:** OWASP API3:2023 Broken Object Property Level Authorization, OWASP API6:2023 Unrestricted Access to Sensitive Business Flows, AV-0020

### UC-07 Pago y registro de la orden

<a id="av-0040"></a>
#### AV-0040 · Confirmación de pago falsificada enviada al Marketplace para registrar una orden como pagada sin pagar

- **ID de origen:** AC-UC07-01 · **Ejecución:** Lote 2 · **Tema de riesgo:** R4
- **STRIDE:** S (T) — Suplantación
- **Actor:** Atacante o cliente que se hace pasar por la pasarela de pago (externo)
- **Elementos del DFD:** Marketplace, Pasarela de pago, Confirmación de pago, delivery-api, Almacén de órdenes del Marketplace · **Límites:** LC-1, LC-2, LC-6
- **Precondiciones:**
  - El Marketplace registra la orden al recibir una confirmación de pago por redirección o notificación asíncrona (S-05)
  - El punto de recepción de la confirmación es accesible desde internet
  - El Marketplace no verifica la firma ni el origen de la notificación, o la firma es débil o predecible
  - El atacante puede obtener la referencia de su propia orden en curso
- **Cómo ocurre:**
  1. El atacante arma un carrito de alto valor y avanza hasta el paso de pago, con lo que se genera una orden pendiente con su referencia
  2. Observa con un proxy de interceptación el formato de una confirmación legítima, por ejemplo en una compra barata propia o en la redirección de retorno
  3. Construye una notificación con el mismo formato, la referencia de la orden pendiente y el estado de pago aprobado
  4. Envía la notificación al punto de recepción del Marketplace con un cliente HTTP, sin pasar por la pasarela
  5. El Marketplace la acepta como auténtica, registra la orden como pagada y consume el cupón
  6. Se crea la orden de entrega en delivery-api y se inicia la preparación del pedido sin que exista ningún cobro
- **Vector práctico:** Con un cliente HTTP y un proxy de interceptación, el atacante fabrica y envía directamente al Marketplace una notificación de pago aprobado que imita el formato de la pasarela. Manipula los campos de estado de pago y referencia de orden, y aprovecha la ausencia de verificación de firma y de consulta de confirmación a la pasarela.
- **Impacto:** Pérdida directa del valor del producto y del envío, porque se prepara y despacha mercancía no pagada. Además se consumen cupones y se genera un registro de orden con estado de pago falso, lo que contamina conciliaciones y reportes financieros.
- **Riesgo:** alto (2×3). El punto de recepción es público y se asume que no se verifica la firma, por lo que forjar la notificación es sencillo y despacha mercancía sin cobro.
- **Controles:**
  - *preventivo* (ecommerce): Verificar en el Marketplace la firma HMAC de cada notificación con el secreto compartido de la pasarela, validar la marca de tiempo y rechazar notificaciones repetidas o fuera de ventana, sin aceptar nunca el estado de pago llegado por la redirección del navegador.
  - *preventivo* (pasarela de pago): Firmar todas las notificaciones de pago, permitir la rotación del secreto y publicar un endpoint de consulta del estado de la transacción por referencia.
  - *preventivo* (ecommerce): Antes de registrar la orden como pagada, consultar de servidor a servidor a la pasarela el estado, el monto y la referencia de la transacción, y solo entonces crear la orden de entrega en delivery-api.
  - *detectivo* (ecommerce): Alertar sobre notificaciones con firma inválida o desde orígenes no esperados, y conciliar a diario las órdenes pagadas contra las liquidaciones de la pasarela para encontrar órdenes sin cobro.
  - *correctivo* (ecommerce): Ante una orden pagada sin cobro confirmado, detener la preparación y cancelar la orden de entrega en delivery-api, revertir el cupón consumido y bloquear la cuenta implicada.
- **Referencias y patrones:** CAPEC-39, CAPEC-277, OWASP Top 10 A04:2021 Insecure Design, S-05, S-26

<a id="av-0041"></a>
#### AV-0041 · Pago de un monto menor al total de la orden aprovechando que el Marketplace no compara el monto confirmado

- **ID de origen:** AC-UC07-02 · **Ejecución:** Lote 2 · **Tema de riesgo:** R2
- **STRIDE:** T (S) — Manipulación
- **Actor:** Cliente con un proxy de interceptación en su navegador (externo)
- **Elementos del DFD:** Marketplace, Pasarela de pago, Total de la orden, Confirmación de pago, Almacén de órdenes del Marketplace · **Límites:** LC-1, LC-6
- **Precondiciones:**
  - El monto a cobrar viaja por el navegador del cliente en la redirección hacia la pasarela, o puede alterarse en el flujo de inicio de pago
  - El Marketplace considera pagada la orden con solo recibir un estado aprobado y no contrasta el monto confirmado con el total almacenado de la orden
  - La pasarela cobra el monto que recibe, aunque no coincida con el de la orden
- **Cómo ocurre:**
  1. El cliente arma un carrito con un producto caro y llega al paso de pago, donde el Marketplace muestra el total final
  2. Con el proxy intercepta la petición de redirección a la pasarela e identifica el campo del monto a cobrar
  3. Reemplaza ese monto por un valor muy inferior, manteniendo la referencia de la orden original
  4. Paga en la pasarela el monto reducido, que la pasarela confirma como aprobado
  5. La pasarela confirma al Marketplace con la misma referencia de orden y el monto cobrado
  6. El Marketplace registra la orden por el total original como pagada, sin validar el monto, y crea la orden de entrega
- **Vector práctico:** Con un proxy de interceptación, el cliente modifica el campo de monto en la petición que inicia el pago en la pasarela y conserva intacta la referencia de la orden. Aprovecha que la confirmación se acepta por el estado aprobado, sin comparar el monto cobrado con el total de la orden registrada.
- **Impacto:** Venta con cobro parcial: el comercio entrega el producto completo y recibe solo una fracción del precio. El fraude es repetible y escala en volumen, y genera discrepancias entre el total de la orden y el cobro real que dificultan la detección.
- **Riesgo:** alto (2×3). Alterar el monto con un proxy es una técnica básica, depende de que el monto viaje por el cliente, y el fraude es repetible y escalable.
- **Controles:**
  - *preventivo* (ecommerce): Crear la sesión de pago desde el servidor con el total calculado y almacenado de la orden, sin aceptar nunca el monto desde parámetros del navegador.
  - *preventivo* (pasarela de pago): Ofrecer sesiones de pago creadas por API de servidor con monto, moneda y referencia inmutables, y rechazar parámetros de monto alterados en la redirección.
  - *preventivo* (ecommerce): Al recibir la confirmación, comparar monto y moneda cobrados con el total almacenado de la orden y registrar como pagada solo si coinciden exactamente.
  - *detectivo* (ecommerce): Alertar y reportar toda discrepancia entre el monto cobrado y el total de la orden, y vigilar clientes con varias órdenes de cobro parcial.
  - *correctivo* (ecommerce): Dejar la orden en estado de pago parcial, retener la entrega y reclamar la diferencia al cliente o reembolsar y cancelar la orden.
- **Referencias y patrones:** CAPEC-39, OWASP Top 10 A04:2021 Insecure Design, AV-0032, AV-0017, S-05, S-26

<a id="av-0042"></a>
#### AV-0042 · Reutilización de una confirmación de pago legítima de una orden barata para marcar como pagada una orden de alto valor

- **ID de origen:** AC-UC07-03 · **Ejecución:** Lote 2 · **Tema de riesgo:** R4
- **STRIDE:** T (S, R) — Manipulación
- **Actor:** Cliente con dos órdenes abiertas y un proxy de interceptación (externo)
- **Elementos del DFD:** Marketplace, Pasarela de pago, Confirmación de pago, Almacén de órdenes del Marketplace, delivery-api · **Límites:** LC-1, LC-6
- **Precondiciones:**
  - La confirmación de pago, en redirección o notificación, no está ligada de forma verificable a una única orden, un monto y un uso
  - El Marketplace no controla idempotencia ni que cada referencia de pago se use una sola vez
  - El cliente puede tener varias órdenes pendientes al mismo tiempo
- **Cómo ocurre:**
  1. El cliente crea dos órdenes pendientes: una de bajo valor y otra de un producto de alto valor
  2. Paga legítimamente la orden barata y, con un proxy, captura la redirección de retorno con la confirmación de esa transacción
  3. Intercepta el retorno de la orden cara y sustituye el identificador de la orden o la referencia de pago por los de la transacción ya pagada
  4. El Marketplace valida solo que la referencia de pago existe y está aprobada, sin cruzarla con la orden ni con el monto
  5. Registra la orden cara como pagada y consume el cupón
  6. Se crea la orden de entrega y se despacha el producto caro
  7. La referencia de pago original queda asociada a dos órdenes
- **Vector práctico:** Con un proxy de interceptación, el cliente captura la confirmación de una compra barata pagada y la reutiliza o ajusta en el retorno de otra orden de mayor valor. Manipula el identificador de orden y la referencia de pago, aprovechando que no se valida su correspondencia ni que la referencia sea de un solo uso.
- **Impacto:** Entrega de mercancía de alto valor con el pago de una orden menor. Una misma referencia de pago respalda dos órdenes, lo que descuadra la conciliación con la pasarela y dificulta probar el fraude después.
- **Riesgo:** alto (2×3). Reutilizar una confirmación legítima es fácil si no se liga a orden y monto, y permite despachar un producto caro pagando uno barato.
- **Controles:**
  - *preventivo* (ecommerce): Asociar cada referencia de pago a una única orden mediante una restricción de unicidad en el almacén de órdenes, con procesamiento idempotente de las confirmaciones.
  - *preventivo* (pasarela de pago): Incluir la referencia de la orden y el monto dentro de la transacción y de la notificación firmada, de modo que la confirmación sea verificable contra una orden concreta.
  - *preventivo* (ecommerce): Validar que la referencia de pago confirmada corresponde a la orden, al monto y al cliente de la sesión antes de cambiar el estado a pagada.
  - *detectivo* (ecommerce): Generar un reporte y una alerta cuando una referencia de pago aparezca ligada a más de una orden o se reciba más de una confirmación para la misma referencia.
  - *correctivo* (ecommerce): Revertir la orden de alto valor sin pago propio, detener su preparación en delivery-api y recuperar el paquete si ya fue despachado.
- **Referencias y patrones:** CAPEC-39, CAPEC-277, AV-0032, S-05, S-26

<a id="av-0043"></a>
#### AV-0043 · Cambio del contenido del carrito entre el total mostrado y el registro de la orden

- **ID de origen:** AC-UC07-04 · **Ejecución:** Lote 2 · **Tema de riesgo:** R2
- **STRIDE:** T (R) — Manipulación
- **Actor:** Cliente que opera dos sesiones simultáneas del Marketplace (externo)
- **Elementos del DFD:** Marketplace, Pasarela de pago, Total de la orden, Almacén de órdenes del Marketplace, delivery-api · **Límites:** LC-1, LC-2, LC-6
- **Precondiciones:**
  - El carrito sigue siendo editable mientras el cliente está en la pasarela de pago
  - El total cobrado no queda bloqueado ni firmado al iniciar el pago
  - Al recibir la confirmación, el Marketplace registra la orden con el estado actual del carrito y no con el que se mostró y cobró
- **Cómo ocurre:**
  1. El cliente agrega un producto barato al carrito y llega al paso de pago, donde se muestra el total bajo
  2. Abre una segunda sesión en el mismo navegador o en otro dispositivo con la misma cuenta
  3. Inicia el pago en la primera sesión y paga el total bajo en la pasarela
  4. Mientras la pasarela procesa el pago, en la segunda sesión cambia el carrito por un producto caro, o aumenta la cantidad
  5. Llega la confirmación de pago, que cubre solo el total bajo
  6. El Marketplace arma la orden con el contenido actual del carrito, la registra como pagada y crea la orden de entrega con el producto caro
- **Vector práctico:** Con dos sesiones abiertas de su cuenta, el cliente edita el contenido y las cantidades del carrito en una de ellas durante el pago de la otra. Aprovecha que el Marketplace no congela el carrito ni compara el total cobrado con el valor de la orden que registra.
- **Impacto:** Entrega de productos de mayor valor que lo pagado, con orden de compra y orden de entrega incoherentes con el cobro. La discrepancia entre el total cobrado y la orden de entrega (S-26) hace difícil el reclamo posterior.
- **Riesgo:** medio (2×2). Requiere dos sesiones y una condición de carrera, y se asume que el carrito no se bloquea, aunque cada abuso entrega mercancía de más valor que lo pagado.
- **Controles:**
  - *preventivo* (ecommerce): Al iniciar el pago, congelar el carrito en una instantánea inmutable con su hash y total, bloquear su edición y crear la orden solo desde esa instantánea.
  - *preventivo* (ecommerce): Al recibir la confirmación, verificar que el hash y el total de la instantánea coinciden con lo cobrado y usar esa instantánea, no el carrito actual, para crear la orden de entrega.
  - *detectivo* (ecommerce): Alertar sobre modificaciones de carrito o sesiones simultáneas de la misma cuenta mientras hay un pago pendiente, y comparar el total cobrado contra los ítems de la orden y de la orden de entrega.
  - *correctivo* (ecommerce): Reconstruir la orden y la orden de entrega desde la instantánea pagada, o retener el despacho y cobrar la diferencia antes de enviar.
- **Referencias y patrones:** CAPEC-39, CWE-367, AV-0017, S-26, S-05

<a id="av-0044"></a>
#### AV-0044 · Cliente que desconoce el pago ante la pasarela tras recibir el producto y el comercio no puede probar la vinculación orden-pago-entrega

- **ID de origen:** AC-UC07-05 · **Ejecución:** Lote 2 · **Tema de riesgo:** R1
- **STRIDE:** R (S) — Repudio
- **Actor:** Cliente que usa un medio de pago propio o robado (externo)
- **Elementos del DFD:** Marketplace, Pasarela de pago, Medio de pago tokenizado, Confirmación de pago, Almacén de órdenes del Marketplace, delivery-api · **Límites:** LC-1, LC-6
- **Precondiciones:**
  - El Marketplace no conserva de forma inmutable la relación entre la orden, la confirmación de pago, el medio de pago tokenizado y la orden de entrega
  - La evidencia de entrega es débil, por ejemplo sin código de confirmación del cliente
  - La pasarela permite contracargos o disputas del titular del medio de pago
- **Cómo ocurre:**
  1. El cliente compra un producto de alto valor con una tarjeta propia o con una tarjeta ajena obtenida de forma ilícita
  2. La pasarela confirma el pago y el Marketplace registra la orden y la entrega
  3. Una vez recibido el producto, el cliente o el titular real de la tarjeta abre una disputa ante el banco, y afirma que no autorizó el cargo o que no recibió la compra
  4. El comercio intenta reunir la evidencia, pero no puede ligar la confirmación de pago con la orden y la entrega con una prueba confiable
  5. La disputa se resuelve a favor del titular y el comercio asume el contracargo
  6. El cliente conserva el producto
- **Vector práctico:** Con una tarjeta propia o una tarjeta ajena de origen ilícito, el cliente completa el pago en la pasarela y luego presenta una disputa o contracargo ante el banco emisor. Se apoya en que el comercio no tiene la referencia de pago, la orden y la evidencia de entrega ligadas en un registro inmutable.
- **Impacto:** Pérdida del valor del producto más las comisiones del contracargo. Aumenta el índice de disputas del comercio con la pasarela, lo que puede traer penalizaciones o la suspensión del servicio de cobro.
- **Riesgo:** alto (3×2). El contracargo con tarjeta propia o robada es un fraude frecuente y, sin evidencia ligada, se pierde el producto y se arriesgan penalizaciones de la pasarela.
- **Controles:**
  - *preventivo* (pasarela de pago): Aplicar autenticación reforzada del titular (3-D Secure) y reglas de riesgo en pagos de alto valor, cuentas nuevas o direcciones de envío inusuales.
  - *preventivo* (ecommerce): Guardar en un registro inmutable de solo anexado el vínculo entre orden, referencia de pago, medio de pago tokenizado, datos del dispositivo y orden de entrega.
  - *preventivo* (proveedor logístico): Exigir en la entrega el código de confirmación del cliente, con foto con marca de tiempo y ubicación, y entregar esta evidencia al ecommerce.
  - *detectivo* (ecommerce): Vigilar la tasa de disputas por cliente, medio de pago y dirección, y alertar sobre señales como cuentas nuevas con productos de alto valor.
  - *correctivo* (ecommerce): Presentar la representación de la disputa con el registro vinculado y la evidencia de entrega, y bloquear el cliente y el medio de pago implicados.
- **Referencias y patrones:** CAPEC-151, AV-0022, FE-01, S-26

<a id="av-0045"></a>
#### AV-0045 · Consulta de órdenes ajenas modificando el identificador de la orden en la confirmación o el seguimiento posterior al pago

- **ID de origen:** AC-UC07-06 · **Ejecución:** Lote 2 · **Tema de riesgo:** R7
- **STRIDE:** I — Divulgación de información
- **Actor:** Cliente autenticado con una orden propia (externo)
- **Elementos del DFD:** Marketplace, delivery-api, Orden de entrega, Almacén de órdenes del Marketplace · **Límites:** LC-1, LC-2
- **Precondiciones:**
  - El cliente tiene al menos una orden pagada y accede a la pantalla de confirmación o seguimiento
  - El identificador de la orden o de la orden de entrega es secuencial o predecible
  - El Marketplace o delivery-api no verifican que la orden consultada pertenezca al cliente autenticado
- **Cómo ocurre:**
  1. El cliente paga una orden y abre la confirmación o el seguimiento de su compra
  2. Con un proxy de interceptación identifica la petición que consulta la orden y el identificador de la orden o de la entrega
  3. Reemplaza el identificador por valores cercanos al suyo, de manera iterativa
  4. El servicio responde con el detalle de órdenes de otros clientes: productos, total, descuento, dirección, nombre y teléfono de contacto y modalidad de entrega
  5. El atacante recopila esos datos de forma masiva con una herramienta de repetición de peticiones
- **Vector práctico:** Con un proxy de interceptación y una herramienta de repetición de peticiones, el cliente modifica el identificador de orden en la consulta de confirmación o de seguimiento. Obtiene así el detalle de órdenes de terceros, porque no se valida la pertenencia del objeto al usuario autenticado.
- **Impacto:** Fuga de datos personales de clientes (dirección, teléfono, historial de compras) que sirve para suplantación, fraude de entrega y acoso, y que expone al comercio a sanciones por protección de datos y a daño reputacional.
- **Riesgo:** alto (2×3). Cambiar el identificador es trivial y automatizable si la autorización por objeto falta, y expone datos personales de muchos clientes con sanciones por protección de datos.
- **Controles:**
  - *preventivo* (ecommerce): Verificar en el servidor, en cada consulta de orden o seguimiento, que la orden pertenece al cliente autenticado, y usar identificadores aleatorios no secuenciales.
  - *preventivo* (ecommerce): Limitar las propiedades devueltas por la consulta de orden y de entrega a las necesarias para el cliente, sin exponer datos de terceros, y exigir en delivery-api una identidad de servicio con alcance por orden.
  - *detectivo* (ecommerce): Aplicar límites de tasa y alertar sobre enumeración de identificadores, es decir, muchas consultas de objetos distintos o respuestas 403 y 404 de una misma sesión.
  - *correctivo* (ecommerce): Revocar las sesiones y bloquear la cuenta que enumeró, corregir la autorización y notificar a los clientes afectados y a la autoridad según la normativa de protección de datos.
- **Referencias y patrones:** OWASP API1:2023 Broken Object Level Authorization, OWASP API3:2023 Broken Object Property Level Authorization, API1:2023, API3:2023, S-26

<a id="av-0046"></a>
#### AV-0046 · Empleado con acceso al registro de órdenes que marca una orden como pagada o altera su total para sustraer producto

- **ID de origen:** AC-UC07-07 · **Ejecución:** Lote 2 · **Tema de riesgo:** R3
- **STRIDE:** E (T, R) — Elevación de privilegios
- **Actor:** Empleado de operaciones o soporte con acceso de escritura al almacén de órdenes o a delivery-api (interno)
- **Elementos del DFD:** Almacén de órdenes del Marketplace, delivery-api, Orden de entrega, Confirmación de pago · **Límites:** LC-2
- **Precondiciones:**
  - Los perfiles de soporte u operaciones pueden editar el estado de pago, el total o el descuento de una orden, o crear órdenes de entrega, sin doble aprobación
  - No hay conciliación automática entre las órdenes marcadas como pagadas y los cobros de la pasarela
  - Existen dos registros de la misma compra que pueden quedar inconsistentes (S-26)
  - La bitácora de cambios es parcial o editable
- **Cómo ocurre:**
  1. El empleado crea una orden con una cuenta cómplice, o localiza una orden pendiente o cancelada
  2. Desde la consola interna cambia el estado de la orden a pagada, o reduce el total o aplica un descuento manual sin respaldo en la pasarela
  3. El cambio dispara la creación de la orden de entrega en delivery-api y el inicio de la preparación
  4. El producto sale hacia una dirección controlada por el empleado o su cómplice
  5. Si hay revisión, el empleado atribuye la diferencia a un error de la pasarela o a una falla de sincronización entre los dos registros
- **Vector práctico:** Desde la consola administrativa o el acceso a la base de datos de órdenes, el empleado edita el campo de estado de pago o el total de una orden que no tiene un cobro asociado. Su permiso de escritura le sirve para disparar la orden de entrega en delivery-api y la bitácora insuficiente impide rastrear su acción.
- **Impacto:** Pérdida de mercancía sin cobro, con registros que parecen legítimos. El fraude es difícil de atribuir y puede repetirse durante meses antes de que se detecte en la conciliación.
- **Riesgo:** alto (2×3). Un empleado con escritura sin doble aprobación ni conciliación puede repetir el fraude durante meses con registros que parecen legítimos.
- **Controles:**
  - *preventivo* (ecommerce): Impedir la edición manual del estado de pago, el total y el descuento: solo la confirmación verificada de la pasarela puede marcar pagada una orden, y los ajustes excepcionales requieren doble aprobación.
  - *preventivo* (ecommerce): Aplicar mínimo privilegio a perfiles de soporte y operaciones, con bitácora de auditoría inmutable de solo anexado, almacenada fuera del control de quienes editan órdenes.
  - *preventivo* (proveedor logístico): Aceptar para despacho solo órdenes de entrega originadas por delivery-api y firmadas, y permitir que el ecommerce pida la retención de un paquete.
  - *detectivo* (ecommerce): Conciliar a diario las órdenes pagadas con las liquidaciones de la pasarela y alertar sobre cambios manuales de estado o total y sobre direcciones de entrega repetidas por empleado.
  - *correctivo* (ecommerce): Suspender el acceso del empleado, congelar las órdenes involucradas, solicitar al proveedor la retención o devolución de los paquetes en tránsito y abrir una investigación.
- **Referencias y patrones:** CAPEC-122, OWASP Top 10 A01:2021 Broken Access Control, FE-09, S-26, S-05

### UC-08 Preparación y empaquetado en almacén

<a id="av-0047"></a>
#### AV-0047 · Registro de peso y dimensiones falsos en el empaquetado para desviar costos de transporte y ocultar sustituciones

- **ID de origen:** AC-UC08-02 · **Ejecución:** Lote 2 · **Tema de riesgo:** R1
- **STRIDE:** T (R) — Manipulación
- **Actor:** Personal de almacén que registra peso y dimensiones reales del paquete (interno)
- **Elementos del DFD:** F14, delivery-api, Peso y dimensiones reales, Etiqueta y código del paquete, Red de logística · **Límites:** LC-5
- **Precondiciones:**
  - El peso y las dimensiones reales los digita el empleado, sin lectura automática de báscula ni contraste con los valores teóricos del producto
  - delivery-api acepta los datos de empaquetado sin validar desviaciones frente a lo cotizado
  - El proveedor logístico usa esos datos para asignar vehículo y tarifa
- **Cómo ocurre:**
  1. El empleado prepara un producto voluminoso y ve que el peso o volumen real difiere del cotizado, o decide sustituir parte del contenido
  2. Digita en el sistema del almacén un peso y unas dimensiones distintos de los reales, por ejemplo los teóricos del catálogo o menores
  3. Escanea la etiqueta y la orden pasa a listo para recolección con esos datos
  4. delivery-api almacena los datos sin alertar por desviación y los transmite a la red de logística
  5. El proveedor planifica transporte con datos erróneos y aplica recargos o rechaza la carga, o la diferencia de peso queda sin explicación y se atribuye a otro actor
- **Vector práctico:** Edición manual de los campos de peso y dimensiones en el formulario de empaquetado del almacén. El dato manipulado son esos valores registrados en la orden de entrega, que se envían a delivery-api y al proveedor sin contraste con una báscula, el peso teórico o una foto.
- **Impacto:** Costos de transporte y recargos no previstos, asignación errónea de vehículos, retrasos o rechazos de carga y pérdida de la trazabilidad para detectar sustituciones de contenido.
- **Riesgo:** medio (2×2). El empleado digita peso y dimensiones sin báscula ni contraste con el valor teórico, lo que hace la manipulación fácil, pero el daño se limita a recargos, rechazos de carga y pérdida de trazabilidad.
- **Controles:**
  - *preventivo* (ecommerce): Integrar báscula y dimensionador con lectura automática hacia el formulario de empaquetado, con los campos de peso y dimensiones no editables a mano; cualquier excepción manual exige motivo y aprobación del supervisor.
  - *preventivo* (ecommerce): Validar en delivery-api el peso y las dimensiones recibidos por F14 contra el peso y volumen teóricos del producto con una tolerancia definida, y bloquear el paso a listo para recolección cuando la desviación la supere hasta que haya revisión de una segunda persona.
  - *detectivo* (proveedor logístico): Pesar y medir el bulto en la recolección y enviar a delivery-api un evento de discrepancia cuando difiera de lo declarado por el almacén más allá de la tolerancia.
  - *detectivo* (ecommerce): Reporte periódico de desviaciones entre lo registrado y el peso teórico, agrupado por empleado y turno, con alerta ante patrones repetidos o sesgo sistemático a la baja.
  - *correctivo* (ecommerce): Reabrir la orden con discrepancia, volver a pesar y medir con evidencia fotográfica, corregir los datos en delivery-api, y atribuir y reasignar al almacén los recargos generados por el dato falso.
- **Referencias y patrones:** CAPEC-39 Manipulating Opaque Client-based Data Tokens, OWASP API Security Top 10 API6:2023, AV-0033, FE-09

<a id="av-0048"></a>
#### AV-0048 · Transición de estado fuera del rol de preparación ejecutada por personal de almacén para cerrar o encubrir órdenes

- **ID de origen:** AC-UC08-03 · **Ejecución:** Lote 2 · **Tema de riesgo:** R3
- **STRIDE:** E (T) — Elevación de privilegios
- **Actor:** Personal de almacén con cuenta nominal de preparación en el sistema del almacén o en el delivery-admin-front (interno)
- **Elementos del DFD:** F14, delivery-api, delivery-admin-front, Estado de la orden · **Límites:** LC-5
- **Precondiciones:**
  - El rol de preparación del almacén opera sobre delivery-api por F14 o desde el delivery-admin-front (S-27)
  - delivery-api valida la autenticación de la cuenta pero no restringe qué transiciones de estado puede ejecutar el rol de preparación, de modo que permite estados posteriores como despachada, entregada, cancelada o devuelta
  - Los estados finales no requieren motivo, evidencia ni aprobación de una segunda persona
  - No existe alerta cuando el estado contradice los eventos de la integración logística (UC-10)
  - Existen órdenes con producto sustraído o faltante que el empleado quiere cerrar
- **Cómo ocurre:**
  1. El empleado inicia sesión con su propia cuenta de preparación en el sistema del almacén o en el delivery-admin-front
  2. Localiza una orden con faltante de producto, por ejemplo una que ya recolectó el proveedor o una cuyo producto sustrajo
  3. Selecciona manualmente un estado que corresponde a otros roles, como entregada, devuelta o cancelada, en lugar del estado de listo para recolección
  4. delivery-api acepta la transición porque valida solo la identidad de la cuenta y no la autorización por tipo de transición, y no pide motivo ni aprobación
  5. La orden queda cerrada en un estado final que contradice los eventos de logística, y la excepción deja de aparecer en la cola de incidencias
  6. El faltante queda oculto hasta que el cliente reclama, y la contradicción con los eventos del proveedor solo se detecta en una conciliación posterior
- **Vector práctico:** Con su cuenta de preparación en el sistema del almacén o en el delivery-admin-front, el empleado usa la función de cambio manual de estado para fijar un estado final que su rol no debería poder asignar. El dato manipulado es el estado de la orden en delivery-api, con una transición que excede el rol de preparación, sin motivo ni evidencia obligatorios.
- **Impacto:** Órdenes cerradas como entregadas o devueltas sin que el evento físico ocurriera, encubrimiento de sustracciones, reclamos de clientes sin evidencia a favor de la empresa y estados que contradicen los eventos del proveedor logístico.
- **Riesgo:** alto (2×3). delivery-api no restringe las transiciones por rol y los estados finales no exigen motivo ni aprobación, así que un empleado puede cerrar o encubrir órdenes con faltante y generar reclamos sin evidencia y estados que contradicen al proveedor.
- **Controles:**
  - *preventivo* (ecommerce): Aplicar en delivery-api una matriz de transiciones permitidas por rol, de modo que el rol de preparación solo pueda pasar de en preparación a empaquetada y a listo para recolección, y rechazar en servidor cualquier otro estado (entregada, devuelta, cancelada, despachada).
  - *preventivo* (ecommerce): Exigir motivo, evidencia adjunta y aprobación de una segunda persona con rol distinto para estados finales, mantener cuentas nominales con MFA en el delivery-admin-front y prohibir usuarios compartidos.
  - *detectivo* (ecommerce): Alerta automática cuando el estado de una orden contradiga los eventos de la integración logística (UC-10), por ejemplo entregada sin evento de entrega del proveedor o cancelada tras la recolección.
  - *detectivo* (ecommerce): Registro de auditoría inmutable de cada cambio de estado, con cuenta, origen (F14 o admin-front), motivo y hora, y revisión periódica de cambios fuera de horario o concentrados en un mismo empleado.
  - *correctivo* (ecommerce): Revertir el estado de las órdenes cambiadas sin autorización con base en los eventos del proveedor, reabrir la incidencia, revocar o reducir permisos de la cuenta implicada y conciliar la orden con la evidencia de escaneo del proveedor.
  - *correctivo* (proveedor logístico): Entregar a solicitud el histórico de eventos de escaneo y recolección de las órdenes afectadas para reconstruir el estado real y resolver el reclamo del cliente.
- **Referencias y patrones:** CAPEC-122 Privilege Abuse, OWASP API Security Top 10 API5:2023 Broken Function Level Authorization, FE-15, AV-0006

<a id="av-0049"></a>
#### AV-0049 · Sustracción del producto en almacén encubierta con registro falso de empaquetado, peso y estado

- **ID de origen:** AC-UC08-01 · **Ejecución:** Lote 2 · **Tema de riesgo:** R1
- **STRIDE:** T (R) — Manipulación
- **Actor:** Personal de almacén con acceso a la cola de preparación y a la confirmación de empaquetado (interno)
- **Elementos del DFD:** F14, delivery-api, Almacén, Estado de la orden, Peso y dimensiones reales, Etiqueta y código del paquete · **Límites:** LC-5
- **Precondiciones:**
  - El empleado puede registrar peso y dimensiones, escanear la etiqueta y cambiar la orden a listo para recolección desde el sistema del almacén o el delivery-admin-front (S-27)
  - Existen órdenes de productos voluminosos de alto valor en la cola de preparación
  - SN-UC08-01: delivery-api acepta la confirmación de empaquetado recibida por F14 sin contrastar el peso y las dimensiones registrados con el peso teórico del producto y sin exigir foto del paquete
  - SN-UC08-02: el traspaso del paquete al proveedor logístico no exige un escaneo conjunto de ambas partes que verifique el contenido o el peso del bulto
- **Cómo ocurre:**
  1. El empleado identifica en la cola de preparación una orden de un producto voluminoso de alto valor y la toma para prepararla
  2. Retira el producto del inventario del almacén y arma un bulto de relleno con dimensiones aproximadas a las del original
  3. Registra en el sistema de preparación el peso y las dimensiones teóricas del producto, no los del bulto real, y confirma el empaquetado
  4. Imprime una etiqueta con el código del paquete, la pega en el bulto de relleno y la escanea, de modo que el escaneo queda asociado a la orden
  5. delivery-api cambia la orden a listo para recolección y lo comunica al almacén y al proveedor por F14
  6. El proveedor recoge el bulto; cuando el cliente reclama, la pérdida aparece como faltante en tránsito o producto equivocado, sin evidencia que permita ubicar dónde se sustrajo
- **Vector práctico:** Con su cuenta de empleado en el sistema del almacén, el empleado registra en la confirmación de empaquetado un peso y unas dimensiones que no corresponden al bulto real, escanea una etiqueta pegada a un bulto de relleno y mueve la orden a listo para recolección. Los datos manipulados son el peso y las dimensiones registrados, el código de etiqueta escaneado y el estado de la orden, que delivery-api acepta sin contraste con el contenido físico (SN-UC08-01 y SN-UC08-02).
- **Impacto:** Pérdida del inventario de alto valor, imposibilidad de atribuir el faltante al almacén frente al proveedor logístico, disputas de responsabilidad en tránsito y reembolsos al cliente que asume la empresa.
- **Riesgo:** alto (2×3). El empleado puede registrar peso falso y escanear una etiqueta sobre un bulto de relleno sin contraste físico ni escaneo conjunto en el traspaso, y la pérdida de producto voluminoso de alto valor resulta imposible de atribuir al almacén.
- **Controles:**
  - *preventivo* (ecommerce): Exigir en la confirmación de empaquetado el peso leído automáticamente de una báscula integrada y una foto del bulto cerrado con la etiqueta visible, y contrastar ambos con el peso teórico del producto en delivery-api antes de pasar a listo para recolección.
  - *preventivo* (ecommerce): Para productos voluminosos de alto valor, exigir verificación de contenido por una segunda persona (doble control) y restringir la impresión de etiquetas a la orden activa para impedir reimpresiones sin autorización.
  - *preventivo* (proveedor logístico): Realizar un escaneo conjunto en el traspaso de custodia, con verificación del peso del bulto por el proveedor y confirmación firmada por ambas partes, y registrar en delivery-api cualquier diferencia respecto al peso declarado.
  - *detectivo* (ecommerce): Conciliación diaria entre órdenes marcadas como listas o despachadas y paquetes escaneados y recibidos por el proveedor, con análisis de faltantes y diferencias de peso concentrados por turno o empleado.
  - *detectivo* (proveedor logístico): Reportar a delivery-api las diferencias de peso o de estado del bulto detectadas al recibirlo, y compartir con el ecommerce la conciliación de recepciones frente a despachos.
  - *correctivo* (ecommerce): Abrir una investigación con la foto, el peso, el registro de escaneos y la grabación del puesto de empaque para atribuir la sustracción, bloquear el acceso del empleado implicado, y reponer el producto o reembolsar al cliente con recuperación posterior de la pérdida.
- **Referencias y patrones:** CAPEC-148 Content Spoofing, OWASP Logging and Monitoring Failures, FE-09, AV-0006

### UC-09 Recolección y transporte por el proveedor logístico

<a id="av-0050"></a>
#### AV-0050 · Paquete sustraído en un centro de distribución encubierto con escaneos de tránsito falsos

- **ID de origen:** AC-UC09-01 · **Ejecución:** Lote 2 · **Tema de riesgo:** R1
- **STRIDE:** T (R) — Manipulación
- **Actor:** Personal de centro de distribución (interno de tercero)
- **Elementos del DFD:** Red de logística, logistic, F18, Eventos de escaneo · **Límites:** LC-4, LC-5
- **Precondiciones:**
  - El empleado tiene un escáner o usuario con permiso para registrar eventos en el centro de distribución
  - El siguiente punto de control no concilia lo que se despacha contra lo que se recibe
  - No hay peso ni foto del paquete en cada escaneo (S-27)
- **Cómo ocurre:**
  1. El empleado identifica en el centro un paquete voluminoso de alto valor por su etiqueta y su peso
  2. Retira el paquete físico del flujo y lo saca del centro
  3. Con su usuario del escáner registra el evento de salida hacia el siguiente centro, como si el paquete hubiera continuado
  4. logistic guarda el evento y lo reenvía a delivery-api (F18), por lo que la orden aparece en tránsito
  5. El paquete nunca llega al siguiente punto y la orden se marca como fallida o perdida días después
  6. La pérdida se atribuye al tramo siguiente o al proveedor en general, y el reembolso lo asume el ecommerce
- **Vector práctico:** Desde su escáner autenticado, el empleado registra un evento de salida sobre el código del paquete sin que exista movimiento físico, y el dato manipulado es el evento de escaneo y la ubicación asociada al paquete.
- **Impacto:** Pérdida del producto y reembolso o reenvío a cargo del ecommerce. Trazabilidad falsa que impide ubicar dónde ocurrió el faltante y disputa contractual con el proveedor logístico.
- **Riesgo:** medio (2×2). El empleado ya tiene un escáner autenticado y no hay peso, foto ni conciliación entre puntos, así que sustraer un paquete es fácil, pero afecta a un paquete por vez.
- **Controles:**
  - *preventivo* (proveedor logístico): Exigir en cada escaneo de salida del centro de distribución el peso y una foto del paquete, y rechazar en logistic eventos sin esa evidencia o con peso fuera de tolerancia respecto al registrado en el despacho.
  - *preventivo* (proveedor logístico): Confirmar el traspaso entre centros con escaneo de recepción en el punto siguiente, de modo que un evento de salida sin recepción correlacionada genere un estado 'custodia no confirmada' y no 'en tránsito'.
  - *detectivo* (proveedor logístico): Conciliar automáticamente cada hora los eventos de salida contra los de recepción por tramo, y alertar cuando un paquete supere el tiempo de tránsito esperado entre centros o haya salidas sin recepción concentradas en un operario o turno.
  - *detectivo* (ecommerce): Recibir en delivery-api (F18) el peso, la foto y el identificador del operario de cada evento, y comparar la trayectoria de los eventos con los tiempos esperados de la ruta para marcar órdenes con tránsito anómalo.
  - *correctivo* (ecommerce): Congelar el reembolso o reenvío hasta que el proveedor entregue la evidencia de custodia del último escaneo verificado, y activar la cláusula contractual de responsabilidad por pérdida en el tramo donde se perdió la evidencia.
- **Referencias y patrones:** CAPEC-220, OWASP API6:2023, FE-09, FE-07, AV-0001

<a id="av-0051"></a>
#### AV-0051 · Negación de recepción del paquete en el traspaso almacén-proveedor

- **ID de origen:** AC-UC09-02 · **Ejecución:** Lote 2 · **Tema de riesgo:** R1
- **STRIDE:** R (T) — Repudio
- **Actor:** Empresa de logística (personal de recolección) (interno de tercero)
- **Elementos del DFD:** F15, Red de logística, logistic · **Límites:** LC-5
- **Precondiciones:**
  - El traspaso de custodia en el almacén no se confirma con un escaneo de ambas partes
  - No hay conciliación diaria entre despachos del almacén y recepciones del proveedor
  - El almacén solo conserva su propio registro de despacho
- **Cómo ocurre:**
  1. El repartidor o el personal de recolección llega al almacén para recoger varios paquetes
  2. Se lleva uno o más paquetes pero escanea solo una parte, o no escanea la entrega en logistic
  3. El almacén ya marcó la orden como lista para recolección y la da por despachada
  4. Después el proveedor afirma que nunca recibió ese paquete, y el almacén no tiene prueba independiente de la entrega
  5. El paquete se desvía y la responsabilidad de la pérdida queda sin atribuir
  6. El ecommerce no puede reclamar la penalización contractual ni demostrar en qué tramo se perdió
- **Vector práctico:** El operario de recolección omite el escaneo en la entrega y sustrae el paquete, y el dato manipulado es la ausencia del registro de recolección en logistic frente al registro de despacho del almacén.
- **Impacto:** Pérdida de producto sin responsable demostrable, reembolsos al cliente y litigio con el proveedor sin evidencia de custodia.
- **Riesgo:** medio (2×2). Sin escaneo conjunto ni conciliación diaria, omitir el escaneo en la recolección es sencillo y deja la pérdida sin responsable, con impacto limitado a los paquetes de cada recolección.
- **Controles:**
  - *preventivo* (ecommerce): Implantar escaneo conjunto en el traspaso F15: el almacén solo cierra la orden como despachada cuando el operario del proveedor escanea cada paquete en logistic y el sistema devuelve una confirmación firmada con operario, hora y manifiesto.
  - *preventivo* (proveedor logístico): Emitir un manifiesto de recolección por visita con el listado de paquetes y exigir que el operario del proveedor lo contrafirme digitalmente, con peso y foto del lote al salir del almacén.
  - *detectivo* (ecommerce): Ejecutar una conciliación diaria automática entre órdenes despachadas por el almacén y paquetes recibidos en logistic, con alerta por cada diferencia no resuelta en 24 horas.
  - *detectivo* (ecommerce): Revisar cámaras del muelle de carga y comparar el recuento físico de bultos cargados contra los escaneos de cada visita.
  - *correctivo* (proveedor logístico): Aplicar la penalización contractual con base en la contrafirma del manifiesto o en su ausencia, e investigar con el proveedor al operario de la visita para recuperar el paquete.
- **Referencias y patrones:** CAPEC-220, FE-09, AV-0002

<a id="av-0052"></a>
#### AV-0052 · Retiro del paquete en el almacén por alguien que se hace pasar por el proveedor logístico

- **ID de origen:** AC-UC09-04 · **Ejecución:** Lote 2 · **Tema de riesgo:** R1
- **STRIDE:** S (T) — Suplantación
- **Actor:** Atacante externo con uniforme e identificación falsos del proveedor (externo)
- **Elementos del DFD:** F15, Red de logística · **Límites:** LC-5
- **Precondiciones:**
  - El almacén entrega paquetes a quien se presenta como transportista sin validar su identidad contra la asignación de recolección
  - El atacante conoce los horarios de recolección, o tiene un dato de una orden real
  - El escaneo de entrega lo hace un dispositivo que acepta cualquier operario
- **Cómo ocurre:**
  1. El atacante observa o averigua el horario de recolección del proveedor en el almacén
  2. Llega antes que el proveedor real con un vehículo y una identificación que imita la del proveedor
  3. Afirma que viene a recoger paquetes de órdenes concretas y presenta datos reales de las órdenes obtenidos de una etiqueta o de un contacto interno
  4. El personal del almacén entrega los paquetes y registra que fueron entregados al proveedor
  5. Cuando llega el repartidor real, el almacén ya no tiene los paquetes y las órdenes aparecen como entregadas al proveedor
  6. El atacante revende los productos y el ecommerce reclama a un proveedor que nunca los recibió
- **Vector práctico:** El atacante se presenta en el almacén con identificación falsa y datos reales de órdenes y obtiene el paquete físico, y el dato falsificado es la identidad del recolector en el traspaso F15.
- **Impacto:** Pérdida de varios paquetes de una sola vez, disputa entre almacén y proveedor y reembolsos masivos a clientes.
- **Riesgo:** alto (2×3). Un impostor con identificación falsa y datos reales de órdenes puede llevarse varios paquetes de una vez si el almacén no valida al recolector, lo que genera pérdidas y reembolsos masivos.
- **Controles:**
  - *preventivo* (proveedor logístico): Enviar al almacén antes de cada visita la identidad esperada del recolector (nombre, documento, placa del vehículo y código de recolección de un solo uso), y entregar paquetes solo si coincide con la asignación.
  - *preventivo* (ecommerce): Exigir al recolector el escaneo de su credencial en el dispositivo del proveedor y un código de recolección de un solo uso vinculado al manifiesto, con registro de la identificación y foto del vehículo en el muelle.
  - *preventivo* (ecommerce): No entregar paquetes ante visitas fuera del horario asignado o sin asignación en logistic, y escalar a un supervisor antes de cualquier excepción.
  - *detectivo* (proveedor logístico): Alertar cuando se registre un traspaso F15 con un operario no asignado a la ruta, o cuando el proveedor no reconozca la recepción de un manifiesto en pocas horas.
  - *correctivo* (ecommerce): Activar un protocolo de incidente que bloquee las órdenes afectadas, notifique al proveedor y a las autoridades con las grabaciones del muelle, y reenvíe los pedidos a los clientes sin cargo mientras se reclama el valor.
- **Referencias y patrones:** CAPEC-220, FE-09

<a id="av-0053"></a>
#### AV-0053 · Venta de datos personales del cliente leídos en etiquetas y escaneos durante el transporte

- **ID de origen:** AC-UC09-05 · **Ejecución:** Lote 2 · **Tema de riesgo:** R7
- **STRIDE:** I — Divulgación de información
- **Actor:** Personal de centro de distribución o repartidor (interno de tercero)
- **Elementos del DFD:** Red de logística, logistic, Etiqueta y código del paquete, Eventos de escaneo · **Límites:** LC-4, LC-5
- **Precondiciones:**
  - La etiqueta impresa o la pantalla del escáner muestran nombre, dirección y teléfono del cliente
  - No hay control de volumen ni registro de consultas por operario
  - El operario tiene acceso de lectura a muchos paquetes del centro
- **Cómo ocurre:**
  1. El empleado trabaja en un turno con acceso a los escáneres y a las etiquetas de decenas de paquetes
  2. Fotografía las etiquetas o consulta con el escáner el detalle de los paquetes de productos voluminosos y de alto valor
  3. Reúne nombre, dirección, teléfono y qué producto compró cada cliente
  4. Vende la lista a un tercero, o la usa para ir a robar a domicilio
  5. Los clientes sufren llamadas fraudulentas o robos, y el origen de la fuga no se identifica en los registros
- **Vector práctico:** El empleado usa su cuenta de escáner y la cámara de su teléfono para leer y copiar el detalle de paquetes ajenos, y el dato obtenido es la información de destinatario y dirección de las etiquetas.
- **Impacto:** Fuga de datos personales de clientes, riesgo físico para quienes recibieron productos de alto valor, sanciones por protección de datos y pérdida de confianza en el ecommerce.
- **Riesgo:** alto (2×3). El personal ve los datos completos del cliente en etiquetas y escáneres sin control de volumen, y la fuga puede causar robos a domicilio y sanciones por protección de datos.
- **Controles:**
  - *preventivo* (ecommerce): Reemplazar los datos personales de la etiqueta por un código opaco y mostrar al operario solo lo necesario para su tramo, de modo que nombre, teléfono y dirección completa solo se vean en la entrega final por el repartidor asignado.
  - *preventivo* (proveedor logístico): Limitar en logistic la consulta de detalle de paquetes al centro y turno del operario, con tope de consultas por hora, y prohibir teléfonos personales en la zona de clasificación.
  - *detectivo* (proveedor logístico): Registrar cada consulta de detalle por operario y alertar sobre consultas masivas, sobre productos de alto valor o sobre paquetes que no están en el flujo asignado al operario.
  - *detectivo* (ecommerce): Sembrar datos de control (clientes señuelo) en envíos de prueba para detectar el origen de una fuga cuando se usen en contactos fraudulentos.
  - *correctivo* (ecommerce): Ante una sospecha de fuga, suspender al operario, notificar a los clientes expuestos y a la autoridad de protección de datos en los plazos legales, y exigir al proveedor el informe de las consultas del turno.
- **Referencias y patrones:** CAPEC-569, OWASP API9:2023, FE-09

<a id="av-0054"></a>
#### AV-0054 · Retención deliberada de paquetes en un centro de distribución para frenar entregas

- **ID de origen:** AC-UC09-06 · **Ejecución:** Lote 2 · **Tema de riesgo:** R3
- **STRIDE:** D (T) — Denegación de servicio
- **Actor:** Personal de centro de distribución inconforme o sobornado por un competidor (interno de tercero)
- **Elementos del DFD:** Red de logística, logistic, F18, Estado de la orden de entrega · **Límites:** LC-4, LC-5
- **Precondiciones:**
  - El empleado puede registrar eventos de escaneo y excepciones en el centro
  - No hay alerta por paquetes sin movimiento que superen el tiempo máximo en un punto de control
  - delivery-api muestra al cliente el último estado enviado por logistic
- **Cómo ocurre:**
  1. El empleado selecciona un lote de paquetes de un mismo comercio o de un tipo de producto
  2. Los deja sin escaneo de salida o registra una excepción, como dirección incorrecta o paquete dañado, que detiene su avance
  3. logistic reenvía el estado a delivery-api (F18) y el Marketplace muestra el estado al cliente
  4. Los paquetes se acumulan en el centro y las entregas se retrasan o se cancelan
  5. Los clientes reclaman y piden reembolsos, y la reputación del ecommerce cae mientras se investiga la causa
- **Vector práctico:** Desde su usuario de escáner, el empleado registra excepciones falsas o no registra la salida de un lote de paquetes, y el dato manipulado es el estado y los eventos de escaneo de esas órdenes.
- **Impacto:** Incumplimiento de plazos de entrega, cancelaciones y reembolsos masivos, daño reputacional y costos de reenvío para el ecommerce.
- **Riesgo:** bajo (1×2). Requiere un empleado inconforme o sobornado y es detectable por tiempos, pero un lote retenido provoca retrasos, reembolsos y daño reputacional.
- **Controles:**
  - *preventivo* (proveedor logístico): Exigir evidencia (foto y motivo codificado) para registrar excepciones como dirección incorrecta o paquete dañado, y limitar cuántas excepciones por turno puede registrar cada operario sin aprobación de un supervisor.
  - *detectivo* (proveedor logístico): Definir un tiempo máximo de permanencia por punto de control y alertar sobre paquetes sin movimiento que lo superen, con un tablero que agrupe los retenidos por comercio y por centro.
  - *detectivo* (ecommerce): Monitorear en delivery-api (F18) la proporción de excepciones y de órdenes estancadas por centro de distribución y comercio, y alertar ante picos respecto al histórico.
  - *correctivo* (ecommerce): Escalar el lote retenido al proveedor con un plazo de liberación, notificar proactivamente a los clientes afectados, y reencaminar las órdenes por otro centro o por otro proveedor.
- **Referencias y patrones:** OWASP API6:2023, AV-0008

<a id="av-0055"></a>
#### AV-0055 · Reasignación de ruta y repartidor para desviar un paquete de alto valor a un cómplice, ocultada como cambio operativo normal

- **ID de origen:** AC-UC09-03 · **Ejecución:** Lote 2 · **Tema de riesgo:** R3
- **STRIDE:** T (R) — Manipulación
- **Actor:** Personal de centro de distribución con permiso legítimo para modificar la asignación de ruta y repartidor (interno de tercero)
- **Elementos del DFD:** Red de logística, logistic, Asignación de ruta y repartidor, Eventos de escaneo · **Límites:** LC-4, LC-5
- **Precondiciones:**
  - El rol del empleado incluye de forma legítima el permiso de reasignar ruta y repartidor; no se asume escalada de privilegios ni acceso fuera de su rol
  - logistic no exige aprobación de un segundo rol ni motivo obligatorio para reasignar paquetes de alto valor
  - No hay alerta por reasignaciones de paquetes voluminosos de alto valor ni por reasignaciones repetidas del mismo paquete
  - El repartidor cómplice pertenece a la misma red logística y tiene acceso a la ruta asignada
- **Cómo ocurre:**
  1. El empleado consulta en logistic los paquetes que están en su centro de distribución y elige uno voluminoso de alto valor
  2. Con su usuario y permiso legítimos modifica la asignación de ruta y repartidor del paquete, dejando al repartidor cómplice o una ruta que no cubre la dirección de entrega
  3. El cómplice recibe el paquete en el centro, se escanea la salida y lo retira del circuito sin intentar la entrega
  4. logistic envía a delivery-api por la integración un estado de fallido o una entrega con evidencia débil, y el Marketplace lo muestra al cliente
  5. La reasignación queda en el historial como un cambio operativo rutinario, sin motivo ni segunda aprobación, y el empleado puede negar la intención
  6. El cliente reclama que no recibió el producto y el ecommerce paga reembolso o reenvío, mientras empleado y cómplice se reparten el valor
- **Vector práctico:** Desde la consola de logistic, con su usuario legítimo, el empleado edita el campo de repartidor y ruta asignados al paquete elegido. El dato manipulado es la asignación de ruta y repartidor, que determina quién tiene la custodia del paquete. La acción es válida para su rol y no genera alerta.
- **Impacto:** Pérdida del producto de alto valor, reembolso o reenvío y daño reputacional para el ecommerce. La atribución es difícil porque la acción parece una operación legítima del centro de distribución, y el abuso de un permiso legítimo queda sin trazabilidad útil del motivo.
- **Riesgo:** medio (1×3). Requiere la colusión de un empleado con permiso legítimo y un repartidor, pero el valor del paquete es alto y la acción parece operación normal, lo que dificulta la atribución.
- **Controles:**
  - *preventivo* (proveedor logístico): Exigir en logistic la aprobación de un segundo rol y un motivo obligatorio codificado para reasignar ruta o repartidor de paquetes por encima de un valor o volumen umbral, y bloquear reasignaciones a rutas que no cubran la dirección de entrega.
  - *preventivo* (ecommerce): Compartir con el proveedor, al despachar, el indicador de alto valor del paquete para que se apliquen las reglas de doble aprobación y se exija el código de confirmación del cliente en la entrega.
  - *detectivo* (proveedor logístico): Alertar por reasignaciones de paquetes de alto valor, reasignaciones repetidas del mismo paquete, y pares recurrentes empleado–repartidor con entregas fallidas o reclamadas.
  - *detectivo* (ecommerce): Conciliar periódicamente el historial de reasignaciones de logistic contra los reclamos de no recibido y los estados fallidos en delivery-api, y analizar relaciones entre repartidores, centros y clientes que reclaman.
  - *correctivo* (ecommerce): Retener el reembolso hasta recibir del proveedor el historial de custodia con el motivo de cada reasignación, aplicar la responsabilidad contractual por pérdida y suspender a los operarios implicados durante la investigación.
- **Referencias y patrones:** OWASP API6:2023, STRIDE T y R sobre almacén de datos de asignaciones, FE-08, FE-09, AV-0002

### UC-10 Actualización de estados por la integración logística

<a id="av-0056"></a>
#### AV-0056 · Evento de estado "entregado" falsificado con la credencial de integración filtrada

- **ID de origen:** AC-UC10-01 · **Ejecución:** Lote 2 · **Tema de riesgo:** R4
- **STRIDE:** S (T, E) — Suplantación
- **Actor:** Atacante externo que obtiene la credencial de servicio compartida de la integración logística (externo)
- **Elementos del DFD:** logistic, delivery-api, Marketplace · **Límites:** LC-4
- **Precondiciones:**
  - La credencial de servicio de la integración es compartida entre sistemas y no está ligada a un origen de red ni a una firma por evento (S-06).
  - El atacante obtiene la credencial por una fuga en un repositorio, en un log, en un correo o en un equipo del proveedor.
  - El atacante conoce o enumera identificadores de órdenes de entrega, por ejemplo por una orden propia o por un número predecible.
  - delivery-api acepta el estado "entregado" sin comprobar que haya escaneos previos de recolección o tránsito (S-16).
- **Cómo ocurre:**
  1. El atacante identifica una orden de alto valor que está en preparación o en tránsito.
  2. Con la credencial obtenida y una herramienta cliente HTTP, envía a delivery-api un evento de estado "entregado" para esa orden. Incluye una marca de tiempo plausible y una ubicación cercana a la dirección de destino.
  3. delivery-api autentica la credencial como la integración legítima y actualiza el estado sin contrastarlo con los escaneos de la red de logística.
  4. El Marketplace muestra "entregado" al cliente y se cierra la ventana de seguimiento.
  5. El paquete sigue en la red logística, o el atacante lo intercepta o lo redirige por otra vía. El cliente reclama que no recibió nada y no hay una cadena de eventos que respalde la disputa.
- **Vector práctico:** Cliente HTTP con la credencial de integración filtrada, usado desde una IP no habitual. Manipula el campo estado de entrega (valor "entregado"), junto con el identificador de la orden, la marca de tiempo y la ubicación reportada en el evento enviado a delivery-api.
- **Impacto:** Cierre falso de órdenes y pérdida del seguimiento real. Se generan reclamos, reembolsos o reenvíos a cargo del ecommerce y se facilita el robo o el desvío de paquetes. Se pierde la confianza en el estado mostrado al cliente.
- **Riesgo:** alto (2×3). La credencial compartida y sin firma por evento (S-06) hace plausible su fuga, y un 'entregado' falso cierra la orden y deja al ecommerce sin evidencia para la disputa.
- **Controles:**
  - *preventivo* (ecommerce): Reemplazar la credencial compartida por credenciales por sistema con mTLS o firma HMAC por evento (con marca de tiempo) que delivery-api verifique en LC-4, y restringir el endpoint de eventos a la lista de IPs del proveedor.
  - *preventivo* (ecommerce): Validar en delivery-api la máquina de estados: solo aceptar 'entregado' si existen antes los eventos 'recolectado' y 'en reparto' de la misma orden, con marcas de tiempo coherentes y ubicación dentro de un radio razonable del destino.
  - *preventivo* (proveedor logístico): Firmar cada evento en el origen y exponer una API de verificación contra los escaneos reales de la red logística, y rotar la credencial cada cierto tiempo.
  - *detectivo* (ecommerce): Alertar sobre eventos 'entregado' sin escaneos previos, desde IPs fuera de la lista habitual o con secuencias imposibles, y conciliar a diario los estados de delivery-api con el registro de escaneos del proveedor.
  - *correctivo* (ecommerce): Revocar y rotar de inmediato la credencial comprometida, revertir los estados de las órdenes afectadas a partir de la conciliación y retener el reembolso o reenvío hasta confirmar la entrega con el proveedor.
- **Referencias y patrones:** CAPEC-277, OWASP API2:2023 Broken Authentication, OWASP API5:2023 Broken Function Level Authorization, FE-17

<a id="av-0057"></a>
#### AV-0057 · Credencial de integración con permisos amplios usada para modificar datos más allá de informar estados

- **ID de origen:** AC-UC10-04 · **Ejecución:** Lote 2 · **Tema de riesgo:** R4
- **STRIDE:** E (T, I) — Elevación de privilegios
- **Actor:** Atacante con la credencial de la integración logística (externo)
- **Elementos del DFD:** logistic, delivery-api · **Límites:** LC-4
- **Precondiciones:**
  - La credencial de servicio tiene un alcance mayor que el de informar estados (S-06).
  - delivery-api no separa permisos por función ni por orden de entrega.
  - El atacante conoce o descubre otros endpoints de delivery-api, por ejemplo en documentación expuesta o en un inventario de APIs desactualizado.
- **Cómo ocurre:**
  1. El atacante obtiene la credencial de integración.
  2. Con un cliente HTTP prueba, desde fuera, otros endpoints de delivery-api además del de eventos de estado: consulta de órdenes, cambios de dirección o de tienda.
  3. delivery-api acepta la credencial en esas funciones porque no restringe su alcance.
  4. El atacante lee direcciones y datos de clientes, o modifica la dirección de entrega de órdenes específicas. Con ello redirige paquetes o extrae datos personales.
- **Vector práctico:** Cliente HTTP con la credencial de integración para invocar funciones de delivery-api distintas de la de estados. Manipula el campo dirección de entrega y consulta datos de clientes asociados a identificadores de órdenes.
- **Impacto:** Exposición de datos personales (nombres, direcciones, órdenes) y desvío de paquetes mediante cambio de dirección. Una sola credencial filtrada compromete toda la operación de entregas.
- **Riesgo:** alto (2×3). Si la credencial tiene alcance amplio (S-06), una sola filtración permite leer datos personales y cambiar direcciones de entrega en toda la operación.
- **Controles:**
  - *preventivo* (ecommerce): Limitar el scope de la credencial de integración a un único endpoint (POST de eventos de estado) con autorización por función en delivery-api, de modo que consulta de órdenes y cambio de dirección o tienda devuelvan 403 para esa identidad.
  - *preventivo* (ecommerce): Restringir la credencial a órdenes asignadas a ese proveedor y exponer delivery-api a la integración solo mediante un gateway con allowlist de rutas e IPs. Mantener un inventario actualizado de endpoints y retirar los obsoletos o no documentados (API9).
  - *detectivo* (ecommerce): Registrar y alertar toda llamada de la identidad de integración a rutas distintas de la de eventos, así como consultas de datos de clientes o cambios de dirección originados por esa identidad.
  - *correctivo* (ecommerce): Ante uso fuera de alcance, revocar la credencial, revisar el historial de cambios de dirección para restaurar los valores originales, detener los envíos redirigidos y notificar la exposición de datos personales según corresponda.
- **Referencias y patrones:** OWASP API5:2023 Broken Function Level Authorization, OWASP API9:2023 Improper Inventory Management, FE-17

<a id="av-0058"></a>
#### AV-0058 · Proveedor logístico niega haber reportado una entrega porque los eventos no son atribuibles

- **ID de origen:** AC-UC10-05 · **Ejecución:** Lote 2 · **Tema de riesgo:** R4
- **STRIDE:** R (T) — Repudio
- **Actor:** Proveedor logístico (empresa de logística) en una disputa por una entrega (interno de tercero)
- **Elementos del DFD:** logistic, delivery-api · **Límites:** LC-4
- **Precondiciones:**
  - Todos los eventos llegan bajo la misma credencial compartida y no llevan firma por mensaje (S-06).
  - delivery-api guarda solo el último estado y no conserva el mensaje original ni su origen.
  - El estado "entregado" es la evidencia principal para cerrar el caso (S-16).
- **Cómo ocurre:**
  1. Un paquete se pierde o es reclamado como no recibido, y delivery-api tiene la orden como "entregado" por un evento de la integración.
  2. El ecommerce reclama al proveedor el costo de la pérdida con base en ese evento.
  3. El proveedor afirma que el evento no salió de sus sistemas y atribuye el hecho a un tercero con la credencial filtrada.
  4. Sin firma por evento ni registro del mensaje original, el ecommerce no puede demostrar quién emitió el evento, y asume la pérdida.
- **Vector práctico:** Negación de origen de un evento aprovechando la credencial compartida. El dato en disputa es el estado "entregado" con su marca de tiempo y su ubicación, almacenado en delivery-api sin firma ni registro del mensaje original.
- **Impacto:** Pérdida económica no recuperable y disputas contractuales sin evidencia. Se debilita la capacidad de auditoría de la integración.
- **Riesgo:** medio (2×2). La disputa es probable cuando hay pérdidas y no se guarda el mensaje original ni su origen; la pérdida económica es acotada a cada envío pero no recuperable.
- **Controles:**
  - *preventivo* (proveedor logístico): Exigir firma digital por evento con clave propia del proveedor (no repudio) y un identificador único de evento, y cláusula contractual que haga válido y atribuible a esa clave todo evento firmado.
  - *preventivo* (ecommerce): Guardar en delivery-api un registro inmutable (append-only) de cada evento recibido con el mensaje original, la firma, la IP de origen, el identificador de credencial y la hora de recepción, en lugar de conservar solo el último estado.
  - *detectivo* (ecommerce): Conciliar periódicamente el registro de eventos recibidos con el log de escaneos y eventos emitidos del proveedor, e investigar las diferencias de volumen o de contenido.
  - *correctivo* (proveedor logístico): En una disputa, el proveedor entrega las evidencias de emisión (logs firmados, usuario y escaneo que originó el evento) en un plazo contractual, y el ecommerce usa el registro inmutable para reclamar la pérdida o aplicar penalidades.
- **Referencias y patrones:** OWASP API2:2023 Broken Authentication, FE-17

<a id="av-0059"></a>
#### AV-0059 · Contenido malicioso en la ubicación reportada que se muestra al cliente en el Marketplace

- **ID de origen:** AC-UC10-07 · **Ejecución:** Lote 2 · **Tema de riesgo:** R4
- **STRIDE:** T (I, E) — Manipulación
- **Actor:** Atacante con la credencial de integración o empleado del proveedor que controla el contenido de los eventos (externo)
- **Elementos del DFD:** logistic, delivery-api, Marketplace · **Límites:** LC-4
- **Precondiciones:**
  - El campo de ubicación reportada (u otros campos de texto del evento) acepta texto libre sin validar formato ni longitud.
  - El Marketplace muestra esos valores al cliente sin codificarlos de forma segura.
  - El atacante puede enviar eventos a delivery-api, con la credencial o desde el sistema del proveedor.
- **Cómo ocurre:**
  1. El atacante envía un evento a delivery-api para una orden concreta. En lugar de coordenadas o de una ubicación válida, el campo de ubicación contiene texto con marcado, o un enlace externo con un mensaje engañoso.
  2. delivery-api guarda el valor sin validarlo y lo expone al Marketplace.
  3. Cuando el cliente consulta el seguimiento de su orden, el Marketplace presenta el contenido. Puede ejecutarse código en el navegador del cliente, o se muestra un enlace de supuesto pago o confirmación.
  4. El cliente sigue el enlace o su sesión queda expuesta, con riesgo de robo de datos o de suplantación en el Marketplace.
- **Vector práctico:** Cliente HTTP con la credencial de integración, o el propio sistema del proveedor, para enviar un evento cuyo campo de ubicación reportada contiene marcado o un enlace externo en vez de coordenadas. El dato manipulado es ese campo, que delivery-api guarda y el Marketplace muestra al cliente.
- **Impacto:** Compromiso de sesiones o phishing hacia los clientes desde un canal de confianza (el seguimiento de la orden). Posible robo de datos personales o de credenciales, con daño reputacional.
- **Riesgo:** alto (2×3). Si no se valida ni se codifica el texto libre (supuesto por confirmar), un evento malicioso puede lanzar XSS o phishing hacia clientes desde un canal de confianza.
- **Controles:**
  - *preventivo* (ecommerce): Validar en delivery-api el esquema del evento: la ubicación debe ser latitud y longitud numéricas en rango, o un texto de catálogo con longitud máxima y lista de caracteres permitidos. Rechazar marcado, URLs y cualquier campo no definido.
  - *preventivo* (ecommerce): Codificar por contexto (output encoding) toda la información del evento que renderiza el Marketplace, sin usar innerHTML ni permitir enlaces generados desde esos campos, y aplicar una Content-Security-Policy restrictiva.
  - *detectivo* (ecommerce): Registrar y alertar los eventos rechazados por validación de ubicación y detectar patrones de marcado (<script>, URLs, javascript:) en los datos almacenados, además de monitorear violaciones de CSP en el Marketplace.
  - *correctivo* (ecommerce): Sanear o eliminar los valores maliciosos ya almacenados, invalidar las sesiones de clientes que consultaron esas órdenes, avisarles del posible enlace fraudulento y revocar la credencial usada.
- **Referencias y patrones:** OWASP API8:2023 Security Misconfiguration, CAPEC-277, FE-17

<a id="av-0060"></a>
#### AV-0060 · Empleado del proveedor logístico registra estados de entrega desde su propio sistema sin escaneo físico, a través de la integración logistic

- **ID de origen:** AC-UC10-02 · **Ejecución:** Lote 2 · **Tema de riesgo:** R4
- **STRIDE:** T (S, R) — Manipulación
- **Actor:** Empleado del proveedor logístico con acceso al sistema que alimenta la integración logistic (interno de tercero)
- **Elementos del DFD:** logistic, delivery-api, Marketplace · **Límites:** LC-4
- **Precondiciones:**
  - El empleado puede crear o editar eventos de estado en el sistema del proveedor, o conoce cómo se invoca la integración.
  - delivery-api no verifica que cada transición esté respaldada por un escaneo físico registrado en la red logística (S-15).
  - Los eventos viajan con la credencial de servicio compartida de la integración (S-06), sin identificar al empleado que los originó.
- **Cómo ocurre:**
  1. El empleado retiene o desvía un paquete de valor de la orden X, por ejemplo en un centro de distribución.
  2. Desde el sistema del proveedor, o invocando directamente la integración, crea los eventos "en reparto" y luego "entregado" para la orden X, sin que exista un escaneo en la red logística.
  3. logistic reenvía los eventos a delivery-api con la credencial compartida y delivery-api actualiza el estado de la orden de entrega.
  4. El Marketplace muestra al cliente que la orden fue entregada. Cuando el cliente reclama, el evento figura como originado por la integración y no identifica a la persona que lo generó.
- **Vector práctico:** Con su acceso legítimo al sistema del proveedor (o con una invocación directa de logistic), el empleado crea o edita manualmente eventos de entrega. El dato manipulado es el estado de entrega (y su marca de tiempo) de la orden X, que llega a delivery-api bajo la credencial compartida de la integración. Se diferencia de AV-0006 en que el actor es un empleado del proveedor logístico y el canal es la integración logistic con credencial compartida, no el sistema de la tienda. Se diferencia de AV-0001 en que no se falsifica la ubicación desde la app del repartidor, sino que se fabrica el evento en el sistema del proveedor.
- **Impacto:** Pérdida de mercadería voluminosa, reembolsos o reenvíos a cargo del ecommerce y disputa contractual difícil de resolver con el proveedor. Se pierde la capacidad de atribuir el evento a una persona concreta porque todos los eventos usan la misma credencial.
- **Riesgo:** medio (2×2). El empleado tiene acceso legítimo y delivery-api no exige respaldo de escaneo (S-15), pero el hurto se limita a órdenes concretas y es recuperable en parte vía responsabilidad contractual.
- **Controles:**
  - *preventivo* (ecommerce): Exigir en delivery-api que cada transición de estado referencie un identificador de escaneo físico verificable en la red logística, y rechazar eventos 'en reparto' o 'entregado' sin respaldo de un escaneo previo del paquete.
  - *preventivo* (proveedor logístico): Restringir en el sistema del proveedor la creación o edición manual de eventos de estado a un rol aprobado, con doble aprobación para estados finales, cuentas nominales y propagación del identificador del usuario origen en cada evento.
  - *detectivo* (ecommerce): Conciliar los eventos 'entregado' con los escaneos de la red y con el código de confirmación del cliente, y alertar cuando haya eventos sin escaneo o ediciones manuales concentradas en un mismo usuario o centro de distribución.
  - *correctivo* (proveedor logístico): Abrir una investigación conjunta ante reclamos de no recepción, con los logs de usuario del proveedor, y aplicar la penalidad contractual, la restitución de la mercadería y la desactivación del acceso del empleado involucrado.
- **Referencias y patrones:** CAPEC-277, AV-0006, AV-0001, FE-17

<a id="av-0061"></a>
#### AV-0061 · Repetición de eventos legítimos de la integración con credencial filtrada para revertir el estado "entregado" de una orden

- **ID de origen:** AC-UC10-03 · **Ejecución:** Lote 2 · **Tema de riesgo:** R4
- **STRIDE:** T (D) — Manipulación
- **Actor:** Atacante que dispone de la credencial compartida de la integración y de copias de eventos legítimos previos (externo)
- **Elementos del DFD:** logistic, delivery-api, Marketplace · **Límites:** LC-4
- **Precondiciones:**
  - El atacante posee la credencial de servicio compartida de la integración, filtrada por un descuido del proveedor o de un tercero (S-06).
  - El atacante dispone de copias de eventos legítimos ya enviados por la integración para una orden concreta, por ejemplo un evento "fallido" o "en tránsito". Se asume que las obtuvo del mismo incidente de filtración, que expuso registros de la integración junto con la credencial.
  - Los eventos no llevan nonce, firma con marca de tiempo ni número de secuencia verificado por delivery-api.
  - delivery-api no valida el orden de las transiciones: acepta retroceder de "entregado" a "en tránsito" o a "fallido".
- **Cómo ocurre:**
  1. El atacante selecciona una orden ya entregada y un evento legítimo anterior de esa misma orden, por ejemplo "fallido" o "en tránsito".
  2. Reenvía ese evento a delivery-api con una herramienta de envío de peticiones HTTP, usando la credencial de la integración, después de que la orden figure como "entregado".
  3. delivery-api procesa el evento repetido como válido, porque no detecta que es un duplicado ni que la transición es retrógrada, y sobrescribe el estado actual.
  4. El Marketplace muestra al cliente un estado incorrecto, lo que puede disparar reclamos, reprogramaciones o flujos de devolución para una orden que ya se entregó.
- **Vector práctico:** Con una herramienta de envío de peticiones HTTP y la credencial de la integración, el atacante reutiliza un evento legítimo capturado. Los datos manipulados son el estado de entrega y la marca de tiempo del mensaje, que se reenvían sin cambios para la misma orden hacia delivery-api. Se diferencia de FE-17 en que no se fabrica un evento nuevo, sino que se repite uno auténtico, y el ataque depende de la ausencia de unicidad y de control de secuencia.
- **Impacto:** Órdenes ya entregadas que reaparecen como fallidas o en tránsito, con reentregas o reembolsos indebidos. El soporte, el seguimiento al cliente y los reportes operativos quedan contaminados con estados inconsistentes.
- **Riesgo:** bajo (1×2). Requiere tener la credencial y copias de eventos previos de una misma filtración, lo cual es poco probable, y el efecto es estados inconsistentes y reclamos, no robo directo.
- **Controles:**
  - *preventivo* (ecommerce): Incluir en cada evento un ID único y un número de secuencia por orden dentro de la firma con marca de tiempo, y hacer que delivery-api descarte duplicados, eventos fuera de ventana de tiempo (por ejemplo 5 minutos) y secuencias menores o iguales a la última aceptada.
  - *preventivo* (ecommerce): Impedir en delivery-api transiciones retrógradas desde estados finales ('entregado') hacia 'en tránsito' o 'fallido', salvo mediante un flujo manual aprobado y auditado.
  - *detectivo* (ecommerce): Registrar los eventos rechazados por duplicado o por retroceso de estado y alertar cuando una misma orden reciba reenvíos de eventos antiguos o cuando reaparezcan como activas órdenes ya entregadas.
  - *correctivo* (proveedor logístico): Restaurar el último estado válido a partir del registro inmutable de eventos, cancelar los reenvíos o reembolsos disparados por el estado falso y rotar la credencial, además de proteger los logs de la integración del lado del proveedor.
- **Referencias y patrones:** CAPEC-277, FE-17

### UC-11 Registro de entrega a domicilio con geolocalización

<a id="av-0001"></a>
#### AV-0001 · Entrega registrada sin entregar mediante ubicación GPS simulada

- **ID de origen:** AC-UC11-01 · **Ejecución:** UC-11 · **Tema de riesgo:** R1
- **STRIDE:** S (R, T) — Suplantación
- **Actor:** Repartidor (interno de tercero)
- **Elementos del DFD:** F17, F18, App del repartidor, logistic, delivery-api · **Límites:** LC-4, LC-5
- **Precondiciones:**
  - El repartidor tiene asignada una orden a domicilio de alto valor
  - La ubicación la genera el dispositivo del repartidor y delivery-api la acepta sin atestación (S-17)
  - El repartidor controla su dispositivo (Android con opciones de desarrollador o con root)
  - Conoce la dirección de entrega o sus coordenadas desde la app
- **Cómo ocurre:**
  1. El repartidor recoge el producto y no se dirige al domicilio
  2. Activa una app de ubicación simulada (mock location) y fija las coordenadas de la dirección del cliente
  3. Abre la app del repartidor y registra la entrega con evidencia fabricada (foto reutilizada o tomada de otro lugar)
  4. La app adjunta las coordenadas simuladas y logistic envía el registro a delivery-api (F18)
  5. delivery-api calcula la distancia contra la dirección, la encuentra dentro del radio de tolerancia de RN-3 y marca la orden como entregada
  6. El repartidor se queda con el producto; el cliente reclama que no recibió nada
- **Vector práctico:** Desde el dispositivo del repartidor, una app de mock location (o un Android rooteado con Frida/Xposed que hookea la API de localización) inyecta las coordenadas de la dirección de entrega. El dato manipulado son las coordenadas y su marca de tiempo en el registro enviado a delivery-api, que no valida la procedencia ni la integridad de la posición.
- **Impacto:** Pérdida del producto y reembolso o reenvío al cliente. La orden consta como entregada, lo que debilita la trazabilidad y complica la disputa con el proveedor logístico. Pérdida económica recurrente si el repartidor repite el abuso.
- **Riesgo:** alto (3×3). Las apps de ubicación simulada son triviales de usar en Android y no hay atestación (S-17), por lo que el abuso es muy probable y causa pérdida directa de producto de alto valor, reembolso y disputa con el proveedor.
- **Controles:**
  - *preventivo* (proveedor logístico): Integrar en la app del repartidor atestación del dispositivo (Play Integrity API) y exigir un veredicto válido y reciente (dispositivo íntegro, app sin modificar) vinculado a un nonce emitido por delivery-api para cada registro de entrega; sin veredicto válido no se permite registrar la entrega.
  - *preventivo* (proveedor logístico): Detectar ubicación simulada en la app (flag isMock/isFromMockProvider, apps de mock location habilitadas, root, hooks Frida/Xposed) y enviar el resultado dentro del payload; delivery-api rechaza o envía a revisión manual los registros con indicadores de manipulación.
  - *preventivo* (ecommerce): Hacer obligatorio el código de confirmación del cliente para cerrar la entrega a domicilio de alto valor, de modo que la coordenada por sí sola no baste para marcar la orden como entregada.
  - *detectivo* (ecommerce): Análisis de trayectoria por repartidor en delivery-api: detectar saltos imposibles entre entregas, ausencia de recorrido GPS previo hacia la dirección, precisión GPS idéntica o redondeada entre registros y desfase entre marca de tiempo del dispositivo y del servidor.
  - *detectivo* (proveedor logístico): Alertas por concentración de reclamos de no recibido por repartidor o ruta, con umbral y revisión semanal conjunta con el proveedor logístico.
  - *correctivo* (proveedor logístico): Ante un registro sospechoso, congelar el cierre de la orden, contactar al cliente, suspender temporalmente al repartidor y activar la cláusula contractual de responsabilidad del proveedor para recuperar el costo del producto y del reembolso.
- **Referencias y patrones:** FE-07, OWASP API10:2023 Unsafe Consumption of APIs
- **Ajuste del analista:** Responsable: la atestación del dispositivo se implementa en la app del repartidor, que es del proveedor logístico.

<a id="av-0002"></a>
#### AV-0002 · Colusión cliente-repartidor para cobrar el reembolso con el producto entregado

- **ID de origen:** AC-UC11-03 · **Ejecución:** UC-11 · **Tema de riesgo:** R1
- **STRIDE:** R (T) — Repudio
- **Actor:** Cliente en colusión con repartidor (externo) + Repartidor (interno de tercero)
- **Elementos del DFD:** F17, F18, delivery-api, estados de entrega · **Límites:** LC-5
- **Precondiciones:**
  - El repartidor puede registrar un resultado distinto del real (entregado, rechazado, no entregado) sin evidencia robusta
  - El reembolso se concede por estado de entrega o reclamo sin devolución física del producto
  - Cliente y repartidor se coordinan fuera de la plataforma
- **Cómo ocurre:**
  1. El cliente compra un producto de alto valor con entrega a domicilio y se pone de acuerdo con el repartidor
  2. El repartidor entrega el producto en la dirección pero registra el intento como rechazado o no entregado, con una foto genérica y un motivo inventado
  3. delivery-api cambia el estado de la orden y no exige el código de confirmación ni la evidencia del cliente
  4. El cliente solicita cancelación y reembolso, que se aprueba según el estado registrado
  5. Cliente y repartidor se reparten el valor del producto
- **Vector práctico:** El repartidor usa su app para registrar el estado 'rechazado' o 'no entregado' con la evidencia adjunta manipulada (foto reutilizada, motivo libre), mientras el cliente abre el reclamo en el canal de soporte. El dato manipulado es el estado y la evidencia del registro de entrega, que no se contrasta con el código de confirmación del cliente. Es el caso inverso (marcar entregado y reclamar no recibido) con el mismo mecanismo.
- **Impacto:** Pérdida del producto y del reembolso, repudio de la entrega real por ambas partes y pérdidas repetidas si la pareja reitera el patrón sobre productos de alto valor.
- **Riesgo:** alto (2×3). Requiere coordinación entre dos partes pero el reembolso se concede sin devolución física y sin contraste con el código de confirmación, y el patrón es repetible sobre productos de alto valor.
- **Controles:**
  - *preventivo* (ecommerce): Condicionar el reembolso por rechazo o no entrega a la recepción y verificación del producto devuelto en almacén; sin devolución física comprobada no se libera el reembolso.
  - *preventivo* (proveedor logístico): Exigir evidencia robusta para registrar estados de rechazo o no entregado: foto con marca de tiempo y geolocalización firmada, motivo seleccionado de catálogo cerrado y confirmación por contacto con el cliente (llamada o mensaje a canal verificado) antes de cambiar el estado.
  - *preventivo* (ecommerce): Pasar a revisión manual las cancelaciones y reembolsos de productos de alto valor solicitados poco después de un intento de entrega rechazado o no entregado.
  - *detectivo* (ecommerce): Análisis de relaciones repartidor-cliente en delivery-api: detectar pares que se repiten, rechazos frecuentes de productos de alto valor y cuentas de clientes vinculadas por dirección, dispositivo o medio de pago.
  - *detectivo* (proveedor logístico): Reporte periódico por repartidor de tasa de rechazos y no entregados frente al promedio de su ruta, con alerta ante desviaciones.
  - *correctivo* (ecommerce): Ante colusión confirmada, bloquear las cuentas del cliente y del repartidor, revertir reembolsos cuando sea posible, reclamar el valor al proveedor logístico según contrato y escalar a asuntos legales.
- **Referencias y patrones:** FE-08, FE-01
- **Ajuste del analista:** Actor combinado: el esquema admite un solo actor; se agrega el repartidor (interno de tercero) como participante.

<a id="av-0003"></a>
#### AV-0003 · Reescritura de las coordenadas del registro de entrega en tránsito entre la app del repartidor y logistic

- **ID de origen:** AC-UC11-02 · **Ejecución:** UC-11 · **Tema de riesgo:** R1
- **STRIDE:** T (S, R) — Manipulación
- **Actor:** Repartidor (interno de tercero)
- **Elementos del DFD:** F18, App del repartidor, logistic, delivery-api · **Límites:** LC-4, LC-5
- **Precondiciones:**
  - El repartidor controla su propio dispositivo Android y puede configurarlo con un proxy (mitmproxy) y un certificado raíz propio, porque la app no usa certificate pinning
  - El registro de entrega viaja en F18 (app→logistic) como JSON con latitud, longitud, marca de tiempo y evidencia, sin firma del payload ni atestación del dispositivo
  - Tiene asignada una orden B que no va a entregar. La app le muestra su dirección y coordenadas, porque forman parte de su ruta
  - El flujo acepta como evidencia el código de confirmación, la foto o la firma (paso 2 del caso de uso), y delivery-api no exige el código ni vincula la foto o firma a la orden
  - logistic reenvía a delivery-api el registro tal como lo recibe, sin revalidar su integridad
  - Solo accede a delivery-api a través de logistic y con la app, sin credenciales directas a delivery-api
- **Cómo ocurre:**
  1. El repartidor se queda con el producto de la orden B y no va a su dirección
  2. Configura su teléfono para que el tráfico de la app pase por mitmproxy, instalando su CA, y carga un script que reescribe el cuerpo de las peticiones de registro
  3. Desde un lugar distinto a la dirección de B (por ejemplo, a 4 km), abre en la app el registro de entrega de B, toma una foto cualquiera como evidencia y no usa el código de confirmación
  4. La app adjunta su GPS real y la marca de tiempo actual y envía el registro a logistic (F18)
  5. El script intercepta esa petición y sustituye los campos de latitud y longitud por las coordenadas de la dirección de entrega de B, que conoce por su ruta. No altera order_id, marca de tiempo ni evidencia
  6. logistic reenvía el registro a delivery-api (LC-4) sin detectar la alteración
  7. delivery-api calcula una distancia cercana a 0 m, cumple RN-3, acepta la foto como evidencia sin código de confirmación y marca la orden B como entregada
  8. El cliente de B no recibe nada, reclama, y el ecommerce reembolsa o reenvía mientras el repartidor se queda con el producto
- **Vector práctico:** Con un addon de mitmproxy, el repartidor intercepta el POST de F18 (app→logistic) en su propio dispositivo y reescribe en el JSON los campos de latitud y longitud con las coordenadas de la dirección de la orden B, que obtiene de su ruta asignada. El dato manipulado son las coordenadas del registro, que delivery-api compara con la dirección en RN-3 sin poder comprobar que provienen del GPS real. Se diferencia del uso de una app de ubicación simulada en que la app puede detectar o no el GPS falso, pero el payload alterado en tránsito carece de firma.
- **Impacto:** Órdenes marcadas como entregadas sin haberlo sido, con pérdida del producto, reembolsos o reenvíos, reclamos concentrados en un repartidor y registros de entrega que ya no sirven como prueba en disputas con el proveedor logístico.
- **Riesgo:** alto (2×3). Requiere más habilidad técnica (mitmproxy con CA propia), pero la ausencia de pinning, firma del payload y atestación lo hace viable, y el efecto es una entrega falsa válida ante RN-3 con pérdida del producto y evidencia inservible en disputas.
- **Controles:**
  - *preventivo* (ecommerce): Firmar el payload del registro de entrega (coordenadas, marca de tiempo, order_id, hash de evidencia, nonce) con una clave de dispositivo respaldada por hardware (Android Keystore) atestada, y verificar la firma en delivery-api en LC-4, rechazando cualquier registro cuya firma no coincida.
  - *preventivo* (proveedor logístico): Implementar certificate pinning en la app del repartidor hacia logistic y detección de proxy o CA de usuario instalada, bloqueando el envío del registro si se detecta intercepción.
  - *preventivo* (proveedor logístico): logistic debe reenviar el registro sin modificarlo junto con la firma original, y delivery-api debe revalidar integridad y frescura (nonce de un solo uso, ventana de tiempo corta, vinculación del order_id a la orden asignada a ese repartidor) en lugar de confiar en el reenvío.
  - *preventivo* (ecommerce): Exigir en delivery-api el código de confirmación del cliente para cerrar la orden y vincular la foto o firma a la orden mediante metadatos firmados (order_id, marca de tiempo, coordenadas) en vez de aceptarlas como evidencia suelta.
  - *detectivo* (ecommerce): Contrastar las coordenadas del registro con la telemetría de ruta continua del dispositivo (trazas GPS periódicas firmadas) y con las coordenadas EXIF de la foto; generar alerta si la posición reportada difiere de la traza más de un umbral.
  - *detectivo* (proveedor logístico): Registrar en logs de auditoría inmutables en logistic y delivery-api el hash del payload recibido y el reenviado, y alertar ante discrepancias o fallos de verificación de firma por repartidor.
  - *correctivo* (proveedor logístico): Ante manipulación confirmada, revocar la clave de dispositivo y la sesión del repartidor, reabrir las órdenes afectadas como no entregadas, recuperar el producto y reclamar al proveedor logístico según contrato.
- **Referencias y patrones:** FE-07, S-17

<a id="av-0004"></a>
#### AV-0004 · Reclamo falso de entrega a otra persona apoyado en que la geolocalización no prueba quién recibió

- **ID de origen:** AC-UC11-04 · **Ejecución:** UC-11 · **Tema de riesgo:** R1
- **STRIDE:** R (S) — Repudio
- **Actor:** Cliente (externo)
- **Elementos del DFD:** F17, F18, App del repartidor, logistic, delivery-api, estados de entrega · **Límites:** LC-5
- **Precondiciones:**
  - El flujo acepta como evidencia el código de confirmación, la foto o la firma (paso 2 del caso de uso), y el código no es obligatorio cuando hay firma o foto
  - El cliente conoce o puede obtener el código de confirmación de su orden, pero nadie lo obliga a darlo
  - El repartidor registra la entrega con la geolocalización del dispositivo y delivery-api la valida con RN-3, por lo que el estado queda como entregado
  - La geolocalización y su marca de tiempo solo acreditan la presencia del repartidor en la dirección, no la identidad de quien recibió el producto
  - La política de reclamos de soporte considera la identidad del receptor (código o firma legible) como la prueba determinante de la recepción por el cliente
- **Cómo ocurre:**
  1. El repartidor llega a la dirección y entrega el producto en la puerta al cliente
  2. El cliente recibe el producto pero, cuando le piden el código de confirmación, dice que no lo tiene a mano
  3. En la pantalla de la app del repartidor (F17) firma con un garabato ilegible, o deja que se tome una foto del paquete en la puerta sin que se vea quién lo recibe
  4. La app adjunta las coordenadas del dispositivo y la marca de tiempo, y logistic envía el registro a delivery-api (F18), que valida la distancia con RN-3 y marca la orden como entregada, con un registro sin código de confirmación
  5. Después el cliente abre un reclamo por el canal de soporte del Marketplace diciendo que no recibió el producto o que lo recibió otra persona
  6. El agente de soporte revisa el estado de entrega en delivery-api y ve ubicación válida dentro del radio, con una firma ilegible o una foto sin receptor identificable y sin código de confirmación
  7. Como esa evidencia prueba que el repartidor estuvo en la dirección pero no que el cliente recibió el producto, el reclamo se resuelve a favor del cliente con reembolso o reenvío, mientras el cliente conserva el producto
- **Vector práctico:** El cliente firma de forma ilegible en la pantalla del repartidor, o acepta solo la foto del paquete, y se niega a dar el código de confirmación en el momento de la entrega. Después abre un reclamo de "no recibido o recibido por otra persona" en soporte. El dato aprovechado es el registro de evidencia (firma o foto sin código) que delivery-api guarda en el estado de entrega. Sus coordenadas validadas por RN-3 acreditan el lugar del repartidor pero no quién recibió el producto.
- **Impacto:** Reembolso o reenvío indebido con pérdida del producto, costo de disputa con el proveedor logístico, que no puede demostrar la recepción por el cliente, y posible repetición del patrón en cuentas con productos de alto valor.
- **Riesgo:** medio (2×2). Es sencillo para un cliente oportunista aprovechar firma o foto sin código, pero el impacto por caso se limita al valor de un pedido y se puede acotar con historial de reclamos.
- **Controles:**
  - *preventivo* (ecommerce): Hacer obligatorio el código de confirmación del cliente (entregado en canal verificado, de un solo uso y ligado a la orden) como evidencia principal, aceptando firma o foto solo como complemento, con una excepción registrada y justificada si el cliente no puede darlo.
  - *preventivo* (proveedor logístico): Exigir que la app valide la calidad de la evidencia antes de enviar (firma con trazo mínimo y nombre del receptor, foto con receptor o puerta identificable, marca de tiempo y coordenadas incrustadas) y rechace firmas ilegibles o fotos sin sujeto.
  - *detectivo* (ecommerce): Llevar un historial de reclamos de no recibido por cliente, dirección y medio de pago, y alertar cuando se superen umbrales o los reclamos se concentren en entregas con evidencia válida y geolocalización correcta.
  - *detectivo* (proveedor logístico): Marcar en delivery-api los registros cerrados sin código de confirmación y revisar periódicamente la tasa de reclamos posteriores sobre ellos por repartidor y por cliente.
  - *correctivo* (ecommerce): Ante un reclamo sobre una entrega sin código, contactar al cliente y revisar la evidencia antes de reembolsar; si se confirma el abuso, restringir al cliente a entregas con código obligatorio o recogida en punto, y recuperar el costo mediante la política de reclamos.
- **Referencias y patrones:** FE-01

### UC-12 Recolección en tienda

<a id="av-0005"></a>
#### AV-0005 · Retiro del producto con el código de otro cliente e identificación falsificada

- **ID de origen:** AC-UC12-01 · **Ejecución:** UC-12 · **Tema de riesgo:** R1
- **STRIDE:** S (E) — Suplantación
- **Actor:** Atacante que obtiene el código de retiro del comprador (externo)
- **Elementos del DFD:** Marketplace, delivery-api, Punto de recolección · **Límites:** LC-1, LC-5
- **Precondiciones:**
  - La orden está en estado listo para recolección y la notificación incluye el código de retiro en claro
  - El atacante obtuvo ese código por una cuenta de cliente tomada con credenciales filtradas o por un SMS o correo reenviado
  - El personal de tienda compara la identificación solo a simple vista y no contra una identificación registrada en la orden
- **Cómo ocurre:**
  1. El atacante entra a la cuenta del Marketplace con credenciales reutilizadas, o lee el mensaje de 'producto listo' en un chat o correo comprometido, y copia el código de retiro y el nombre del titular
  2. Imprime en una impresora de PVC una credencial con el nombre del titular y su propia foto
  3. Se presenta en la tienda elegida y entrega el código al personal
  4. El personal valida el código contra la orden en delivery-api, que responde 'válido', y revisa la credencial solo visualmente
  5. Se entrega el producto voluminoso y la orden pasa a entregada; el titular reclama después que no lo recibió
- **Vector práctico:** Credencial falsa impresa con el nombre del titular más el código de retiro copiado de la cuenta o de la notificación; el dato manipulado es la identidad presentada frente a un código que delivery-api valida sin segundo factor ni identificación registrada.
- **Impacto:** Pérdida de un producto de alto valor, reclamo y reembolso al titular legítimo, y exposición de datos de la cuenta tomada.
- **Riesgo:** alto (2×3). El código se envía en claro y la identificación se revisa a simple vista, así que basta una cuenta con credenciales reutilizadas y una credencial impresa para retirar un producto de alto valor.
- **Controles:**
  - *preventivo* (ecommerce): Reemplazar el código estático enviado por SMS o correo por un código de un solo uso que rota y solo se muestra dentro de la app o cuenta autenticada del titular. La notificación de 'listo para recolección' no incluye el código.
  - *preventivo* (ecommerce): Exigir en el retiro una identificación registrada en la orden: el personal escanea el documento (QR o zona legible por máquina) y delivery-api compara el número con el registrado antes de validar el código. En productos de alto valor se añade una segunda verificación con OTP al teléfono registrado del titular.
  - *detectivo* (ecommerce): Regla en delivery-api que marca los retiros de órdenes cuya cuenta tuvo cambio de contraseña, correo o teléfono, o inicio de sesión desde dispositivo nuevo en las 72 horas previas. Esos retiros se retienen hasta una verificación adicional por un supervisor.
  - *correctivo* (ecommerce): Ante un reporte de acceso indebido, invalidar el código vigente y emitir otro, cerrar todas las sesiones y forzar el cambio de credenciales. Conservar la foto y el escaneo de identificación del retiro para la denuncia y la disputa.
- **Referencias y patrones:** CAPEC-569, OWASP OAT-012, FE-10

<a id="av-0006"></a>
#### AV-0006 · Personal de tienda marca la orden como entregada sin entregar el producto

- **ID de origen:** AC-UC12-02 · **Ejecución:** UC-12 · **Tema de riesgo:** R1
- **STRIDE:** T (R) — Manipulación
- **Actor:** Personal de tienda con acceso al sistema de validación de retiros (interno)
- **Elementos del DFD:** delivery-api, Punto de recolección · **Límites:** LC-5
- **Precondiciones:**
  - El producto voluminoso ya está físicamente en el Punto de recolección y la orden está lista para recolección
  - El empleado puede cambiar el estado de la orden a entregada desde su terminal sin escanear el código de retiro
  - No hay inventario físico ni conciliación entre órdenes entregadas y retiros reales
- **Cómo ocurre:**
  1. El empleado identifica una orden de alto valor que lleva varios días sin retirarse
  2. Desde su sesión en el sistema de la tienda cambia manualmente el estado a entregada, sin escanear el código ni registrar la identificación
  3. Saca el producto del punto de recolección como 'entregado' o lo guarda para sí o para reventa
  4. Cuando el cliente llega, la orden ya figura como entregada y no hay evidencia del retiro para disputar
- **Vector práctico:** Edición directa del estado de la orden con la cuenta de empleado en la terminal de la tienda, sin escanear el código de retiro; el dato manipulado es el estado de la orden en delivery-api.
- **Impacto:** Pérdida del producto, disputa sin evidencia con el cliente, reembolso a cargo de la empresa y dificultad para atribuir al empleado.
- **Riesgo:** alto (2×3). Un empleado con acceso legítimo puede cambiar el estado sin escanear el código y no existe conciliación física, por lo que el fraude es fácil de ejecutar y difícil de atribuir en productos de alto valor.
- **Controles:**
  - *preventivo* (ecommerce): delivery-api solo permite pasar la orden a 'entregada' si recibe un escaneo válido del código de retiro y el identificador de la identificación verificada. Cualquier excepción manual requiere aprobación de un segundo usuario (supervisor) con motivo obligatorio.
  - *preventivo* (ecommerce): Registrar cada cambio de estado en un log append-only e inmutable con empleado, terminal, método de validación y hora, de modo que el empleado no pueda repudiar ni borrar su acción.
  - *detectivo* (ecommerce): Conciliación diaria entre órdenes entregadas, escaneos de código registrados y el inventario físico del Punto de recolección. Alertas por empleado y por tienda sobre entregas sin escaneo o con excepciones manuales frecuentes.
  - *correctivo* (ecommerce): Al detectar una entrega sin evidencia, revertir el estado de la orden, suspender el acceso del empleado, abrir investigación con el log inmutable y gestionar con el cliente la reposición o la entrega del producto.
- **Referencias y patrones:** CAPEC-545, FE-10

<a id="av-0007"></a>
#### AV-0007 · Consulta de órdenes ajenas en la validación de retiro para obtener códigos y datos personales

- **ID de origen:** AC-UC12-05 · **Ejecución:** UC-12 · **Tema de riesgo:** R7
- **STRIDE:** I (S) — Divulgación de información
- **Actor:** Atacante que obtiene acceso a la interfaz de validación de retiros (externo)
- **Elementos del DFD:** delivery-api, Punto de recolección · **Límites:** LC-5
- **Precondiciones:**
  - Existe un endpoint de consulta de orden por identificador, usado por la terminal de la tienda, que no limita el alcance a las órdenes de esa tienda
  - Los identificadores de orden son secuenciales o predecibles
  - La respuesta incluye el código de retiro, el nombre del cliente y datos de su identificación
- **Cómo ocurre:**
  1. El atacante obtiene credenciales de una terminal o de un empleado de la tienda por phishing, o usa una terminal desatendida
  2. Captura la petición de consulta de orden con Burp Suite y la envía a Intruder, que recorre los identificadores cercanos a la orden propia
  3. delivery-api responde con el código de retiro, el nombre del titular y el dato de identificación de órdenes de otros clientes y de otras tiendas
  4. El atacante elige las órdenes de alto valor listas para recolección y arma identificaciones falsas con los nombres obtenidos
  5. Se presenta en la tienda para retirar o vende la lista de datos
- **Vector práctico:** Enumeración con Burp Intruder del identificador de orden en la consulta de validación (BOLA), con el campo orderId como dato manipulado, para leer códigos de retiro y datos personales ajenos.
- **Impacto:** Exposición de datos personales y de los códigos de retiro de muchos clientes, habilita retiros fraudulentos masivos e implica incumplimiento de protección de datos.
- **Riesgo:** alto (2×3). Requiere credenciales o una terminal de tienda, pero la enumeración de IDs predecibles es trivial con Burp Intruder y expone códigos y datos personales de muchos clientes.
- **Controles:**
  - *preventivo* (ecommerce): Autorización a nivel de objeto en delivery-api: el endpoint de consulta solo devuelve órdenes asignadas al punto de recolección del solicitante, verificado contra el token de la terminal. Los identificadores de orden pasan a UUID no predecibles.
  - *preventivo* (ecommerce): Minimizar la respuesta: la terminal envía el código presentado y recibe solo 'válido' o 'inválido', más el nombre y el documento enmascarados. Nunca se devuelve el código de retiro ni el número de identificación completo. Las terminales usan MFA y bloqueo de sesión por inactividad.
  - *detectivo* (ecommerce): Rate limiting por terminal y cuenta de empleado, con alertas ante consultas secuenciales, ráfagas de respuestas 403/404 o accesos a órdenes de otras tiendas. Los eventos se envían al SIEM.
  - *correctivo* (ecommerce): Revocar de inmediato las credenciales y el token de la terminal comprometida. Rotar los códigos de retiro de las órdenes expuestas, avisar a los clientes afectados y notificar la brecha según la normativa de protección de datos.
- **Referencias y patrones:** OWASP API1:2023, CAPEC-545, FE-10

<a id="av-0008"></a>
#### AV-0008 · Saturación del Punto de recolección con órdenes que nunca se retiran

- **ID de origen:** AC-UC12-06 · **Ejecución:** UC-12 · **Tema de riesgo:** R8
- **STRIDE:** D — Denegación de servicio
- **Actor:** Atacante o competidor con cuentas de cliente creadas en masa (externo)
- **Elementos del DFD:** Marketplace, delivery-api, Punto de recolección · **Límites:** LC-1, LC-5
- **Precondiciones:**
  - El Marketplace permite elegir recolección en tienda sin límite de órdenes pendientes por cuenta, medio de pago o tienda
  - No hay plazo máximo de retiro con cancelación automática y liberación del producto
  - El almacén prepara y envía el producto voluminoso a la tienda en cuanto la orden está pagada
- **Cómo ocurre:**
  1. El atacante crea decenas de cuentas y paga órdenes de productos voluminosos con tarjetas propias o prepago, eligiendo siempre la misma tienda de recolección
  2. delivery-api asigna la tienda a cada orden y el almacén prepara y envía los productos
  3. El atacante no retira ninguno de los productos
  4. El Punto de recolección agota su espacio y el stock de esos productos queda inmovilizado, por lo que otros clientes no pueden comprarlos o no hay lugar para sus productos
  5. Después solicita la cancelación y recupera el pago, mientras la empresa asume costos de transporte y almacenaje
- **Vector práctico:** Script con Playwright que repite el flujo de compra con cuentas distintas, eligiendo la misma tienda en la modalidad de recolección (campo tienda de recolección de la orden) y sin retirar los productos, hasta saturar el punto y el inventario.
- **Impacto:** Indisponibilidad del Punto de recolección y del inventario de productos voluminosos, ventas perdidas, costos logísticos de ida y vuelta y degradación del servicio.
- **Riesgo:** medio (2×2). Automatizar la creación de cuentas y pagos es sencillo y la falta de límites lo facilita, pero el atacante inmoviliza capital y el daño es temporal: indisponibilidad de espacio e inventario y costos logísticos.
- **Controles:**
  - *preventivo* (ecommerce): Límites de órdenes de recolección pendientes por cuenta, por medio de pago y por tienda, y tope de capacidad por Punto de recolección. El Marketplace no confirma ni despacha productos voluminosos a una tienda sin capacidad disponible.
  - *preventivo* (ecommerce): Plazo máximo de retiro (por ejemplo 5 días) con recordatorios y cancelación automática que libera el producto y el stock.
  - *preventivo* (pasarela de pago): Controles de velocidad por tarjeta y BIN, con detección de tarjetas prepago y de una misma tarjeta usada en varias cuentas. La pasarela puede exigir 3-D Secure o rechazar esos pagos.
  - *detectivo* (ecommerce): Monitoreo de la tasa de órdenes no retiradas por tienda, cuenta y medio de pago, y de la ocupación del Punto de recolección, con alerta cuando se superen umbrales. Correlación de cuentas nuevas que eligen la misma tienda.
  - *correctivo* (ecommerce): Cancelar las órdenes sospechosas, reponer el stock y bloquear cuentas y tarjetas implicadas. En las cancelaciones por no retiro se retiene o cobra el costo logístico según los términos del servicio.
- **Referencias y patrones:** OWASP OAT-021 Denial of Inventory
- **Ajuste del analista:** Referencia: OWASP OAT-012 (Cashing Out) se sustituye por OAT-021 (Denial of Inventory), que describe el abuso.

<a id="av-0009"></a>
#### AV-0009 · Suplantación del titular con sesión robada para registrar una persona autorizada inventada y retirar el producto

- **ID de origen:** AC-UC12-03 · **Ejecución:** UC-12 · **Tema de riesgo:** R5
- **STRIDE:** S (E) — Suplantación
- **Actor:** Atacante con acceso a la cuenta del cliente (externo)
- **Elementos del DFD:** Marketplace, delivery-api, Punto de recolección · **Límites:** LC-1, LC-5
- **Precondiciones:**
  - El atacante tiene la sesión de la cuenta del comprador (infostealer o credenciales filtradas)
  - El Marketplace permite registrar un 'autorizado' para el retiro sin reautenticar ni notificar por un canal independiente
  - Existe una orden con recolección en tienda en estado pendiente o listo para recolección
  - El Punto de recolección solo compara nombre e identificación presentados contra los datos de la orden
- **Cómo ocurre:**
  1. El atacante entra a la cuenta del comprador con la sesión robada y abre la orden con recolección en tienda; se hace pasar por el titular (suplantación de identidad)
  2. Agrega como autorizado el nombre y el número de identificación de un cómplice, que porta una identificación falsa o ajena con esos datos
  3. El Marketplace envía el dato a delivery-api, que lo asocia a la orden sin segundo factor ni aviso al titular por correo, SMS o notificación push
  4. El atacante lee el código de retiro en la orden de la cuenta y se lo pasa al cómplice
  5. El cómplice se presenta en la tienda con el código y la identificación; el personal verifica que coinciden con la orden y entrega el producto, y la orden pasa a entregada
  6. El titular descubre la entrega a un tercero cuando consulta la orden o recibe el aviso de entregada
- **Vector práctico:** Con la sesión robada, el atacante edita el campo 'persona autorizada' de la orden en la interfaz web del Marketplace, o reenvía la petición modificada con Burp Suite cambiando nombre e identificación del autorizado; el cómplice usa esa identificación junto con el código de retiro visible en la cuenta.
- **Impacto:** Retiro fraudulento con apariencia legítima, porque el autorizado figura en la orden. Pérdida del producto, reclamo de reembolso del titular y disputa sin forma de distinguir la acción del titular real de la del atacante.
- **Riesgo:** alto (2×3). Con una sesión robada el atacante registra un autorizado sin fricción y el retiro parece legítimo, lo que complica la disputa y la recuperación del producto de alto valor.
- **Controles:**
  - *preventivo* (ecommerce): Exigir reautenticación con MFA para agregar o modificar la persona autorizada. La autorización de terceros solo puede iniciarse desde la cuenta del titular y tiene un periodo de espera (por ejemplo 24 horas) antes de ser efectiva en productos de alto valor.
  - *preventivo* (ecommerce): Enviar aviso fuera de banda al correo y teléfono registrados antes del cambio de sesión, con enlace de confirmación o rechazo. El retiro del autorizado exige su identificación escaneada y el código de un solo uso, y delivery-api la compara con los datos del autorizado.
  - *detectivo* (ecommerce): Reglas de correlación que alertan cuando coinciden sesión desde dispositivo o IP nuevos, alta de un autorizado y retiro próximo. También se alerta por cuentas con autorizaciones de terceros frecuentes o con el mismo autorizado en varias cuentas.
  - *correctivo* (ecommerce): Permitir al titular revocar al autorizado desde el aviso y bloquear la orden hasta verificar su identidad por soporte. Si el retiro ya ocurrió, cerrar las sesiones, restablecer credenciales y entregar la evidencia (identificación escaneada, foto) para la denuncia.
- **Referencias y patrones:** CAPEC-569, OWASP OAT-012, FE-10

<a id="av-0010"></a>
#### AV-0010 · Cliente retira el producto en tienda y luego repudia el retiro porque el punto de recolección no deja evidencia independiente

- **ID de origen:** AC-UC12-04 · **Ejecución:** UC-12 · **Tema de riesgo:** R1
- **STRIDE:** R (S) — Repudio
- **Actor:** Cliente comprador (externo)
- **Elementos del DFD:** Marketplace, delivery-api, Punto de recolección · **Límites:** LC-1, LC-5
- **Precondiciones:**
  - La evidencia del retiro se limita a un cambio de estado a entregada en delivery-api, sin firma, foto de la identificación ni escaneo del código
  - El cliente sabe que el reclamo se resuelve con el estado registrado y la falta de evidencia
  - El producto voluminoso es de alto valor y el pago ya fue capturado
- **Cómo ocurre:**
  1. El cliente recibe la notificación de listo para recolección y retira el producto presentando el código y su identificación
  2. El personal valida a mano contra la orden, entrega el producto y marca la orden como entregada, sin que se capture firma, foto del retiro ni escaneo del código
  3. Días después el cliente abre un reclamo en el soporte del Marketplace diciendo que nunca retiró el producto o que lo retiró otra persona sin su permiso
  4. Soporte consulta delivery-api y solo encuentra el estado entregada, sin dato que identifique a quien retiró, por lo que no puede refutar al cliente
  5. La disputa se resuelve a favor del cliente y se emite el reembolso, o se aprueba la cancelación
  6. El cliente se queda con el producto y con el dinero
- **Vector práctico:** Reclamo de no recibido o de retiro por un tercero en el canal de soporte del Marketplace, sobre una orden cuyo único registro es el estado entregada en delivery-api, sin firma, foto ni código escaneado.
- **Impacto:** Pérdida del producto y del importe reembolsado, y carga operativa de disputas sin evidencia para contestarlas.
- **Riesgo:** alto (2×3). Sin firma, foto ni escaneo el reclamo de no recibido no se puede refutar, y el reembolso de un producto voluminoso de alto valor se resuelve a favor del cliente.
- **Controles:**
  - *preventivo* (ecommerce): Exigir al personal, antes de marcar 'entregada', el escaneo del código de un solo uso, el escaneo o la foto de la identificación del retirante, la firma digital y una foto del producto entregado, con marca de tiempo y terminal. Delivery-api bloquea el cambio de estado si falta alguna de esas evidencias.
  - *detectivo* (ecommerce): Historial de reclamos de 'no recibido' o 'retirado por otra persona' por cliente, medio de pago y tienda, con alerta ante clientes con varios reclamos en poco tiempo o con reclamos en órdenes que tenían evidencia completa.
  - *correctivo* (ecommerce): Soporte contrasta el reclamo con la evidencia del retiro y rechaza el reembolso cuando coincide. Si hay contracargo, se adjunta esa evidencia a la disputa y se marca la cuenta o el medio de pago para revisión.
- **Referencias y patrones:** OWASP OAT-012, AV-0004, AV-0002, FE-01
- **Ajuste del analista:** Responsable: la revisión del reclamo la hace soporte del ecommerce, no la pasarela.

### UC-13 Cancelación posterior a la recepción y devolución

<a id="av-0062"></a>
#### AV-0062 · Devolución de un artículo distinto, dañado o una caja con peso equivalente para cobrar el reembolso

- **ID de origen:** AC-UC13-01 · **Ejecución:** Lote 3 · **Tema de riesgo:** R6
- **STRIDE:** T (R) — Manipulación
- **Actor:** Cliente comprador que cancela después de recibir el producto voluminoso (externo)
- **Elementos del DFD:** Marketplace, delivery-api, logistic, Pasarela de pago · **Límites:** LC-1, LC-4, LC-5, LC-6
- **Precondiciones:**
  - El cliente ya recibió el producto y está dentro de la ventana de días para cancelar (S-19)
  - No se registró número de serie ni fotos del producto al despachar, o no se comparan en la recolección inversa
  - Escenario A: el reembolso se emite al confirmar la recolección inversa, antes de la inspección. Escenario B: se emite tras la inspección, pero esta es superficial
- **Cómo ocurre:**
  1. El cliente cancela desde el Marketplace, elige un motivo genérico como 'no cumple expectativas' y se genera la orden de recolección inversa
  2. Antes de la recogida sustituye el contenido por un artículo similar más barato, una unidad dañada o una caja con peso parecido, y conserva el original
  3. El proveedor logístico recoge el bulto sellado y registra la recolección en logistic, que lo notifica a delivery-api
  4. Escenario A: el Marketplace dispara el reembolso en la pasarela al recibir la confirmación de recolección, y el fraude se completa antes de abrir el paquete
  5. Escenario B: el almacén compara solo peso y embalaje exterior, registra 'conforme' y se emite el reembolso
  6. Cuando se detecta la diferencia, el cliente ya cobró y niega haber enviado algo distinto
- **Vector práctico:** El cliente usa la función de cancelación del Marketplace y entrega un bulto físico alterado. El dato manipulado es el contenido del paquete devuelto, mientras el estado de recolección inversa y el resultado de inspección se alimentan de controles débiles (confirmación del proveedor o chequeo de peso). La automatización que vincula la confirmación de recolección con la orden de reembolso en la pasarela permite cobrar sin verificar el artículo.
- **Impacto:** Pérdida del valor del producto voluminoso, que queda en poder del cliente, más el costo logístico de ida y vuelta y la recepción de un artículo sin valor en el inventario. Si la conducta se repite, el fraude se escala y las disputas con el cliente se vuelven difíciles de resolver sin evidencia.
- **Riesgo:** alto (2×3). El producto voluminoso tiene alto valor y el reembolso puede salir antes de una inspección real (S-19), por lo que el fraude es plausible y la pérdida es total.
- **Controles:**
  - *preventivo* (ecommerce): Condicionar el reembolso en la pasarela al resultado 'conforme' de la inspección en almacén, nunca a la confirmación de recolección del proveedor; el reembolso parcial o retenido se libera solo con inspección completa.
  - *preventivo* (ecommerce): Registrar número de serie y fotos del producto al despachar, y exigir en la inspección el escaneo del número de serie y la comparación con el registro del despacho, además del peso con tolerancia definida.
  - *preventivo* (proveedor logístico): Exigir en la recolección inversa fotos con marca de tiempo y ubicación del producto y del embalaje antes de sellar el bulto, junto con un precinto numerado cuyo número se registra en logistic.
  - *detectivo* (ecommerce): Puntuar devoluciones por cliente, dirección y medio de pago (frecuencia, motivo genérico repetido, diferencias de peso o serie) y alertar al equipo antifraude cuando se supere el umbral.
  - *correctivo* (ecommerce): Abrir caso de disputa con la evidencia fotográfica y de serie, reclamar el importe al cliente, bloquear nuevas cancelaciones con reembolso en su cuenta y marcar el medio de pago para revisión manual.
- **Referencias y patrones:** FE-02, CAPEC-207, OWASP Business Logic Abuse

<a id="av-0063"></a>
#### AV-0063 · Cancelación o consulta de devolución sobre órdenes ajenas por referencia directa al identificador

- **ID de origen:** AC-UC13-04 · **Ejecución:** Lote 3 · **Tema de riesgo:** R7
- **STRIDE:** E (I, T) — Elevación de privilegios
- **Actor:** Atacante autenticado como cliente con una cuenta propia (externo)
- **Elementos del DFD:** Marketplace, delivery-api, logistic · **Límites:** LC-1, LC-4
- **Precondiciones:**
  - El atacante tiene una cuenta válida en el Marketplace y una orden propia
  - Los identificadores de orden y de recolección inversa son secuenciales o predecibles, o se pueden obtener por otro medio
  - Delivery-api no verifica que la orden pertenezca al cliente autenticado al cancelar o consultar
- **Cómo ocurre:**
  1. El atacante inicia una cancelación legítima y observa con un proxy de interceptación las peticiones que el Marketplace envía a delivery-api
  2. Identifica el identificador de orden y de recolección inversa en las peticiones
  3. Sustituye el identificador por otros cercanos y reenvía la petición de cancelación o consulta
  4. Delivery-api acepta la petición y crea recolecciones inversas de pedidos ajenos, o devuelve dirección, teléfono y estado de recolección del otro cliente
  5. El cliente afectado ve su compra cancelada, con una recolección inversa programada en su domicilio, o recibe visitas no esperadas
- **Vector práctico:** El atacante usa un proxy de interceptación y un script de enumeración sobre el identificador de orden en las peticiones de cancelación y consulta de recolección inversa. El dato manipulado es el identificador de orden o de recolección, que se acepta sin comprobar propiedad en el servidor.
- **Impacto:** Cancelación indebida de pedidos de terceros y exposición de datos personales (dirección, nombre, teléfono). También se generan recolecciones inversas innecesarias, con costos logísticos y deterioro de la experiencia de clientes legítimos.
- **Riesgo:** medio (2×2). Se desconocen el formato de los identificadores y la autorización por objeto en delivery-api; la enumeración es sencilla si no hay control y afecta datos personales y pedidos ajenos, aunque cada incidente es de valor acotado.
- **Controles:**
  - *preventivo* (ecommerce): Validar en delivery-api, en cada endpoint de cancelación y consulta de recolección inversa, que la orden pertenece al cliente autenticado del token de sesión, sin confiar en el identificador enviado por el cliente.
  - *preventivo* (ecommerce): Usar identificadores de orden y de recolección inversa aleatorios e impredecibles (UUIDv4), y autenticar la llamada de delivery-api a logistic con credenciales de servicio, de modo que logistic solo acepte órdenes originadas allí.
  - *preventivo* (ecommerce): Incluir pruebas automatizadas de autorización por objeto (usuario A contra recursos de usuario B) en el pipeline, que bloqueen el despliegue si fallan.
  - *detectivo* (ecommerce): Aplicar límite de tasa y alertar por ráfagas de respuestas 403/404 o de identificadores distintos consultados por una misma cuenta o IP sobre los endpoints de cancelación y recolección inversa.
  - *correctivo* (ecommerce): Anular las cancelaciones y recolecciones inversas creadas sobre órdenes ajenas, restaurar el estado de la orden, notificar al cliente afectado y revocar las sesiones de la cuenta atacante.
- **Referencias y patrones:** OWASP API1:2023 Broken Object Level Authorization, CAPEC-39, API1:2023

<a id="av-0064"></a>
#### AV-0064 · Conductor de la empresa de logística confirma la recolección inversa sin llevar el producto al almacén

- **ID de origen:** AC-UC13-05 · **Ejecución:** Lote 3 · **Tema de riesgo:** R6
- **STRIDE:** R (T) — Repudio
- **Actor:** Personal de recolección de la empresa de logística (interno de tercero)
- **Elementos del DFD:** logistic, delivery-api, Marketplace, Pasarela de pago · **Límites:** LC-4, LC-5, LC-6
- **Precondiciones:**
  - El reembolso se emite al confirmar el proveedor la recolección, sin esperar la llegada al almacén (S-19)
  - La recolección inversa no exige foto del producto, código de confirmación del cliente ni escaneo de recepción en el almacén
  - El producto devuelto es voluminoso y de alto valor y tiene mercado secundario
- **Cómo ocurre:**
  1. Un cliente legítimo, o un cómplice, solicita la cancelación tras recibir el producto
  2. El personal de recolección acude al domicilio y recoge el producto voluminoso
  3. Registra en logistic la recolección como completada, pero desvía el producto en lugar de llevarlo al almacén
  4. Logistic informa a delivery-api, que dispara el reembolso al cliente al considerar cumplida la recolección
  5. El almacén nunca recibe el producto; el proveedor atribuye la pérdida a otro tramo o declara incidente en ruta
  6. El ecommerce ha reembolsado y no puede reclamar la penalización contractual por falta de evidencia de custodia
- **Vector práctico:** El empleado de la logística usa la app de recolección para marcar el estado 'recogido' y adjuntar evidencia débil o reutilizada. El dato manipulado es el estado de la recolección inversa que logistic envía a delivery-api, que desencadena el reembolso sin contrastar la recepción en almacén.
- **Impacto:** Pérdida del producto y del reembolso, con disputa de responsabilidad entre ecommerce y proveedor. Si hay colusión con el cliente, se desvía mercancía y se reparte el beneficio, y no se puede reclamar la penalización por falta de cadena de custodia.
- **Riesgo:** alto (2×3). El estado informado por el proveedor dispara el reembolso (S-19, S-20) y el producto es voluminoso, de alto valor y con mercado secundario, lo que hace atractivo el desvío y difícil atribuir la responsabilidad.
- **Controles:**
  - *preventivo* (ecommerce): Liberar el reembolso y la restitución del cupón solo tras el escaneo de recepción en almacén de la unidad con su precinto, y no con el estado 'recogido' enviado por logistic.
  - *preventivo* (proveedor logístico): Exigir al recolector un código de confirmación del cliente, foto del producto con marca de tiempo y geolocalización validada contra la dirección, y escaneo del precinto, rechazando evidencia reutilizada mediante hash de imagen.
  - *preventivo* (proveedor logístico): Mantener cadena de custodia con escaneo en cada tramo (recogida, hub, entrega en almacén) y un plazo máximo de tránsito definido contractualmente.
  - *detectivo* (ecommerce): Conciliar de forma automática las recolecciones 'recogidas' sin recepción en almacén dentro del plazo máximo y alertar por pares recolector–cliente repetidos o desvíos de ruta.
  - *correctivo* (proveedor logístico): Retener el pago de la liquidación al proveedor y aplicar la penalización contractual con la evidencia de custodia, suspender al recolector implicado e iniciar investigación conjunta.
- **Referencias y patrones:** FE-08, OWASP Business Logic Abuse, AV-0051, AV-0002

<a id="av-0065"></a>
#### AV-0065 · Personal de almacén registra una inspección conforme falsa para liberar el reembolso a un cómplice

- **ID de origen:** AC-UC13-03 · **Ejecución:** Lote 3 · **Tema de riesgo:** R6
- **STRIDE:** R (T) — Repudio
- **Actor:** Personal de almacén que inspecciona devoluciones (interno)
- **Elementos del DFD:** logistic, delivery-api, Marketplace, Pasarela de pago · **Límites:** LC-4, LC-5, LC-6
- **Precondiciones:**
  - El resultado de la inspección lo registra una sola persona, sin segundo control ni fotos obligatorias
  - El reembolso se libera al registrar el resultado 'conforme' (escenario de S-19 en que se reembolsa tras la inspección sin verificación independiente)
  - El empleado puede identificar devoluciones de clientes cómplices o de alto valor
  - El número de serie o el peso del producto no se registró al despachar, o no se contrasta con lo devuelto
- **Cómo ocurre:**
  1. El cliente cómplice cancela tras recibir el producto y devuelve un artículo distinto, dañado o incompleto
  2. El paquete llega al almacén y el empleado cómplice lo recibe en el flujo de inspección
  3. El empleado registra el resultado como conforme, sin evidencia o con fotos reutilizadas de otra devolución
  4. El sistema acepta el estado registrado, libera el reembolso en la pasarela y restituye el cupón si aplica
  5. El empleado retira el producto original o lo da de baja como merma, y comparte con el cliente parte del beneficio
  6. Ante una auditoría, el empleado alega error de captura o inspección visual válida y no existe prueba independiente de lo que se recibió
- **Vector práctico:** El empleado usa la consola o app de almacén con su usuario legítimo para registrar el resultado de la inspección de una devolución concreta. El dato manipulado es el campo de resultado y su evidencia asociada (fotos reutilizadas, sin número de serie), que delivery-api toma como verdad sin contrastarlo con el despacho original. Ese registro dispara el reembolso sin que otra persona confirme lo recibido.
- **Impacto:** Reembolsos fraudulentos y pérdida de inventario de alto valor, con responsabilidad difícil de atribuir. Se pierde la inspección como control antifraude y se debilita la evidencia ante disputas.
- **Riesgo:** medio (1×3). Requiere un empleado interno en colusión con un cliente, lo que es poco frecuente, pero sin doble control ni evidencia independiente el reembolso de un producto de alto valor queda sin freno y es difícil de atribuir.
- **Controles:**
  - *preventivo* (ecommerce): Exigir doble control (cuatro ojos) con un segundo inspector o supervisor para aprobar el resultado 'conforme' de devoluciones por encima de un umbral de valor, antes de liberar el reembolso.
  - *preventivo* (ecommerce): Hacer obligatorios el escaneo del número de serie, el peso y fotos del desembalaje tomadas en la app de almacén con marca de tiempo, comparados contra el registro del despacho, sin permitir adjuntar fotos preexistentes.
  - *detectivo* (ecommerce): Detectar fotos duplicadas por hash, inspecciones 'conformes' sin evidencia y correlaciones entre inspector y clientes con devoluciones repetidas, y auditar una muestra aleatoria con segunda inspección independiente.
  - *detectivo* (ecommerce): Conciliar periódicamente el inventario de devoluciones y mermas del almacén contra los números de serie reembolsados, para detectar productos originales dados de baja.
  - *correctivo* (ecommerce): Reabrir el caso, suspender el acceso del inspector implicado, recuperar el importe del cliente cómplice y escalar a investigación interna con los registros de auditoría de la consola.
- **Referencias y patrones:** FE-02, AV-0002

<a id="av-0066"></a>
#### AV-0066 · Doble reembolso por reenvío concurrente de la solicitud de cancelación

- **ID de origen:** AC-UC13-06 · **Ejecución:** Lote 3 · **Tema de riesgo:** R6
- **STRIDE:** T (D) — Manipulación
- **Actor:** Cliente que manipula el flujo de cancelación (externo)
- **Elementos del DFD:** Marketplace, delivery-api, logistic, Pasarela de pago · **Límites:** LC-1, LC-4, LC-6
- **Precondiciones:**
  - SN-03: la operación de reembolso no es idempotente ni está protegida por un bloqueo sobre el estado de la orden
  - SN-04: las llamadas del Marketplace a la pasarela no llevan una clave única por reembolso
  - El Marketplace emite el reembolso al recibir confirmaciones de recolección o inspección desde delivery-api o logistic, y esas confirmaciones pueden repetirse
  - La orden sigue en un estado que permite cancelar mientras se procesan las primeras solicitudes
- **Cómo ocurre:**
  1. El cliente recibe el producto y abre la solicitud de cancelación de la orden desde el Marketplace
  2. Antes de que el estado de la orden cambie, reenvía la misma solicitud varias veces en paralelo desde un cliente HTTP o un script, o la repite desde varias sesiones
  3. El Marketplace valida cada solicitud contra un estado de orden que aún no se actualizó y crea una orden de recolección inversa para cada una
  4. Cuando llegan las confirmaciones de recolección e inspección, cada una dispara su propia solicitud de reembolso a la pasarela, que procesa dos o más sobre la misma orden
  5. Si aplica, el cupón se restituye más de una vez
  6. La conciliación contable detecta la diferencia días después, cuando el cliente ya dispuso del dinero
  7. Con muchas solicitudes se generan además múltiples recolecciones inversas y se satura el trabajo del proveedor logístico
- **Vector práctico:** El cliente usa una herramienta de reenvío concurrente de peticiones contra el endpoint de cancelación de orden del Marketplace, con el identificador de la orden pagada como dato repetido. Lo que explota es la ventana entre la recepción de cada petición y la actualización del estado de la orden, además de la falta de un identificador único de reembolso. Sin control de idempotencia, cada petición supera la validación de estado y puede activar su propio reembolso y su propia orden de recolección.
- **Impacto:** Pérdidas económicas por reembolsos duplicados, conciliación contable compleja y restituciones repetidas del cupón. También se generan órdenes de recolección duplicadas, con costos logísticos y errores operativos en el almacén.
- **Riesgo:** medio (2×2). Reenviar peticiones en paralelo es trivial y se asume sin idempotencia (SN-03, SN-04), pero la conciliación acota la pérdida a reembolsos duplicados por orden.
- **Controles:**
  - *preventivo* (ecommerce): Implementar una máquina de estados con transición atómica (bloqueo de fila o control de versión) de la orden a 'cancelación en curso', de modo que solo una solicitud supere la validación y las demás reciban un rechazo.
  - *preventivo* (ecommerce): Enviar a la pasarela una clave de idempotencia única por reembolso, derivada del identificador de orden, y deduplicar las confirmaciones repetidas de recolección e inspección.
  - *preventivo* (pasarela de pago): Rechazar solicitudes de reembolso con clave de idempotencia repetida y que el total reembolsado supere el monto capturado de la transacción.
  - *preventivo* (proveedor logístico): Deduplicar las órdenes de recolección inversa por identificador de orden de origen, de modo que solo exista una activa por orden.
  - *detectivo* (ecommerce): Conciliar a diario reembolsos contra pagos y alertar cuando una orden tenga más de un reembolso o una restitución de cupón, o varias recolecciones inversas abiertas.
  - *correctivo* (ecommerce): Recuperar los reembolsos duplicados del cliente, revertir las restituciones repetidas del cupón y cancelar las recolecciones inversas redundantes.
- **Referencias y patrones:** OWASP API6:2023 Unrestricted Access to Sensitive Business Flows, FE-14

<a id="av-0067"></a>
#### AV-0067 · Reutilización de cupón de un solo uso al encadenar compra, cancelación y restitución

- **ID de origen:** AC-UC13-02 · **Ejecución:** Lote 3 · **Tema de riesgo:** R6
- **STRIDE:** E — Elevación de privilegios
- **Actor:** Cliente que abusa de la restitución de cupones al cancelar (externo)
- **Elementos del DFD:** Marketplace, delivery-api, logistic, Pasarela de pago, Servicio de cupones (cupons-api, fuera del DFD de UC-13; supuesto nuevo SN-01) · **Límites:** LC-1, LC-4, LC-6
- **Precondiciones:**
  - La restitución del cupón al cancelar se dispara automáticamente y no espera al resultado de la inspección ni al cierre del reembolso (S-12: la política real de restitución no está definida)
  - El cupón es de un solo uso o tiene límite de usos por cliente (RN-4)
  - La restitución no comprueba si el producto volvió al almacén, ni cuántas restituciones acumuló el mismo cliente
  - SN-01: UC-13 no incluye cupons-api entre sus componentes, pero S-12 y UC-04 indican que el Marketplace le pide consumir y restituir cupones; se asume esa integración
- **Cómo ocurre:**
  1. El cliente aplica un cupón de alto valor en una compra (UC-04) y paga; cupons-api registra el cupón como consumido
  2. Recibe el producto y solicita la cancelación desde el Marketplace indicando un motivo; se genera la orden de recolección inversa
  3. El Marketplace pide a cupons-api restituir el cupón al aceptar la solicitud o al emitir el reembolso, sin esperar la inspección ni la confirmación de recolección
  4. El cliente usa el cupón restituido en una nueva compra, con la misma cuenta o con cuentas nuevas, y repite el ciclo; así supera el límite de un uso por cliente que RN-4 pretende imponer
  5. En el escenario de restitución al aceptar la solicitud, el cliente no entrega el paquete al proveedor logístico y la devolución queda sin completar, pero el cupón ya fue restituido y nada vuelve a bloquearlo
  6. El cliente conserva el producto con el descuento original y disfruta otra vez del cupón, ejerciendo un beneficio al que no tiene derecho según la regla de negocio
- **Vector práctico:** El cliente usa la interfaz normal del Marketplace (app o web) con su sesión legítima para solicitar la cancelación de una orden pagada con cupón y, una vez restituido el cupón, aplicarlo en una compra nueva. No modifica ningún dato ni el historial de cupones: el abuso consiste en ejercer un privilegio que no le corresponde, un nuevo uso de un cupón de un solo uso, porque el flujo de restitución lo concede sin comprobar el estado final de la devolución. El dato aprovechado es el estado de la orden entre 'cancelación solicitada' y 'devolución recibida e inspeccionada', que desencadena la restitución sin una autorización que dependa de la recuperación del producto.
- **Impacto:** Descuentos acumulados sin control, pérdida de margen y agotamiento del presupuesto promocional. Cupones diseñados como únicos se usan repetidamente y las métricas de uso por cliente quedan distorsionadas. Si la devolución nunca se completa, el cliente conserva además el producto con descuento.
- **Riesgo:** medio (2×2). La política de restitución no está definida (S-12) y el ciclo se puede repetir con cuentas nuevas, pero el impacto se limita al valor del descuento y al presupuesto promocional.
- **Controles:**
  - *preventivo* (ecommerce): Restituir el cupón solo cuando la devolución esté recibida e inspeccionada como conforme en almacén, y no al aceptar la solicitud ni al iniciar el reembolso.
  - *preventivo* (ecommerce): Limitar las restituciones por cliente, dispositivo y medio de pago, y vincular el cupón restituido a la cuenta original con la misma vigencia, para impedir su uso en cuentas nuevas.
  - *detectivo* (ecommerce): Alertar por ciclos repetidos de compra con cupón, cancelación y restitución, y correlacionar cuentas distintas que compartan dirección, dispositivo o medio de pago.
  - *detectivo* (pasarela de pago): Proporcionar al ecommerce una huella o token estable del medio de pago para correlacionar cuentas que reutilizan cupones restituidos.
  - *correctivo* (ecommerce): Revocar el cupón restituido si la devolución no se completa en el plazo definido, cobrar al cliente el descuento y bloquear la cuenta de uso de cupones ante reincidencia.
- **Referencias y patrones:** OWASP API6:2023 Unrestricted Access to Sensitive Business Flows, S-12, UC-04, FE-14

### UC-14 Administración interna de clientes y perfiles

<a id="av-0068"></a>
#### AV-0068 · Consulta masiva de datos personales de clientes sin caso de soporte para vender o usar la información

- **ID de origen:** AC-UC14-01 · **Ejecución:** Lote 3 · **Tema de riesgo:** R7
- **STRIDE:** I (R) — Divulgación de información
- **Actor:** Operador de atención a clientes con acceso de lectura a perfiles en clients-admin-front (interno)
- **Elementos del DFD:** clients-admin-front, clients-api, F27, F11, LC-3 · **Límites:** LC-3
- **Precondiciones:**
  - El operador tiene una cuenta válida con permiso de búsqueda y consulta de clientes
  - La búsqueda no exige un caso o ticket abierto asociado al cliente consultado
  - clients-api devuelve datos personales completos (nombre, teléfono, direcciones) sin enmascarar y sin límite de consultas por operador
- **Cómo ocurre:**
  1. El operador se autentica en clients-admin-front con su usuario habitual
  2. Busca clientes sin ticket asociado, por zona, nivel o membresía, y abre perfil tras perfil
  3. Identifica a los clientes de nivel alto o con compras de alto valor, y consulta sus direcciones y teléfonos
  4. Copia los datos a un archivo externo o los fotografía de la pantalla
  5. Vende la lista a terceros o la entrega a quien planea robos en domicilios o en entregas
- **Vector práctico:** Acción: consulta repetida y sistemática de perfiles fuera de cualquier caso de soporte. Herramienta: la propia interfaz de búsqueda de clients-admin-front, más copia manual o captura de pantalla. Dato manipulado: nombre, teléfono, correo, direcciones y atributos de nivel o membresía de los clientes.
- **Impacto:** Fuga de datos personales de clientes con riesgo para su seguridad física (robos dirigidos), incumplimiento de protección de datos personales y daño reputacional. Si no hay correlación con tickets, la detección es tardía.
- **Riesgo:** alto (2×3). Un operador legítimo ya tiene acceso y hoy no hay enmascaramiento ni límites, y la fuga de direcciones de clientes de alto valor puede derivar en robos físicos y en incumplimiento de protección de datos.
- **Controles:**
  - *preventivo* (ecommerce): clients-api solo devuelve el perfil completo si el operador tiene un ticket abierto asignado a ese cliente. La validación se hace en el servidor, no solo en clients-admin-front.
  - *preventivo* (ecommerce): Enmascarar por defecto teléfono, correo y direcciones en búsquedas y perfiles. Revelar cada campo exige indicar el motivo, y la revelación queda registrada. Poner límite de perfiles abiertos por operador y hora, sin función de exportación y con marca de agua con el usuario en pantalla.
  - *detectivo* (ecommerce): Alertas automáticas por consultas sin ticket asociado, volumen de perfiles abiertos superior a la media del equipo y búsquedas orientadas a nivel o membresía alta. Revisión trimestral de accesos por parte del responsable de atención.
  - *correctivo* (ecommerce): Suspender de inmediato el acceso del operador sospechoso, revisar los perfiles consultados, notificar a los clientes afectados y a la autoridad de protección de datos según el procedimiento de incidentes, y aplicar la medida disciplinaria o legal que corresponda.
- **Referencias y patrones:** CAPEC-575, OWASP API1:2023, FE-16

<a id="av-0069"></a>
#### AV-0069 · Operador reemplaza correo o teléfono de un cliente para tomar o vender su cuenta

- **ID de origen:** AC-UC14-02 · **Ejecución:** Lote 3 · **Tema de riesgo:** R3
- **STRIDE:** T (S, E) — Manipulación
- **Actor:** Operador de atención a clientes sobornado o con intención de fraude (interno)
- **Elementos del DFD:** clients-admin-front, clients-api, F27, F11, LC-3 · **Límites:** LC-3
- **Precondiciones:**
  - El operador puede editar correo y teléfono del perfil desde clients-admin-front
  - clients-api acepta el cambio de contacto de un empleado sin repetir la verificación con código de un solo uso al nuevo correo o teléfono
  - No se notifica al titular en sus datos de contacto anteriores
- **Cómo ocurre:**
  1. Un tercero que ha pagado al operador, o el propio operador, elige una cuenta con medios de pago guardados o historial de compras
  2. El operador abre el perfil en clients-admin-front y sustituye el correo y el teléfono por datos controlados por el tercero
  3. clients-api guarda el cambio por F27 sin verificar la propiedad del nuevo contacto y sin avisar al titular
  4. El tercero usa la recuperación de acceso del Marketplace, que envía el código al contacto nuevo, y entra en la cuenta
  5. Compra con medios de pago guardados o desvía entregas con direcciones guardadas, y el titular pierde el acceso
- **Vector práctico:** Acción: edición de los campos de correo y teléfono de un perfil ajeno y posterior uso del flujo de recuperación de acceso. Herramienta: formulario de edición de clients-admin-front y el flujo estándar de recuperación del Marketplace. Dato manipulado: correo y teléfono de contacto del cliente, que sirven como factor de recuperación y verificación.
- **Impacto:** Toma de cuenta habilitada desde dentro, compras fraudulentas con medios de pago del cliente, pérdida del acceso del titular y posible incumplimiento de RN-1 si el contacto se reutiliza.
- **Riesgo:** alto (2×3). Cambiar el contacto sin verificar la propiedad del nuevo correo o teléfono permite tomar la cuenta mediante la recuperación estándar y usar medios de pago guardados, con pérdida económica directa para el cliente.
- **Controles:**
  - *preventivo* (ecommerce): El cambio de correo o teléfono desde backoffice exige un código de un solo uso enviado al nuevo contacto, un motivo con ticket y la aprobación de un segundo empleado (cuatro ojos) antes de que clients-api lo persista.
  - *preventivo* (ecommerce): Bloquear la recuperación de acceso y los cambios de dirección durante 72 horas tras un cambio de contacto hecho por backoffice, salvo validación reforzada del titular.
  - *preventivo* (pasarela de pago): Exigir autenticación reforzada (3-D Secure o equivalente) en pagos con medio guardado tokenizado, para que el control sobre el correo no baste para comprar.
  - *detectivo* (ecommerce): Notificar al contacto anterior cada cambio de correo o teléfono con enlace de reversión. Alertar cuando a un cambio de contacto por backoffice le sigan una recuperación de acceso y una compra en menos de 72 horas.
  - *detectivo* (pasarela de pago): Aplicar puntuación antifraude a los pagos con medio guardado, con reglas de velocidad y de cambio reciente de datos de contacto, y marcar para revisión las transacciones de riesgo.
  - *correctivo* (ecommerce): Revertir el contacto al valor anterior usando el historial de cambios, bloquear la cuenta hasta verificar al titular, anular los pedidos pendientes de despacho y gestionar la devolución o el contracargo de los pagos fraudulentos.
  - *correctivo* (pasarela de pago): Reversar o disputar las transacciones identificadas como fraudulentas y bloquear el token del medio de pago afectado.
- **Referencias y patrones:** OWASP API2:2023, AV-0012, FE-11

<a id="av-0070"></a>
#### AV-0070 · Cambios de perfil sin autoría fiable por cuenta compartida o historial modificable

- **ID de origen:** AC-UC14-03 · **Ejecución:** Lote 3 · **Tema de riesgo:** R3
- **STRIDE:** R (T) — Repudio
- **Actor:** Operador de atención a clientes que comparte credenciales o puede alterar el historial (interno)
- **Elementos del DFD:** clients-admin-front, clients-api, F27, LC-3 · **Límites:** LC-3
- **Precondiciones:**
  - Varios operadores usan una misma cuenta de clients-admin-front, o el historial de cambios se registra sin identificar al empleado de forma inequívoca
  - El historial de cambios es editable o eliminable con el mismo rol que edita perfiles
  - Los cambios no exigen motivo ni referencia a un caso
- **Cómo ocurre:**
  1. El operador realiza cambios indebidos en datos personales o atributos de perfil de varios clientes desde la cuenta compartida
  2. clients-api registra los cambios con un usuario genérico, sin motivo y sin ticket
  3. Cuando se detecta una anomalía, el operador niega haberlas hecho amparándose en que la cuenta es de uso común
  4. Si tiene permiso sobre el registro, elimina o edita las entradas del historial de los clientes afectados para borrar el rastro
- **Vector práctico:** Acción: ediciones de perfil desde una cuenta de uso compartido y, si es posible, edición o borrado de entradas del historial de cambios. Herramienta: interfaz de clients-admin-front con credenciales comunes. Dato manipulado: registro del historial de cambios (autor, fecha, valor anterior y nuevo) y atributos del perfil.
- **Impacto:** No se puede atribuir a una persona la modificación indebida de datos, se impide la investigación de fraudes internos y se pierde la integridad del historial como evidencia.
- **Riesgo:** medio (2×2). Las cuentas compartidas y los historiales editables son una debilidad habitual de los backoffices, y aunque no causan el daño directo, impiden atribuir y probar cualquier otro abuso interno.
- **Controles:**
  - *preventivo* (ecommerce): Eliminar las cuentas compartidas y usar solo cuentas nominales vinculadas al directorio corporativo (SSO) con baja automática al salir del empleado. Exigir motivo y referencia de ticket en todo cambio de perfil.
  - *preventivo* (ecommerce): El historial de cambios es de solo adición, con autor, fecha, valor anterior y valor nuevo. Ningún rol de atención puede editarlo ni borrarlo, y se replica a un almacenamiento externo inmutable o a un SIEM.
  - *detectivo* (ecommerce): Alertas por sesiones simultáneas de una misma cuenta desde distintos dispositivos o ubicaciones, por cambios sin ticket y por cualquier intento de modificar o borrar el historial. Conciliación periódica del historial contra los logs de clients-api.
  - *correctivo* (ecommerce): Reconstruir los cambios afectados desde los logs de clients-api y las copias de respaldo, rotar las credenciales compartidas existentes y revisar los cambios del período en que no hubo autoría fiable.
- **Referencias y patrones:** FE-15, AV-0031

<a id="av-0071"></a>
#### AV-0071 · Operador envía directamente a clients-api campos que el front no expone para ampliar sus privilegios o los de terceros

- **ID de origen:** AC-UC14-04 · **Ejecución:** Lote 3 · **Tema de riesgo:** R3
- **STRIDE:** E (T) — Elevación de privilegios
- **Actor:** Operador de atención a clientes con conocimientos técnicos (interno)
- **Elementos del DFD:** clients-admin-front, clients-api, F27, LC-3 · **Límites:** LC-3
- **Precondiciones:**
  - El operador tiene una sesión válida y puede observar las peticiones que clients-admin-front envía a clients-api
  - clients-api valida que el usuario esté autenticado como empleado, pero no controla por función ni por campo qué rol puede cambiar cada atributo
  - El objeto de perfil incluye campos sensibles (estado de la cuenta, atributos de beneficio, marcas internas) que la interfaz no muestra al operador de atención
- **Cómo ocurre:**
  1. El operador abre las herramientas del navegador y observa la petición de guardado que viaja por F27
  2. La reenvía con un proxy de interceptación, añadiendo o cambiando campos del objeto de perfil que la interfaz no ofrece
  3. clients-api acepta el objeto completo y persiste campos reservados a otros roles o a procesos del servidor
  4. El operador modifica el estado o los beneficios de cuentas propias o de conocidos, y su cambio queda como una edición normal de perfil
- **Vector práctico:** Acción: reenvío modificado de la petición de edición de perfil con campos adicionales no ofrecidos por la interfaz. Herramienta: proxy de interceptación y repetición de peticiones sobre el tráfico de clients-admin-front. Dato manipulado: cuerpo de la solicitud de F27, con atributos protegidos del perfil.
- **Impacto:** Elevación de privilegios dentro del backoffice y alteración de datos protegidos sin el control de otros roles, con efecto en beneficios, estado de cuentas y reglas como RN-2.
- **Riesgo:** alto (2×3). Si los permisos solo se aplican en el front, cualquier operador con un proxy puede escribir campos reservados, con efecto directo en beneficios y estado de cuentas.
- **Controles:**
  - *preventivo* (ecommerce): clients-api aplica autorización por función y por campo según el rol del empleado. Usa una lista permitida de campos editables por rol, rechaza con error cualquier campo desconocido o no autorizado y no hace binding automático del objeto de perfil completo.
  - *preventivo* (ecommerce): Los atributos de beneficio (nivel, membresía, estado de la cuenta, marcas internas) solo los modifican procesos del servidor o un flujo con justificación y aprobación de otro rol. El envío se recalcula al confirmar el pago.
  - *detectivo* (ecommerce): Registrar y alertar los intentos de escritura de campos no permitidos por operador y las ediciones de beneficios sobre cuentas propias o relacionadas. Incluir pruebas automáticas de autorización por función y campo en el pipeline antes del despliegue.
  - *correctivo* (ecommerce): Revertir los atributos alterados al valor anterior desde el historial, recalcular los envíos de pedidos afectados, revocar los permisos del operador y revisar todas sus ediciones previas.
- **Referencias y patrones:** OWASP API5:2023, CAPEC-384, AV-0014, FE-06

<a id="av-0072"></a>
#### AV-0072 · Edición de identificadores del perfil para duplicar o fusionar registros y eludir la unicidad del cliente

- **ID de origen:** AC-UC14-06 · **Ejecución:** Lote 3 · **Tema de riesgo:** R3
- **STRIDE:** T (E) — Manipulación
- **Actor:** Operador de atención a clientes que colabora con un cliente defraudador (interno)
- **Elementos del DFD:** clients-admin-front, clients-api, F27, F11, LC-3 · **Límites:** LC-3
- **Precondiciones:**
  - El operador puede editar correo, teléfono y datos de identidad del perfil
  - clients-api no repite la validación de unicidad de RN-1 en las ediciones hechas desde backoffice, o permite forzarla
  - No existe aprobación para modificar los identificadores del cliente
- **Cómo ocurre:**
  1. Un cliente con una cuenta bloqueada o con historial negativo pide al operador que le habilite otra cuenta
  2. El operador cambia el correo o teléfono de un perfil para que coincida con un identificador usado por otro registro, o altera los de la cuenta bloqueada para liberarlos
  3. clients-api guarda el cambio por F27 sin rechazar el duplicado
  4. Se generan dos perfiles con el mismo identificador, o el cliente recupera una cuenta con otro historial, y se aprovechan promociones o beneficios pensados para registros únicos
  5. Las operaciones posteriores quedan asociadas a un registro ambiguo
- **Vector práctico:** Acción: edición manual de los identificadores del perfil para forzar duplicados o reasignarlos entre cuentas. Herramienta: formulario de edición de clients-admin-front. Dato manipulado: correo, teléfono y datos de identidad que sustentan el registro único del cliente (RN-1).
- **Impacto:** Pérdida de integridad del registro único del cliente, evasión de bloqueos o límites por cliente, abuso de promociones y datos inconsistentes en los demás servicios que consultan clients-api.
- **Riesgo:** medio (2×2). Requiere la colaboración de un operador con un cliente defraudador y afecta sobre todo a la integridad del registro único, a promociones y a bloqueos, sin fuga masiva de datos.
- **Controles:**
  - *preventivo* (ecommerce): Restricción de unicidad de correo y teléfono en la base de datos y validación de RN-1 en clients-api para todas las ediciones, incluidas las de backoffice, sin opción de forzar el duplicado.
  - *preventivo* (ecommerce): Cambios en identificadores y datos de identidad con motivo, ticket y aprobación de un segundo empleado. Prohibir la edición de identificadores de cuentas bloqueadas o con historial negativo salvo por un rol de riesgo.
  - *detectivo* (ecommerce): Reporte periódico de cambios de identificador, de identificadores liberados desde cuentas bloqueadas y de posibles duplicados, con alerta cuando un operador repite este tipo de cambios.
  - *correctivo* (ecommerce): Restaurar los identificadores originales, separar o fusionar los registros mediante un procedimiento auditado, reevaluar las promociones y beneficios otorgados y volver a bloquear la cuenta evadida.
- **Referencias y patrones:** AV-0031

<a id="av-0073"></a>
#### AV-0073 · Toma de una cuenta de operador por relleno de credenciales o phishing para leer y editar clientes

- **ID de origen:** AC-UC14-05 · **Ejecución:** Lote 3 · **Tema de riesgo:** R5
- **STRIDE:** S (I, T, E) — Suplantación
- **Actor:** Atacante con credenciales filtradas o capacidad de phishing contra empleados (externo)
- **Elementos del DFD:** clients-admin-front, clients-api, F27, LC-3 · **Límites:** LC-3
- **Precondiciones:**
  - clients-admin-front es accesible desde fuera de la red corporativa o desde una red que el atacante alcanza (supuesto nuevo, ver supuestos)
  - La autenticación del operador depende solo de usuario y contraseña, sin segundo factor ni restricción por dispositivo (supuesto nuevo, ver supuestos)
  - El atacante dispone de credenciales reutilizadas de un empleado o puede engañarlo con una página falsa de inicio de sesión
- **Cómo ocurre:**
  1. El atacante obtiene un listado de credenciales filtradas de otros servicios o prepara un correo de phishing con un portal que imita clients-admin-front
  2. Prueba las credenciales contra el inicio de sesión de clients-admin-front o recoge las que introduce el empleado en el portal falso, y entra con la identidad del operador
  3. Con la sesión del operador busca y abre perfiles de clientes, y copia nombres, teléfonos y direcciones de clientes de alto valor
  4. Edita atributos de perfil (nivel, membresía) o datos de contacto de cuentas elegidas; clients-admin-front envía el cambio a clients-api por F27 y este lo guarda al ser una sesión de operador válida
  5. Las acciones quedan registradas en el historial de cambios con la identidad del operador legítimo, por lo que la actividad del atacante es indistinguible de la del empleado
- **Vector práctico:** Acción: inicio de sesión en clients-admin-front con la identidad de un operador usando credenciales reutilizadas o capturadas por un portal falso. Herramienta: herramienta de automatización de intentos de acceso con listas de credenciales filtradas, o kit de phishing que clona la pantalla de acceso. Dato manipulado: credenciales y sesión del operador y, con ellas, datos personales y atributos de los perfiles de clientes.
- **Impacto:** Acceso a todo el padrón de clientes con los privilegios del operador, fuga masiva de datos personales, modificaciones fraudulentas de perfiles (beneficios o toma de cuentas) atribuidas a un empleado inocente y dificultad para investigar el incidente.
- **Riesgo:** alto (2×3). El relleno de credenciales y el phishing son frecuentes y, sin segundo factor ni restricción de red, una sola cuenta de operador da acceso a datos y edición de clientes con las acciones atribuidas a un inocente.
- **Controles:**
  - *preventivo* (ecommerce): MFA obligatorio y resistente al phishing (FIDO2/WebAuthn) para todos los operadores de clients-admin-front, integrado con el SSO corporativo.
  - *preventivo* (ecommerce): Restringir el acceso a clients-admin-front a VPN o red corporativa y a dispositivos gestionados. Aplicar límite de intentos por usuario e IP, bloqueo progresivo y verificación de contraseñas contra listas de credenciales filtradas.
  - *detectivo* (ecommerce): Alertas por inicios de sesión desde dispositivo, país o IP nuevos, por muchos fallos contra muchas cuentas y por acceso masivo a perfiles o ediciones de beneficio justo después de un inicio de sesión inusual.
  - *correctivo* (ecommerce): Revocar las sesiones activas, forzar el cambio de contraseña y el re-registro del segundo factor, revisar y revertir los cambios hechos durante la sesión comprometida y notificar a los clientes cuyos datos se consultaron.
- **Referencias y patrones:** OWASP API2:2023 Broken Authentication, CAPEC-575 Account Footprinting, AV-0012, FE-11

### UC-15 Administración interna de cupones

<a id="av-0074"></a>
#### AV-0074 · Toma de cuenta de un operador de marketing para crear cupones de alto valor desde cupons-frontend

- **ID de origen:** AC-UC15-01 · **Ejecución:** Lote 3 · **Tema de riesgo:** R5
- **STRIDE:** S (E, T) — Suplantación
- **Actor:** Atacante externo que suplanta a un operador de marketing y promociones (externo)
- **Elementos del DFD:** cupons-frontend, cupons-api, F28, F12 · **Límites:** LC-3
- **Precondiciones:**
  - El acceso a cupons-frontend se protege solo con usuario y contraseña, o con un segundo factor que se puede interceptar o fatigar
  - El atacante tiene credenciales del operador obtenidas por suplantación de identidad, reutilización de contraseñas filtradas o malware en su estación
  - cupons-api acepta como legítima cualquier sesión autenticada del rol de marketing sin comprobar dispositivo, origen ni contexto (S-21)
  - No hay aprobación doble ni alertas por creación de cupones fuera de campaña
- **Cómo ocurre:**
  1. El atacante envía un correo de suplantación al operador con una página falsa de inicio de sesión de cupons-frontend, o prueba credenciales filtradas contra el acceso
  2. Captura usuario, contraseña y el código de segundo factor, o reutiliza la sesión activa del navegador del operador
  3. Inicia sesión en cupons-frontend desde una red anónima con la identidad del operador
  4. Crea un cupón con descuento alto, segmento amplio, vigencia larga y usos totales muy altos, y lo activa; la petición viaja por F28 a cupons-api
  5. cupons-api lo guarda en el almacén de cupones y usos (F12) como disponible para el checkout
  6. El atacante reparte o vende el código a terceros y todo queda registrado a nombre del operador legítimo
- **Vector práctico:** El atacante usa una página de captura de credenciales o credenciales filtradas para obtener la sesión del operador. Con el navegador abre el formulario de alta de cupones de cupons-frontend y manipula la definición del cupón (valor, vigencia, usos totales, segmento). Esa definición es el dato que cupons-api acepta como legítimo porque proviene de una cuenta autenticada.
- **Impacto:** Pérdida directa de margen por descuentos fraudulentos, agotamiento del presupuesto de campaña y venta de códigos en canales externos. La bitácora atribuye la acción al operador, lo que genera una investigación interna errónea y dificulta el repudio legítimo. Si los controles no distinguen un origen anómalo, el abuso se detecta solo al revisar márgenes.
- **Riesgo:** alto (2×3). El phishing y la reutilización de credenciales son frecuentes y, con un segundo factor interceptable, una sesión robada permite activar cupones de alto valor atribuidos a otro operador, con pérdida de margen y de presupuesto.
- **Controles:**
  - *preventivo* (ecommerce): Exigir MFA resistente a suplantación (FIDO2/WebAuthn) en cupons-frontend para el rol de marketing y bloquear el acceso desde redes anónimas (Tor, VPN públicas) o fuera de la red corporativa o VPN de la empresa.
  - *preventivo* (ecommerce): Exigir en cupons-api aprobación doble (un segundo usuario distinto del creador) para activar cupones con descuento alto, sin límite de usos, con vigencia larga o con segmento amplio, y aplicar topes por rol validados en el servidor.
  - *preventivo* (ecommerce): Vincular la sesión al dispositivo y al contexto (token ligado al dispositivo, expiración corta, reautenticación con MFA antes de activar o distribuir un cupón).
  - *detectivo* (ecommerce): Alertar en tiempo real por inicios de sesión desde ubicación, ASN o dispositivo nuevos, por creación de cupones fuera de campañas aprobadas y por uso concentrado de un cupón en pocas cuentas relacionadas; enviar la alerta al SOC.
  - *correctivo* (ecommerce): Procedimiento de respuesta: revocar sesiones y credenciales del operador, desactivar de inmediato los cupones creados durante la sesión sospechosa, anular o revisar las órdenes que los canjearon y restablecer el acceso con verificación presencial o por canal alterno.
- **Referencias y patrones:** CAPEC-701, OWASP API6:2023 Unrestricted Access to Sensitive Business Flows, FE-05, AV-0029

<a id="av-0075"></a>
#### AV-0075 · Agencia externa con acceso al backoffice exporta segmentos de clientes y cupones personales

- **ID de origen:** AC-UC15-03 · **Ejecución:** Lote 3 · **Tema de riesgo:** R7
- **STRIDE:** I (E) — Divulgación de información
- **Actor:** Usuario de agencia de marketing contratada con una cuenta en cupons-frontend (interno de tercero)
- **Elementos del DFD:** cupons-frontend, cupons-api, F28, F12 · **Límites:** LC-3
- **Precondiciones:**
  - La agencia recibió una cuenta con permiso de distribuir cupones a segmentos
  - El rol de la agencia permite ver y descargar el segmento asignado, los códigos generados y el presupuesto de las campañas, aunque no sean suyas
  - cupons-api no restringe la consulta de segmentos y códigos a las campañas del tercero
  - No hay registro ni alerta de exportaciones masivas
- **Cómo ocurre:**
  1. Un usuario de la agencia inicia sesión en cupons-frontend con su cuenta legítima
  2. Abre el listado de campañas y segmentos, y consulta también campañas ajenas cambiando el identificador en la consulta que cupons-frontend hace a cupons-api
  3. Descarga los códigos de cupones personales o de alto valor, la composición de los segmentos de clientes y el presupuesto de cada campaña
  4. Entrega esos datos a otro cliente de la agencia, los vende o los usa con cuentas propias
  5. Los códigos obtenidos se canjean en el checkout por cuentas que no son las destinatarias
- **Vector práctico:** El usuario de la agencia usa la función de listado o exportación de cupons-frontend, y con un proxy de interceptación cambia el identificador de campaña o segmento en las consultas hacia cupons-api. Así obtiene códigos de cupón, la lista de clientes de cada segmento y el presupuesto de campañas que no le fueron asignadas.
- **Impacto:** Fuga de códigos de descuento y de información comercial confidencial (presupuestos, criterios de segmentación) y exposición de la lista de clientes de segmentos sensibles. Los códigos filtrados se canjean por personas no elegibles, con pérdida económica y posible incumplimiento de obligaciones de protección de datos con el tercero.
- **Riesgo:** medio (2×2). Cambiar el identificador de campaña o segmento es trivial si cupons-api no comprueba la pertenencia al tercero; el daño combina fuga de códigos, de presupuestos y de listas de clientes, pero queda acotado al alcance de las cuentas de agencia.
- **Controles:**
  - *preventivo* (ecommerce): Autorizar en cupons-api cada consulta por objeto: validar que el identificador de campaña o segmento pertenezca al tercero (control de acceso a nivel de objeto) y responder 404 o 403 uniformes ante identificadores ajenos.
  - *preventivo* (ecommerce): Reducir el rol de la agencia al mínimo: sin acceso al presupuesto de campañas, con códigos personales enmascarados o enviados directamente por el sistema sin descarga, y con segmentos expuestos solo como identificadores seudonimizados.
  - *preventivo* (ecommerce): Ligar los cupones personales a la cuenta destinataria y validarlo en el checkout, de modo que un código filtrado no sea canjeable por otras cuentas.
  - *detectivo* (ecommerce): Registrar toda consulta y exportación de segmentos y códigos con usuario, campaña y volumen; alertar por exportaciones masivas, por accesos a campañas no asignadas y por canjes de cupones personales desde cuentas distintas a la destinataria.
  - *correctivo* (ecommerce): Suspender la cuenta de la agencia, regenerar o invalidar los códigos expuestos, notificar a la agencia y activar el procedimiento de incidentes de datos personales conforme al contrato y a la normativa aplicable.
- **Referencias y patrones:** CAPEC-240, OWASP API9:2023 Improper Inventory Management, FE-04, FE-05, API6:2023

<a id="av-0076"></a>
#### AV-0076 · Operador modifica un cupón activo y borra la evidencia de su cambio para negar la autoría

- **ID de origen:** AC-UC15-04 · **Ejecución:** Lote 3 · **Tema de riesgo:** R3
- **STRIDE:** R (T) — Repudio
- **Actor:** Operador de marketing y promociones con permiso de edición de cupones (interno)
- **Elementos del DFD:** cupons-frontend, cupons-api, F28, F12 · **Límites:** LC-3
- **Precondiciones:**
  - La edición de un cupón activo sobrescribe la definición anterior sin conservar versiones
  - La bitácora de cupons-api registra solo el estado final, o puede ser editada o depurada por quien administra la campaña
  - Varios operadores comparten una cuenta o una cuenta genérica de campaña
  - El operador sabe que los márgenes se revisan con retraso
- **Cómo ocurre:**
  1. Un operador edita un cupón activo para ampliar su vigencia, subir el valor o quitar el monto mínimo, y se beneficia o beneficia a terceros durante algunas horas
  2. Antes de la revisión de márgenes, restaura los valores originales desde cupons-frontend, o elimina el cupón y crea uno equivalente
  3. cupons-api guarda solo la última definición, de modo que el historial no muestra el cambio intermedio
  4. Cuando se detectan órdenes con descuentos fuera de política, el cupón figura con reglas correctas y la bitácora no identifica quién hizo la edición
  5. El operador niega haber hecho el cambio y señala a otros usuarios con acceso a la campaña
- **Vector práctico:** El operador usa el formulario de edición y la función de desactivar o eliminar cupones de cupons-frontend para modificar y luego restaurar la definición del cupón (vigencia, valor, monto mínimo). Así elimina de la fuente de verdad en cupons-api la evidencia del periodo en que las reglas eran más favorables, apoyándose en una bitácora mutable o sin versiones.
- **Impacto:** No es posible atribuir el abuso ni reconstruir qué órdenes se beneficiaron de reglas alteradas, lo que impide recuperar pérdidas, sancionar y reconciliar el presupuesto de campaña. Se incumple la trazabilidad esperada para las operaciones de RN-4.
- **Riesgo:** medio (2×2). Un operador interno con permiso de edición y sin versionado puede hacer un cambio temporal y restaurarlo con poco esfuerzo, y la falta de atribución impide recuperar pérdidas, aunque el abuso es de alcance acotado en el tiempo.
- **Controles:**
  - *preventivo* (ecommerce): Versionar cada definición de cupón en cupons-api: la edición crea una nueva versión inmutable (quién, cuándo, valores anteriores y nuevos) y el borrado es lógico, sin eliminación física por parte de operadores.
  - *preventivo* (ecommerce): Eliminar cuentas compartidas o genéricas de campaña, exigir cuentas nominales con MFA y requerir aprobación doble para modificar cupones activos (vigencia, valor, monto mínimo).
  - *preventivo* (ecommerce): Enviar la bitácora de cambios a un almacenamiento de solo anexado (WORM) con firma o encadenamiento de hashes, fuera del alcance de quienes administran campañas.
  - *detectivo* (ecommerce): Conciliar de forma automática cada orden con la versión del cupón vigente al momento del canje; alertar por cambios de definición seguidos de restauración en pocas horas y por canjes bajo reglas distintas de las actuales.
  - *correctivo* (ecommerce): Reconstruir con la bitácora inmutable las versiones y las órdenes beneficiadas, recuperar o ajustar el presupuesto afectado y aplicar el proceso disciplinario con evidencia atribuible.
- **Referencias y patrones:** CAPEC-39, FE-05, AV-0029, AV-0035

<a id="av-0077"></a>
#### AV-0077 · Operador descontento desactiva o altera masivamente cupones de una campaña vigente

- **ID de origen:** AC-UC15-05 · **Ejecución:** Lote 3 · **Tema de riesgo:** R3
- **STRIDE:** D (T) — Denegación de servicio
- **Actor:** Operador de marketing y promociones con permisos de edición y activación masiva (interno)
- **Elementos del DFD:** cupons-frontend, cupons-api, F28, F12 · **Límites:** LC-3
- **Precondiciones:**
  - El operador tiene permiso para editar, desactivar o reasignar cupones de campañas que no creó
  - Existe una función de acción masiva o la edición es rápida sobre muchas definiciones
  - No se exige aprobación ni hay confirmación diferida para cambios en campañas vigentes
  - cupons-api aplica de inmediato los cambios a la validación del checkout
- **Cómo ocurre:**
  1. Durante un periodo de alta demanda, el operador entra a cupons-frontend con su sesión legítima
  2. Selecciona las campañas vigentes y las desactiva, adelanta su fecha de fin, reduce los usos totales a cero o cambia el segmento a uno vacío
  3. cupons-api guarda los cambios por F28 y deja las reglas inconsistentes en F12
  4. En el checkout, cupons-api rechaza los cupones legítimos de los clientes, que ven mensajes de código inválido o vencido
  5. Aumentan los abandonos de carrito y las solicitudes a soporte mientras el equipo busca la causa, y la reversión manual es lenta
- **Vector práctico:** El operador usa la función de edición o desactivación masiva de cupons-frontend para cambiar en las definiciones de cupón de campañas vigentes los campos de estado, vigencia, usos totales y segmento. Esos cambios llegan por F28 a cupons-api y hacen que la validación del checkout rechace cupones legítimos.
- **Impacto:** Caída de conversión durante una campaña, pérdida de ventas, deterioro de la confianza de clientes que tenían cupones válidos y costos de soporte y de reconstrucción de las reglas originales. Puede incumplirse además la promesa de descuento comunicada al cliente.
- **Riesgo:** bajo (1×2). Requiere un insider motivado, pero con permisos amplios y cambios aplicados al instante la interrupción de una campaña vigente es fácil, con pérdida de ventas y costo de soporte y reversión lenta.
- **Controles:**
  - *preventivo* (ecommerce): Limitar el permiso de editar, desactivar o reasignar cupones a las campañas de las que el operador es responsable, y exigir aprobación de un segundo usuario o confirmación diferida para acciones masivas o para cambios sobre campañas vigentes.
  - *preventivo* (ecommerce): Poner topes en cupons-api al número de cupones modificables por operación y por ventana de tiempo, y bloquear cambios como usos totales en cero, segmento vacío o fecha de fin adelantada en campañas vigentes sin aprobación.
  - *detectivo* (ecommerce): Monitorear la tasa de rechazo de cupones en el checkout y las ediciones masivas; alertar al equipo de marketing y de operaciones cuando se supere un umbral sobre la línea base o se desactiven varias campañas en poco tiempo.
  - *correctivo* (ecommerce): Mantener respaldos versionados de las definiciones de cupón con función de reversión de un clic a la versión previa aprobada, y un procedimiento de comunicación al cliente y de soporte durante la restauración.
- **Referencias y patrones:** OWASP API6:2023 Unrestricted Access to Sensitive Business Flows, FE-05

<a id="av-0078"></a>
#### AV-0078 · Operador de marketing excede los topes de su rol al enviar por F28 una definición de cupón que cupons-api no autoriza

- **ID de origen:** AC-UC15-02 · **Ejecución:** Lote 3 · **Tema de riesgo:** R3
- **STRIDE:** E (T, R) — Elevación de privilegios
- **Actor:** Operador de marketing y promociones con acceso a cupons-frontend (interno)
- **Elementos del DFD:** cupons-frontend, cupons-api, F28, F12 · **Límites:** LC-3
- **Precondiciones:**
  - Los topes por rol (descuento máximo, vigencia máxima, segmento permitido, presupuesto asignado) se aplican solo en la interfaz de cupons-frontend
  - cupons-api acepta los campos recibidos en F28 sin comprobar en el servidor la autorización del rol sobre cada campo ni compararlos con el presupuesto de la campaña
  - El operador puede usar un proxy de interceptación en su navegador
  - No se exige segunda aprobación para activar el cupón
- **Cómo ocurre:**
  1. El operador llena el formulario de cupón con valores permitidos por su rol, por ejemplo un descuento moderado y un segmento acotado
  2. Con un proxy de interceptación detiene la petición de creación o edición que cupons-frontend envía a cupons-api por F28
  3. Sustituye en la petición campos que la interfaz limita u oculta: porcentaje de descuento, tope de usos por cliente, monto mínimo, vigencia, identificador de campaña o segmento asignado
  4. Reenvía la petición y cupons-api la acepta sin verificar si el rol del operador permite esos valores, y la deja disponible para validación en el checkout (F12)
  5. El cupón queda activo con descuento, vigencia o alcance que el operador no estaba autorizado a definir, mientras la interfaz sigue mostrando los valores originales si no relee el estado del servidor
  6. El operador distribuye el código a cuentas allegadas o lo vende; si se investiga, puede alegar que configuró solo los valores visibles en la interfaz
- **Vector práctico:** El operador usa un proxy de interceptación entre cupons-frontend y cupons-api para sustituir, en la petición de F28, los campos de la definición del cupón (porcentaje, usos por cliente, monto mínimo, vigencia, identificador de campaña o segmento). Con esa acción obtiene privilegios de configuración superiores a los de su rol, porque cupons-api no autoriza esos valores en el servidor; la alteración de la petición es solo el medio y el daño central es el exceso de privilegio.
- **Impacto:** El operador ejerce en la práctica privilegios que su rol no le otorga: crea cupones con descuentos o alcances fuera de política, imputados a una campaña con presupuesto que no corresponde o que no lo tiene. Se erosiona RN-4 por la pérdida económica en márgenes y en el presupuesto de campaña. La diferencia entre lo que muestra la interfaz y lo activo en el servidor dificulta la auditoría y permite al operador negar responsabilidad.
- **Riesgo:** alto (2×3). Interceptar y modificar la petición F28 es sencillo para un operador con un proxy cuando los topes están solo en la interfaz, y el resultado es un cupón activo fuera de política que afecta márgenes y presupuesto de campaña.
- **Controles:**
  - *preventivo* (ecommerce): Validar en cupons-api, del lado del servidor, la autorización por rol y por campo en cada petición de F28: descuento máximo, vigencia máxima, usos por cliente, segmento permitido y campaña asignada, con una lista blanca de campos aceptados y rechazo de valores fuera de tope.
  - *preventivo* (ecommerce): Comprobar en cupons-api que el costo máximo potencial del cupón (valor por usos totales) no exceda el presupuesto restante de la campaña asignada y que el operador tenga permiso sobre esa campaña.
  - *preventivo* (ecommerce): Requerir aprobación de una segunda persona para activar cupones que superen los topes ordinarios o que carezcan de límite de usos, y que cupons-frontend relea siempre el estado guardado en el servidor tras cada guardado.
  - *detectivo* (ecommerce): Registrar en una bitácora inmutable la petición recibida en F28 y los valores persistidos; alertar por rechazos repetidos de validación de topes (indicio de manipulación) y por cupones activos con valores que difieren de lo mostrado en la interfaz o de las campañas aprobadas.
  - *correctivo* (ecommerce): Desactivar el cupón fuera de política, revisar y revertir los canjes asociados, reasignar el costo a la campaña correcta y abrir una investigación disciplinaria con la evidencia de la bitácora.
- **Referencias y patrones:** CAPEC-39, OWASP API5:2023 Broken Function Level Authorization, OWASP API6:2023 Unrestricted Access to Sensitive Business Flows, FE-05, AV-0029

### UC-16 Administración interna de órdenes de entrega

<a id="av-0079"></a>
#### AV-0079 · Operador redirige una orden ya pagada a una dirección controlada por un cómplice mediante el cambio de dirección de excepción

- **ID de origen:** AC-UC16-01 · **Ejecución:** Lote 3 · **Tema de riesgo:** R3
- **STRIDE:** T (E, R) — Manipulación
- **Actor:** Operador de entregas con cuenta nominal en delivery-admin-front y permiso de edición de direcciones (interno)
- **Elementos del DFD:** delivery-admin-front, delivery-api, F29, F13 · **Límites:** LC-3, LC-4
- **Precondiciones:**
  - El operador puede editar la dirección de órdenes pagadas que aún no entregó el proveedor logístico
  - El cambio de dirección no exige motivo, ticket ni aprobación de una segunda persona
  - delivery-api reenvía al proveedor logístico la dirección modificada sin avisar al cliente
  - Hay un cómplice que recibe el paquete
- **Cómo ocurre:**
  1. El operador consulta en delivery-admin-front órdenes recientes de producto de alto valor en estado preparado o en tránsito
  2. Elige una orden y abre la gestión de excepciones, alegando una dirección incorrecta
  3. Reemplaza la dirección de entrega y el contacto por los de un punto controlado por el cómplice
  4. delivery-api guarda el cambio sobre la orden de entrega y lo comunica al proveedor logístico
  5. El repartidor entrega en la nueva dirección y el cómplice recibe el paquete
  6. El cliente reclama la no recepción y el cambio figura como una excepción operativa legítima, sin motivo ni evidencia asociada
- **Vector práctico:** Edición desde la interfaz de delivery-admin-front del campo de dirección y contacto de órdenes pagadas y no entregadas, aprovechando que delivery-api acepta el cambio sin motivo, aprobación ni notificación al cliente y lo propaga al proveedor.
- **Impacto:** Pérdida de producto de alto valor, reclamos y contracargos del cliente, y dificultad para atribuir el cambio si la bitácora no registra motivo ni aprobador.
- **Riesgo:** alto (2×3). Un operador interno con cambio de dirección sin aprobación ni aviso al cliente puede desviar producto de alto valor con poco esfuerzo, y la pérdida es directa y difícil de atribuir.
- **Controles:**
  - *preventivo* (ecommerce): En delivery-api, exigir motivo codificado, ticket de soporte vinculado y aprobación de una segunda persona (cuatro ojos) para cambiar dirección o contacto en órdenes pagadas y no entregadas, con umbral más estricto para productos de alto valor.
  - *preventivo* (ecommerce): Notificar al cliente por su correo o teléfono registrado cada cambio de dirección hecho desde el backoffice y retener la propagación al proveedor un tiempo breve (o hasta que el cliente confirme) en órdenes de alto valor.
  - *detectivo* (ecommerce): Alertar por cambios de dirección a destinos nuevos o repetidos entre órdenes de distintos clientes, por operadores con muchas excepciones de dirección y por cambios sobre órdenes de alto valor; conciliar semanalmente los cambios contra reclamos de no recepción.
  - *correctivo* (proveedor logístico): Ante una sospecha, solicitar al proveedor la retención o interceptación del paquete en tránsito, revertir la dirección original en delivery-api y preservar la bitácora inmutable (operador, motivo, aprobador) para la investigación.
- **Referencias y patrones:** CAPEC-384, OWASP API5:2023, FE-11, AV-0046

<a id="av-0080"></a>
#### AV-0080 · Operador cambia la tienda o la dirección de una orden para reducir o anular el costo de envío de un conocido

- **ID de origen:** AC-UC16-02 · **Ejecución:** Lote 3 · **Tema de riesgo:** R3
- **STRIDE:** T (E) — Manipulación
- **Actor:** Operador de entregas con permiso de cambiar tienda o dirección de órdenes (interno)
- **Elementos del DFD:** delivery-admin-front, delivery-api, F29, F13 · **Límites:** LC-3
- **Precondiciones:**
  - El costo de envío de la orden se recalcula o se conserva según la tienda o la dirección que figuren en la orden (RN-2)
  - El operador puede modificar tienda o dirección sin aprobación
  - No hay conciliación entre el costo cobrado al cliente y el costo calculado tras la excepción
- **Cómo ocurre:**
  1. Un conocido del operador paga una orden voluminosa con un costo de envío alto
  2. El operador abre la orden en delivery-admin-front y la gestiona como excepción
  3. Cambia la tienda de origen a una cercana al destino, o ajusta la dirección o zona registrada, de modo que el costo calculado sea menor
  4. delivery-api registra el cambio y la orden se despacha con el costo de envío reducido
  5. Si la orden ya estaba cobrada, la diferencia queda como una devolución o ajuste a favor del conocido, o la orden sale con el costo de envío bajo
  6. El operador repite el patrón con otras órdenes sin que queden vinculadas a un caso de soporte
- **Vector práctico:** Modificación desde delivery-admin-front de los campos tienda de origen y dirección o zona de entrega de una orden, para que delivery-api recalcule o acepte un costo de envío menor que el que correspondía al cliente.
- **Impacto:** Pérdida de ingresos por envíos subcobrados, distorsión de los costos logísticos por tienda y favoritismo no detectado entre clientes.
- **Riesgo:** medio (2×2). El favoritismo en costos de envío es plausible para un operador con permiso de edición, pero la pérdida por orden es acotada aunque se acumule con el tiempo.
- **Controles:**
  - *preventivo* (ecommerce): Calcular el costo de envío solo en el servidor de delivery-api según RN-2 y bloquear su edición manual; todo ajuste de costo, o cambio de tienda o zona que lo modifique, requiere motivo, ticket y aprobación de un supervisor.
  - *preventivo* (pasarela de pago): Limitar los reembolsos o ajustes a favor del cliente a una orden de reembolso aprobada, referenciada al pago original y con importe máximo igual a la diferencia calculada.
  - *detectivo* (ecommerce): Conciliación diaria entre el costo de envío cobrado y el recalculado tras cada excepción, con alerta por diferencias y por operadores que repiten cambios de tienda o zona que reducen el costo, sobre todo si benefician a los mismos clientes.
  - *correctivo* (ecommerce): Revertir los cambios de tienda o zona sospechosos, recuperar la diferencia con el cliente beneficiado y retirar el permiso de edición al operador mientras dure la revisión.
- **Referencias y patrones:** OWASP API5:2023, AV-0031, AV-0046

<a id="av-0081"></a>
#### AV-0081 · Operador de entregas recolecta direcciones, teléfonos y horarios de entrega de órdenes de alto valor para venderlos o planear robos

- **ID de origen:** AC-UC16-03 · **Ejecución:** Lote 3 · **Tema de riesgo:** R7
- **STRIDE:** I (R) — Divulgación de información
- **Actor:** Operador de entregas con acceso de consulta amplio a órdenes y direcciones (interno)
- **Elementos del DFD:** delivery-admin-front, delivery-api, F29, F13 · **Límites:** LC-3
- **Precondiciones:**
  - El operador puede consultar cualquier orden de entrega sin un caso o ticket abierto
  - Las direcciones y teléfonos se muestran sin enmascarar
  - No hay límites de volumen de consulta ni alertas por consultas atípicas
- **Cómo ocurre:**
  1. El operador filtra en delivery-admin-front las órdenes por estado, por ejemplo en reparto o programadas
  2. Ordena u observa las órdenes de mayor valor y registra dirección, nombre, teléfono y ventana de entrega
  3. Repite las consultas durante varios días, copiando los datos mediante capturas de pantalla o copia manual a un medio personal
  4. Entrega el listado a un tercero o lo usa para interceptar entregas o suplantar al repartidor
  5. Las consultas se confunden con la actividad operativa normal y no se vinculan a ningún caso
- **Vector práctico:** Consultas repetidas y filtradas en el listado de órdenes de delivery-admin-front, con captura de pantalla o copia manual de los campos dirección, contacto, valor y ventana de entrega.
- **Impacto:** Fuga de datos personales de clientes, robos dirigidos en el momento de la entrega, daño reputacional y posible incumplimiento de normas de protección de datos.
- **Riesgo:** alto (3×3). El operador ya tiene acceso legítimo amplio y sin límites ni enmascaramiento, lo que hace la recolección fácil, y la exposición de direcciones y horarios facilita robos físicos y sanciones de protección de datos.
- **Controles:**
  - *preventivo* (ecommerce): Condicionar la consulta del detalle de una orden a un caso o ticket abierto y asignado al operador, y limitar el listado al alcance de su región o tienda.
  - *preventivo* (ecommerce): Enmascarar por defecto teléfono, dirección completa y nombre en delivery-admin-front, con revelado puntual y registrado por orden, y aplicar límites de consultas y de revelados por operador y por hora.
  - *preventivo* (ecommerce): Mostrar marca de agua con el usuario en pantalla y bloquear exportaciones y copia masiva desde el listado de órdenes.
  - *detectivo* (ecommerce): Alertar por consultas sin ticket asociado, volumen inusual de revelados, filtros sistemáticos por valor alto o estado en reparto, y acceso a órdenes de alto valor sin excepción abierta; revisar mensualmente los accesos por operador.
  - *correctivo* (ecommerce): Ante un uso indebido, suspender el acceso del operador, evaluar y notificar a los clientes y a la autoridad de protección de datos si corresponde, y reprogramar o reforzar la entrega de las órdenes expuestas.
- **Referencias y patrones:** OWASP API3:2023, FE-16

<a id="av-0082"></a>
#### AV-0082 · Operador marca como fallido o reprograma una orden ya entregada para provocar un segundo envío a un cómplice

- **ID de origen:** AC-UC16-04 · **Ejecución:** Lote 3 · **Tema de riesgo:** R3
- **STRIDE:** T (E, R) — Manipulación
- **Actor:** Operador de entregas con permiso de cambiar estado manualmente y reprogramar (interno)
- **Elementos del DFD:** delivery-admin-front, delivery-api, F29, F13 · **Límites:** LC-3, LC-4
- **Precondiciones:**
  - delivery-api permite al operador retroceder un estado final (entregado) hacia fallido o reprogramado
  - La transición retrógrada no exige evidencia ni segunda aprobación
  - El cambio manual se comunica al proveedor logístico como instrucción de reenvío o reprogramación
  - El cliente ya recibió el producto o la orden está en poder del cómplice
- **Cómo ocurre:**
  1. El operador identifica órdenes que el proveedor reportó como entregadas hace poco
  2. En delivery-admin-front cambia el estado manualmente a fallido o reprograma la entrega, alegando que el cliente estuvo ausente
  3. delivery-api registra el cambio y lo comunica al proveedor, o genera una nueva orden de despacho
  4. Durante la reprogramación el operador cambia además la dirección hacia el punto del cómplice
  5. Se despacha un segundo envío del mismo producto a una dirección controlada
  6. El cambio contradice los eventos de logistic, pero no hay una alerta que lo señale
- **Vector práctico:** Cambio manual desde delivery-admin-front del campo estado de órdenes en estado final hacia fallido o reprogramado, combinado con la edición de la dirección, sin que delivery-api valide la transición ni contraste con los eventos de logistic.
- **Impacto:** Pérdida de inventario por doble envío, inconsistencias entre el estado interno y el del proveedor, costos logísticos adicionales y disputas con el proveedor.
- **Riesgo:** alto (2×3). Sin validación de transiciones, retroceder un estado final es sencillo y produce un segundo envío con pérdida de inventario, aunque exige un cómplice y la contradicción con la logística es detectable.
- **Controles:**
  - *preventivo* (ecommerce): Implementar en delivery-api una máquina de estados que prohíba el retroceso desde entregado, o lo permita solo con evidencia adjunta y aprobación de un supervisor, y que bloquee reprogramar con cambio de dirección en la misma operación.
  - *preventivo* (proveedor logístico): No generar un reenvío ni una nueva orden de despacho si el proveedor tiene registrada prueba de entrega (escaneo o firma) sin una confirmación de la excepción en su sistema.
  - *detectivo* (ecommerce): Alertar cuando un cambio manual de estado contradiga los eventos recibidos del proveedor, y conciliar a diario las órdenes entregadas que pasan a fallido o reprogramado, agrupadas por operador.
  - *correctivo* (proveedor logístico): Cancelar el segundo despacho antes de su salida, recuperar el paquete si ya salió, restaurar el estado entregado y registrar la incidencia en la bitácora para la investigación y la disputa con el proveedor.
- **Referencias y patrones:** CAPEC-384, FE-15, AV-0048, AV-0061

<a id="av-0083"></a>
#### AV-0083 · Atacante externo toma la sesión o credenciales de un operador de entregas y gestiona órdenes desde delivery-admin-front

- **ID de origen:** AC-UC16-05 · **Ejecución:** Lote 3 · **Tema de riesgo:** R5
- **STRIDE:** S (T, I, E) — Suplantación
- **Actor:** Atacante con credenciales filtradas o robadas por phishing de un operador de entregas (externo)
- **Elementos del DFD:** delivery-admin-front, delivery-api, F29 · **Límites:** LC-3
- **Precondiciones:**
  - delivery-admin-front es accesible desde fuera de la red corporativa o desde una VPN con credenciales débiles
  - La autenticación se basa solo en usuario y contraseña, sin MFA ni restricción de dispositivo
  - El operador reutiliza contraseñas o es víctima de phishing o de malware que roba sesiones
- **Cómo ocurre:**
  1. El atacante obtiene la contraseña o la cookie de sesión del operador mediante una página de phishing que imita el acceso al panel o con malware de robo de credenciales
  2. Inicia sesión en delivery-admin-front desde un dispositivo y ubicación nuevos
  3. Consulta órdenes de alto valor y sus datos de entrega
  4. Cambia direcciones o estados de órdenes seleccionadas hacia un punto controlado
  5. delivery-api registra los cambios con la identidad del operador legítimo y los comunica al proveedor
  6. El operador legítimo queda como responsable aparente ante una investigación
- **Vector práctico:** Reutilización de credenciales o de una sesión robada del operador mediante un navegador propio, para ejecutar desde delivery-admin-front consultas y cambios de dirección o estado con la identidad de otra persona.
- **Impacto:** Desvío de órdenes, fuga de datos personales, atribución errónea al empleado legítimo y pérdida de confianza en la bitácora de cambios.
- **Riesgo:** alto (2×3). El phishing y la reutilización de contraseñas son frecuentes y sin MFA basta una credencial, con acceso a datos y cambios de órdenes atribuidos a otra persona.
- **Controles:**
  - *preventivo* (ecommerce): Exigir MFA resistente a phishing (FIDO2/WebAuthn) en delivery-admin-front, restringir el acceso a la VPN corporativa o a IPs permitidas y ligar la sesión al dispositivo con caducidad corta.
  - *preventivo* (ecommerce): Pedir reautenticación o segundo factor para acciones sensibles (cambio de dirección, de estado final o consulta masiva) y rechazar contraseñas filtradas.
  - *detectivo* (ecommerce): Alertar por inicios de sesión desde dispositivo, país o IP nuevos, sesiones simultáneas y viaje imposible, sobre todo si van seguidos de cambios de dirección o estado o de consultas de órdenes de alto valor.
  - *correctivo* (ecommerce): Revocar todas las sesiones y tokens de la cuenta, forzar el cambio de credenciales y de factor, y revisar y revertir los cambios hechos en la ventana de compromiso, avisando al proveedor para frenar los envíos afectados.
- **Referencias y patrones:** CAPEC-384, OWASP API2:2023, FE-11, FE-15

<a id="av-0084"></a>
#### AV-0084 · Operador de solo consulta o de otra región modifica órdenes fuera de su alcance manipulando las peticiones entre delivery-admin-front y delivery-api

- **ID de origen:** AC-UC16-06 · **Ejecución:** Lote 3 · **Tema de riesgo:** R3
- **STRIDE:** E (T) — Elevación de privilegios
- **Actor:** Operador con rol de consulta o con alcance limitado a una región o tienda (interno)
- **Elementos del DFD:** delivery-admin-front, delivery-api, F29 · **Límites:** LC-3
- **Precondiciones:**
  - delivery-admin-front oculta las acciones de edición según el rol, pero delivery-api no valida la autorización por función ni por alcance
  - El operador puede interceptar y modificar las peticiones de su propio navegador
  - Los identificadores de órdenes son predecibles o enumerables
- **Cómo ocurre:**
  1. El operador inicia sesión con su cuenta nominal y observa con un proxy de inspección de tráfico las peticiones que el panel envía a delivery-api
  2. Identifica la petición que usan los operadores con permiso de edición para cambiar estado o dirección
  3. Reenvía esa petición con el identificador de una orden de otra región o tienda, o la acción de edición que su rol no tiene
  4. delivery-api la acepta porque valida solo la identidad y no la autorización por función ni por objeto
  5. La orden se modifica y el cambio se comunica al proveedor
  6. El cambio queda registrado como una acción normal de su cuenta, sin señal de que excedió su rol
- **Vector práctico:** Uso de un proxy de inspección de tráfico para reenviar peticiones de F29 con el identificador de orden o el tipo de acción alterados, aprovechando la falta de autorización por función y por objeto en delivery-api.
- **Impacto:** Modificación de órdenes fuera del alcance asignado, pérdida de segregación de funciones y posibilidad de fraude o sabotaje por usuarios sin permiso de edición.
- **Riesgo:** alto (2×3). Reenviar una petición con otro identificador con un proxy es trivial para un empleado y, si delivery-api solo valida identidad, puede modificar órdenes ajenas y saltarse la segregación de funciones.
- **Controles:**
  - *preventivo* (ecommerce): Aplicar en delivery-api autorización por función (rol y permiso por acción) y por objeto (región o tienda de la orden) en cada endpoint de F29, validada en servidor y no solo ocultando acciones en delivery-admin-front.
  - *preventivo* (ecommerce): Usar identificadores de orden no predecibles (UUID), con comprobación de pertenencia al alcance del operador, y pruebas automatizadas de autorización en el pipeline que cubran roles de consulta y regiones cruzadas.
  - *detectivo* (ecommerce): Registrar y alertar los rechazos 403/404 repetidos, accesos a órdenes fuera de alcance y acciones no permitidas al rol, con revisión periódica de roles y permisos asignados.
  - *correctivo* (ecommerce): Revertir las modificaciones fuera de alcance, suspender el rol o la cuenta del operador, informar al proveedor de las órdenes alteradas y corregir el endpoint vulnerable con una prueba de regresión.
- **Referencias y patrones:** OWASP API5:2023, OWASP API1:2023, CAPEC-384, AV-0048, AV-0046

## Anexo B · Supuestos derivados declarados por los agentes

Condiciones que cada caso de abuso da por ciertas. Las referencias a supuestos del modelo (S-xx) se omiten aquí porque ya están documentadas.

### UC-01 Registro y gestión de la cuenta del cliente

| Caso | Supuesto |
|---|---|
| AV-0011 | No hay límite por dirección de entrega ni por medio de pago asociado a la cuenta |
| AV-0011 | Se asume que S-08 no exige verificación de un teléfono físico real |
| AV-0012 | No se confirma si existe autenticación multifactor en el inicio de sesión del Marketplace |
| AV-0013 | Se asume que el mensaje de error de duplicado no está unificado con una respuesta genérica |
| AV-0014 | Se asume que nivel y membresía son atributos del mismo objeto que el cliente edita, o que el filtrado de campos no está implementado en clients-api |
| AV-0015 | Se asume que los identificadores no son aleatorios de alta entropía ni están ligados a la sesión |
| AV-0016 | Se asume que la política de intentos máximos y de expiración del código de un solo uso (S-08) no está definida o no se aplica de forma estricta en el endpoint de verificación |
| AV-0016 | Se asume que el registro permite verificar correo y teléfono por separado, con un correo bajo control del atacante |

### UC-02 Selección del producto y carrito

| Caso | Supuesto |
|---|---|
| AV-0017 | Se asume que el Marketplace podría confiar en valores enviados por el cliente al calcular el subtotal; debe validarse contra el diseño real |
| AV-0017 | S-01, S-02 y S-26 no excluyen explícitamente este escenario |
| AV-0018 | Se asume que el Marketplace descuenta o reserva stock al agregar al carrito; si solo lo hace al pagar, este caso no aplica |
| AV-0018 | S-26 no define límites de reserva por carrito |
| AV-0019 | Se asume que la disponibilidad exacta por variante y tienda se expone al cliente; debe confirmarse con el diseño real del Marketplace |
| AV-0019 | Nuevo supuesto: el Marketplace no aplica límite de tasa ni detección de automatización a las operaciones de carrito de una cuenta autenticada; debe confirmarse |
| AV-0019 | Nuevo supuesto: el sondeo se hace con cuentas de cliente registradas y no de forma anónima, porque el carrito exige sesión; la creación de cuentas desechables puede ser sencilla (ver FE-03) |

### UC-03 Captura de datos de envío y contacto

| Caso | Supuesto |
|---|---|
| AV-0020 | S-10: delivery-api confía en la zona enviada por el Marketplace |
| AV-0020 | No hay firma ni recálculo del lado servidor a partir de la dirección guardada |
| AV-0021 | S-09: la autorización por objeto en clients-api no está confirmada |
| AV-0021 | Los identificadores de dirección son secuenciales o predecibles |
| AV-0022 | La orden de entrega referencia la dirección y no guarda un registro inmutable de lo confirmado por el cliente |
| AV-0023 | Supuesto propio de este caso: no hay segundo factor ni notificación al titular por nuevas direcciones o contactos. No se apoya en un supuesto numerado, porque UC-03 solo declara S-09 y S-10. |
| AV-0023 | La orden pagada se despacha sin una verificación adicional de que la dirección es nueva para esa cuenta |
| AV-0024 | Los paneles internos (soporte, preparación de pedidos) no figuran entre los componentes de UC-03. Se asumen como consumidores de los datos de la orden que delivery-api conserva, y por eso este caso no declara LC-4. |
| AV-0024 | La app del repartidor queda fuera de este caso; solo se consideran los paneles internos que reciben la orden. |
| AV-0024 | Los campos de texto libre de dirección y contacto no se sanean ni se codifican en las vistas internas |

### UC-04 Aplicación de cupón de descuento

| Caso | Supuesto |
|---|---|
| AV-0025 | S-11: las reglas incluyen usos por cliente y segmento, pero se asume que no todos los cupones están ligados a una cuenta. |
| AV-0025 | No se conoce si cupons-api aplica límite de intentos o protección contra automatización. |
| AV-0026 | S-26: se asume que el consumo del cupón ocurre al confirmar el pago y no hay bloqueo previo. |
| AV-0026 | No se sabe si cupons-api tiene restricción única sobre el par cupón-cliente. |
| AV-0027 | S-11: el límite de usos por cliente depende de RN-1, por lo que evadir la unicidad del cliente evade el límite. |
| AV-0027 | Se asume que no hay huella de dispositivo ni límites por dirección o medio de pago. |
| AV-0028 | No se confirma si el Marketplace recalcula el total en servidor entre la validación del cupón y el pago. |
| AV-0028 | S-12: se asume que la modalidad y el costo de envío pueden cambiar durante el checkout. |
| AV-0029 | Nuevo: el abuso se origina en UC-15 (cupons-frontend, LC-3), que UC-04 no incluye entre sus componentes ni límites. Se vincula a UC-04 porque se materializa en su checkout con cupons-api (F4, F12, LC-2). Se declara así para trazabilidad y no porque UC-04 los liste. |
| AV-0029 | Nuevo: se asume que no existe aprobación de una segunda persona para cupones de alto descuento o sin límite de usos. |
| AV-0029 | Nuevo: se asume que no existen topes de descuento por rol, alertas por uso concentrado ni bitácora inmutable de cambios en cupones. No se confirma ninguno de estos controles en el contexto entregado. |
| AV-0029 | S-11 se usa solo en lo que describe: los empleados crean los cupones en cupons-frontend y cupons-api los valida. |

### UC-05 Cálculo del costo de envío según el perfil

| Caso | Supuesto |
|---|---|
| AV-0030 | S-03: delivery-api confía en los datos de clients-api |
| AV-0030 | Se asume que el perfil es editable por el cliente mediante una API del Marketplace; debe confirmarse qué campos acepta realmente |
| AV-0031 | Los operadores de atención pueden editar atributos de beneficio en clients-api |
| AV-0031 | No se confirmó que exista doble aprobación para esos cambios |
| AV-0032 | S-10: la tarifa viaja por el Marketplace entre cotización y confirmación; debe confirmarse si el servidor la recalcula |
| AV-0033 | No se conoce si delivery-api obtiene peso y volumen del catálogo o los recibe del cliente |
| AV-0034 | No se confirmó cómo cupons-api valida usos concurrentes ni la vinculación del cupón al perfil |
| AV-0035 | El backoffice de cupones no exige doble aprobación según la información disponible |

### UC-06 Elección de la modalidad de entrega

| Caso | Supuesto |
|---|---|
| AV-0036 | S-10: el costo de cada opción lo calcula delivery-api, pero el Marketplace puede reenviarlo desde el cliente |
| AV-0037 | S-10: el costo se calcula en la cotización y no se vuelve a validar al confirmar |
| AV-0037 | S-18: la tienda de recolección se asigna a la orden sin validar de nuevo disponibilidad ni cobertura |
| AV-0038 | S-10: la ventana de entrega o la capacidad de tienda se reserva al seleccionar, antes del pago |
| AV-0039 | S-18: la tienda se asigna a la orden con el identificador que envía el cliente |
| AV-0039 | SN-01 (nuevo): delivery-api calcula una ventana de entrega distinta por tienda y limita las tiendas ofrecidas según zona u orden; este dato no está declarado en UC-06 y debe confirmarse |
| AV-0039 | Se atiende un solo objetivo, la ventana más corta; la selección de tiendas cerradas, sin stock o sin capacidad queda fuera de este caso porque esos datos no están en UC-06 |

### UC-07 Pago y registro de la orden

| Caso | Supuesto |
|---|---|
| AV-0040 | No se conoce el mecanismo exacto de autenticación de la notificación de la pasarela; se asume que no está documentado ni verificado en el Marketplace |
| AV-0041 | El monto puede viajar o alterarse en el cliente según la integración con la pasarela; si el monto se fija solo en servidor, este caso se limita a la falta de validación en la confirmación |
| AV-0042 | Se asume que el retorno por redirección es una de las vías con las que el Marketplace registra la orden, según S-05 |
| AV-0043 | No se sabe si el Marketplace bloquea el carrito al iniciar el pago; se asume que no lo hace |
| AV-0044 | Se asume que la pasarela soporta contracargos y que no se aplica autenticación reforzada del titular en todos los pagos |
| AV-0045 | Se asume que existe una pantalla o endpoint de consulta de la orden posterior al pago, aunque no esté descrito en el flujo de UC-07 |
| AV-0046 | Se asume que existen herramientas internas de edición de órdenes, aunque no aparezcan en el diagrama original |
| AV-0046 | Se asume que no hay doble aprobación para cambiar el estado de pago |

### UC-08 Preparación y empaquetado en almacén

| Caso | Supuesto |
|---|---|
| AV-0048 | SN-UC08-01: delivery-api no diferencia por rol del almacén qué transiciones de estado se pueden ejecutar sobre una orden |
| AV-0049 | SN-UC08-01: delivery-api no valida el peso y las dimensiones registrados por el almacén contra el peso teórico del producto ni exige foto del paquete como evidencia de empaquetado |
| AV-0049 | SN-UC08-02: el traspaso de custodia almacén → proveedor logístico no requiere escaneo conjunto ni verificación de peso por ambas partes |

### UC-09 Recolección y transporte por el proveedor logístico

| Caso | Supuesto |
|---|---|
| AV-0050 | Se asume que el escaneo lo registra un solo operario sin contrafirma ni verificación de peso en cada punto |
| AV-0051 | Se asume que el escaneo del proveedor y el del almacén son sistemas separados sin conciliación automática (S-14, S-27) |
| AV-0052 | Se asume que el almacén no recibe del proveedor la identidad esperada del recolector antes de cada visita (S-27) |
| AV-0053 | Se asume que la etiqueta incluye datos personales completos, sin identificadores opacos (S-06, S-15) |
| AV-0054 | Se asume que logistic no valida las excepciones contra evidencia ni limita cuántas puede registrar un operario |
| AV-0055 | El empleado tiene el permiso de reasignación como parte de su función; el caso es abuso de un permiso legítimo para alterar un dato (T) y negar la acción (R), no una elevación de privilegios |
| AV-0055 | Se asume que logistic no exige aprobación de un segundo rol ni registra el motivo del cambio |
| AV-0055 | Se asume que el historial de logistic no es revisado ni conciliado por el ecommerce contra los reclamos de entrega |

### UC-10 Actualización de estados por la integración logística

| Caso | Supuesto |
|---|---|
| AV-0056 | El mecanismo exacto de autenticación de la integración no se conoce; se asume que es una credencial compartida sin firma por evento. |
| AV-0057 | Se asume que la credencial no tiene restricciones por endpoint ni por origen; el alcance real debe confirmarse. |
| AV-0058 | Se asume que delivery-api no conserva el mensaje original de cada evento ni su metadato de origen. |
| AV-0059 | Se asume que ni delivery-api ni el Marketplace validan ni codifican los campos de texto libre del evento; debe confirmarse. |
| AV-0060 | Se asume que el proveedor permite a algunos empleados generar o editar eventos fuera del flujo de escaneo. |
| AV-0061 | Se asume que la credencial compartida y los registros de eventos se obtuvieron en una misma filtración, por ejemplo por exposición de registros del lado del proveedor. |
| AV-0061 | Se asume que el mecanismo de la integración no garantiza unicidad ni orden de eventos. |

### UC-11 Registro de entrega a domicilio con geolocalización

| Caso | Supuesto |
|---|---|
| AV-0001 | S-17: la ubicación es un dato generado del lado del cliente y falsificable |
| AV-0001 | No hay detección de ubicación simulada ni atestación del dispositivo en la app |
| AV-0002 | El reembolso no está condicionado a recibir el producto de vuelta en almacén |
| AV-0002 | No se analizan relaciones repetidas repartidor-cliente |
| AV-0003 | No hay certificate pinning, firma del payload ni atestación del dispositivo en F18 |
| AV-0003 | El código de confirmación es una de las evidencias alternativas y delivery-api no lo exige ni lo verifica cuando se envía foto o firma |
| AV-0003 | LC-4 se asume como el límite en el que delivery-api recibe el registro reenviado por logistic |
| AV-0003 | RN-3 solo compara las coordenadas recibidas con la dirección dentro del radio de tolerancia y no valida su origen |
| AV-0003 | El repartidor no tiene acceso directo a delivery-api, solo a través de la app y logistic |
| AV-0004 | El código de confirmación es opcional y puede sustituirse por firma o foto (paso 2 del flujo) |
| AV-0004 | La política de soporte no admite la geolocalización validada con RN-3 como prueba de que el cliente recibió el producto, solo de que el repartidor estuvo en la dirección |
| AV-0004 | El agente de soporte consulta el estado y la evidencia en delivery-api, pero la firma o foto registrada no permite identificar al receptor |
| AV-0004 | El repartidor no es cómplice. Si lo fuera, el caso pasaría al patrón de colusión FE-08 |

### UC-12 Recolección en tienda

| Caso | Supuesto |
|---|---|
| AV-0005 | El código de retiro es estático y se envía por la notificación |
| AV-0005 | No existe verificación de identificación registrada ni doble verificación en productos de alto valor |
| AV-0006 | delivery-api permite el cambio de estado a entregada sin exigir el escaneo del código de retiro |
| AV-0006 | Los eventos de cambio de estado no registran de forma inmutable el empleado ni el método de validación |
| AV-0007 | El endpoint de consulta no valida que la orden pertenezca al punto de recolección del solicitante |
| AV-0007 | Los identificadores de orden son predecibles |
| AV-0008 | No hay un plazo de retiro ni un límite de órdenes de recolección pendientes por cliente o por tienda |
| AV-0009 | La autorización de terceros se puede modificar sin segundo factor ni confirmación fuera de banda al titular |
| AV-0009 | La categoría principal es S porque la acción (registrar un autorizado) está dentro de los permisos de la cuenta; se vulnera la autenticidad del titular y del autorizado. E queda como secundaria solo porque el cómplice obtiene un privilegio de retiro que el atacante no tenía legítimamente |
| AV-0010 | El Punto de recolección no captura firma, foto ni copia de la identificación al entregar |
| AV-0010 | Aporte frente a AV-0004: en la entrega a domicilio la app del repartidor al menos adjunta GPS y marca de tiempo; en la recolección en tienda no hay ni geolocalización ni foto, así que el repudio se apoya en la ausencia total de evidencia y no en una prueba parcial |
| AV-0010 | Frente a AV-0002 no hay colusión: el cliente actúa solo y el personal de tienda es honesto |

### UC-13 Cancelación posterior a la recepción y devolución

| Caso | Supuesto |
|---|---|
| AV-0062 | S-19: no se sabe si el reembolso se emite antes de la inspección; se evalúan ambos escenarios |
| AV-0062 | No se asume que se registre número de serie al despachar |
| AV-0063 | No se conoce el formato de los identificadores de orden ni los controles de autorización por objeto en delivery-api |
| AV-0064 | S-19: se evalúa el escenario en que el reembolso depende de la confirmación del proveedor |
| AV-0064 | S-20: se asume que la integración logistic–delivery-api confía en el estado informado por el proveedor |
| AV-0065 | AV-0002 se extiende a UC-13: allí el actor que registra el estado es el repartidor en la entrega; aquí es el inspector de almacén y el estado registrado es el resultado de inspección que libera el reembolso |
| AV-0065 | Lo que aporta frente a AV-0002 es la inspección sin segundo control, el reembolso ligado al resultado 'conforme' y la posible sustracción del producto original dentro del almacén |
| AV-0065 | S-19: se evalúa el escenario en que el reembolso se emite tras la inspección y depende solo del resultado registrado |
| AV-0065 | No se conoce si hay doble control o fotos obligatorias en almacén |
| AV-0066 | SN-03 (nuevo): no se conoce si el reembolso es idempotente ni si hay bloqueo de estado sobre la orden; se asume que no, sin atribuirlo a RN-4 |
| AV-0066 | SN-04 (nuevo): no se conoce si la pasarela exige clave única por operación de reembolso; se asume que el Marketplace no la envía |
| AV-0066 | No se cita S-26 porque su contenido no se entregó en el contexto |
| AV-0067 | S-12: la política real de restitución no está definida; se evalúan los escenarios de restitución al solicitar la cancelación y de restitución al emitir el reembolso |
| AV-0067 | SN-01 (nuevo): existe un servicio de cupones (cupons-api) fuera del DFD de UC-13 con el que el Marketplace consume y restituye cupones, según UC-04 |
| AV-0067 | SN-02 (nuevo): la restitución no verifica el estado final de la devolución ni limita las restituciones por cliente |
| AV-0067 | No se cita el contenido de S-26 porque no se entregó en el contexto |

### UC-14 Administración interna de clientes y perfiles

| Caso | Supuesto |
|---|---|
| AV-0068 | No se asume que exista hoy enmascaramiento, límite de consultas ni revisión periódica de accesos en clients-admin-front |
| AV-0069 | S-07 y S-09: se asume que las ediciones internas del perfil no pasan por la verificación de contacto del alta (UC-01) |
| AV-0070 | S-21: se asume que no está garantizado que existan cuentas nominales ni un registro de auditoría inmutable |
| AV-0071 | Se asume que los permisos por rol se aplican solo en clients-admin-front y no campo a campo en clients-api |
| AV-0072 | RN-1 se verifica en el alta (UC-01) y se asume que no se aplica igual en las ediciones internas |
| AV-0073 | Supuesto nuevo: clients-admin-front está expuesto a internet o a redes alcanzables por el atacante, sin restricción de red corporativa ni VPN; no se vincula a S-21 |
| AV-0073 | Supuesto nuevo: la autenticación del backoffice no tiene hoy segundo factor ni control de origen o dispositivo; no se vincula a S-21, que aquí no se usa para respaldar esta ausencia |

### UC-15 Administración interna de cupones

| Caso | Supuesto |
|---|---|
| AV-0074 | Se asume que el segundo factor no es resistente a suplantación (por ejemplo, códigos por SMS o notificaciones push aprobables por error) |
| AV-0075 | Se asume que existen cuentas de terceros en cupons-frontend; si todo el personal es interno, el caso aplica a operadores con acceso excesivo |
| AV-0076 | Se asume que no existe bitácora inmutable y versionada de cambios de cupones |
| AV-0077 | Se asume que no hay respaldo versionado de las definiciones de cupón ni confirmación para cambios masivos |
| AV-0078 | Se asume que cupons-api no valida en el servidor la autorización por rol ni por campo sobre los datos recibidos en F28 |

### UC-16 Administración interna de órdenes de entrega

| Caso | Supuesto |
|---|---|
| AV-0079 | S-16: delivery-api comunica los cambios al proveedor como indica el flujo de UC-16 |
| AV-0079 | No hay notificación automática al cliente ante cambios de dirección hechos por el backoffice |
| AV-0080 | Se asume que cambiar tienda o dirección modifica el costo de envío vigente o permite ajustarlo, según RN-2 |
| AV-0081 | No existe enmascaramiento de campos ni acceso condicionado a un caso abierto en UC-16 |
| AV-0082 | S-16: el estado puede cambiarse por el panel interno además de la integración, y ambas vías se analizan |
| AV-0082 | Se asume que no hay validación de transiciones de estado en delivery-api para cambios manuales |
| AV-0083 | Se asume que no hay MFA ni controles contextuales de acceso en el panel, ya que el contexto no los menciona |
| AV-0084 | Se asume que los roles del panel se aplican solo en la interfaz, ya que el contexto no describe controles de autorización en delivery-api |
