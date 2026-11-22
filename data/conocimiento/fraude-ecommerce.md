# Patrones de fraude y abuso en ecommerce y logística

Documento curado para la memoria de largo plazo (segmento `ltm_amenazas`, fuente `fraude`).
Cada sección de nivel 2 es un fragmento. Redacción propia del proyecto, a partir de patrones conocidos en la industria; no describe incidentes reales de una empresa.

## FE-01 · Reclamo falso de "no recibido"

- **Actor:** cliente (externo).
- **STRIDE:** R, S.
- **Cómo ocurre:** el cliente recibe el producto y después reclama que no llegó o que lo recibió otra persona. Aprovecha que la evidencia de entrega es débil (sin código de confirmación, foto borrosa, firma en pantalla ilegible) y pide reembolso o reenvío.
- **Señales:** clientes con varios reclamos en poco tiempo; reclamos en direcciones donde la entrega tiene buena evidencia; cuentas nuevas con productos de alto valor.
- **Controles:** código de confirmación del cliente al entregar; foto con marca de tiempo y ubicación; historial de reclamos por cliente, dirección y medio de pago.

## FE-02 · Devolución de otro artículo o de una caja vacía

- **Actor:** cliente (externo); a veces con complicidad de quien recibe la devolución.
- **STRIDE:** T, R.
- **Cómo ocurre:** el cliente cancela después de recibir y devuelve un artículo distinto, dañado, más barato o una caja con peso similar. Si el reembolso se emite al registrar la recolección inversa y no después de inspeccionar, el fraude se completa antes de que alguien abra el paquete.
- **Señales:** diferencias de peso o de número de serie; devoluciones repetidas del mismo cliente; reembolso emitido antes de la inspección.
- **Controles:** reembolso solo tras inspección en almacén; registro de número de serie al despachar; fotos del producto en la recolección inversa.

## FE-03 · Cuentas múltiples para repetir beneficios

- **Actor:** cliente o grupo organizado (externo).
- **STRIDE:** S, E.
- **Cómo ocurre:** se crean muchas cuentas con correos desechables y números virtuales para usar varias veces un cupón de "primera compra" o un beneficio por cliente. Si la unicidad del cliente se valida solo por correo y teléfono, basta con variar esos dos datos.
- **Señales:** varias cuentas con la misma dirección de entrega, dispositivo, tarjeta o patrón de correo; cuentas creadas en ráfagas.
- **Controles:** huella de dispositivo; límites por dirección de entrega y medio de pago; verificación de teléfono real; protección contra automatización en el registro.

## FE-04 · Enumeración de códigos de cupón

- **Actor:** atacante externo con automatización.
- **STRIDE:** I, E.
- **Cómo ocurre:** si los códigos son cortos o predecibles (por ejemplo, prefijo de campaña y número consecutivo), un script prueba combinaciones en la validación del cupón hasta encontrar códigos válidos que no le fueron otorgados, y los usa o los vende.
- **Señales:** muchas validaciones fallidas desde la misma cuenta, IP o dispositivo; uso de cupones personales por cuentas distintas a la destinataria.
- **Controles:** códigos largos y aleatorios; cupones ligados a la cuenta destinataria; límite de intentos de validación; protección contra automatización.

## FE-05 · Cupón creado o modificado por un empleado para beneficio propio

- **Actor:** operador de marketing (interno).
- **STRIDE:** E, T, R.
- **Cómo ocurre:** el operador crea en el backoffice un cupón de alto descuento sin límite de usos, o amplía la vigencia de uno existente, y lo usa con cuentas de conocidos o lo vende. Si no hay aprobación de otra persona ni alertas, el abuso se detecta solo al revisar márgenes.
- **Señales:** cupones creados fuera de campañas aprobadas; descuentos fuera de rango; un cupón usado por pocas cuentas relacionadas entre sí.
- **Controles:** aprobación doble para descuentos altos o sin límite; topes por rol; bitácora inmutable; alertas por uso concentrado.

## FE-06 · Manipulación de atributos del perfil para pagar menos envío

- **Actor:** cliente (externo) o operador de atención (interno).
- **STRIDE:** T, E.
- **Cómo ocurre:** el costo de envío depende de atributos del perfil (por ejemplo, nivel de cliente, membresía o zona). El cliente los modifica en una petición que la API acepta sin validar, o un operador los cambia para un conocido. Las siguientes órdenes calculan un envío más barato o gratis.
- **Señales:** cambios de atributos justo antes de comprar; cambios hechos por el mismo operador para las mismas cuentas.
- **Controles:** atributos de beneficio solo editables por procesos del servidor; cambios manuales con justificación y aprobación; recalcular el envío al confirmar el pago.

## FE-07 · Entrega registrada sin haber entregado

- **Actor:** repartidor (interno de tercero).
- **STRIDE:** S, R, T.
- **Cómo ocurre:** el repartidor se queda con el producto y registra la entrega desde otro lugar, usando una app de ubicación simulada para cumplir la validación de distancia. Para el sistema, la orden fue entregada; el cliente reclama y el ecommerce paga reembolso o reenvío.
- **Señales:** trayectorias imposibles entre entregas; registros con precisión GPS idéntica; reclamos concentrados en un repartidor o una ruta.
- **Controles:** detección de ubicación simulada y atestación del dispositivo; código de confirmación del cliente; análisis de trayectoria de la ruta; responsabilidad contractual del proveedor.

## FE-08 · Colusión entre cliente y repartidor

- **Actor:** cliente (externo) y repartidor (interno de tercero).
- **STRIDE:** R, T.
- **Cómo ocurre:** el repartidor entrega el producto pero lo registra como "no entregado" o "rechazado"; el cliente pide la cancelación y el reembolso, y se reparten el valor del producto. O al revés: el repartidor marca entregado y el cliente reclama no recibido.
- **Señales:** pares repartidor–cliente que se repiten; rechazos frecuentes de productos de alto valor; cancelaciones justo después de un intento de entrega.
- **Controles:** evidencia del rechazo (foto, motivo, contacto con el cliente); reembolso solo con el producto de vuelta en almacén; análisis de relaciones entre cuentas y repartidores.

## FE-09 · Faltante en almacén encubierto con un registro falso

- **Actor:** personal de almacén (interno).
- **STRIDE:** T, R.
- **Cómo ocurre:** un empleado sustrae el producto y registra la orden como empaquetada y despachada. Si el traspaso al proveedor logístico no se confirma con un escaneo de ambas partes, el faltante aparece después como pérdida en tránsito y nadie puede probar dónde ocurrió.
- **Señales:** diferencias entre órdenes marcadas como despachadas y paquetes escaneados por el proveedor; faltantes concentrados en un turno.
- **Controles:** escaneo conjunto en el traspaso de custodia; peso y foto del paquete; conciliación diaria entre despachos y recepciones del proveedor.

## FE-10 · Retiro en tienda por quien no es el comprador

- **Actor:** atacante externo o personal de tienda (interno).
- **STRIDE:** S, E.
- **Cómo ocurre:** alguien obtiene el código de retiro (por ejemplo, tras tomar la cuenta del cliente o leer un mensaje reenviado) y se presenta con una identificación falsa o con una autorización de tercero inventada. También puede ocurrir que el personal de tienda marque como retirado un producto que se quedó.
- **Señales:** cambios en la cuenta poco antes del retiro; autorizaciones de terceros frecuentes; retiros marcados sin escaneo del código.
- **Controles:** código de un solo uso que solo se muestra en la app del titular; verificación de identificación registrada; autorización de terceros iniciada por el titular desde su cuenta; doble verificación en productos de alto valor.

## FE-11 · Toma de cuenta para desviar una orden

- **Actor:** atacante externo.
- **STRIDE:** S, T.
- **Cómo ocurre:** con credenciales filtradas de otro servicio (relleno de credenciales), el atacante entra a la cuenta del cliente, cambia la dirección o la modalidad de una orden pagada que aún no se despacha, o usa un medio de pago guardado para comprar y recoger en tienda.
- **Señales:** inicio de sesión desde dispositivo o país nuevo seguido de cambio de dirección; muchos intentos fallidos contra muchas cuentas.
- **Controles:** autenticación multifactor; notificación al cliente de cambios de dirección; bloquear cambios de dirección después del pago o pedir reautenticación.

## FE-12 · Compra con tarjeta robada y contracargo

- **Actor:** atacante externo.
- **STRIDE:** S, R.
- **Cómo ocurre:** el atacante paga con datos de una tarjeta robada y pide entrega en una dirección intermedia o retiro en tienda. Cuando el titular desconoce el cargo, el banco aplica un contracargo y el ecommerce pierde el producto y el dinero.
- **Señales:** dirección de entrega distinta a la de facturación; cuentas nuevas con productos fáciles de revender; varias tarjetas probadas en la misma cuenta.
- **Controles:** autenticación reforzada del pago (3-D Secure) cuando lo ofrece la pasarela; reglas de riesgo antes de despachar; retención de órdenes de alto riesgo.

## FE-13 · Manipulación del total o uso simultáneo de un cupón

- **Actor:** cliente (externo).
- **STRIDE:** T.
- **Cómo ocurre:** el cliente intercepta la petición del carrito o de la cotización y cambia precio, cantidad, costo de envío o modalidad. O envía varias peticiones de pago al mismo tiempo con un cupón de un solo uso, aprovechando que la marca de "usado" se escribe después de validar.
- **Señales:** órdenes con totales que no coinciden con el catálogo; un cupón de un solo uso aplicado a varias órdenes con segundos de diferencia.
- **Controles:** recalcular todos los montos en el servidor; reserva atómica del cupón (restricción única o bloqueo) antes de cobrar.

## FE-14 · Cancelación tardía para quedarse con producto y reembolso

- **Actor:** cliente (externo).
- **STRIDE:** T, R.
- **Cómo ocurre:** el cliente cancela cuando la orden ya va en ruta. Si la cancelación emite el reembolso de inmediato y la orden de recolección inversa no llega a tiempo al proveedor, el producto se entrega igual y el cliente se queda con ambos.
- **Señales:** cancelaciones con estado "en ruta"; entregas completadas después de una cancelación.
- **Controles:** máquina de estados que impide cancelar con reembolso inmediato después del despacho; reembolso condicionado a la recuperación del producto.

## FE-15 · Cambio manual de estado sin evidencia desde el backoffice

- **Actor:** operador de entregas (interno).
- **STRIDE:** E, T, R.
- **Cómo ocurre:** el operador usa el delivery-admin-front para marcar una orden como entregada, cancelada o devuelta sin evidencia, para cerrar excepciones rápido o para encubrir un robo. Si la acción no requiere justificación ni aprobación y el usuario es compartido, no queda rastro útil.
- **Señales:** muchas excepciones cerradas por el mismo operador; cambios fuera de horario; cambios que contradicen los eventos de la integración logística.
- **Controles:** motivo y evidencia obligatorios; aprobación de otra persona para estados finales; cuentas nominales; alertas por contradicción con eventos de logística.

## FE-16 · Abuso del acceso interno a datos de clientes

- **Actor:** operador de atención a clientes (interno).
- **STRIDE:** I.
- **Cómo ocurre:** el operador consulta clientes sin un caso abierto, exporta direcciones y teléfonos, o identifica quién compró productos de alto valor y cuándo se entregan, y vende esa información o la usa para robos.
- **Señales:** consultas a clientes sin ticket asociado; volumen de consultas inusual; exportaciones.
- **Controles:** acceso a datos solo con un caso abierto; enmascaramiento de datos; límites de consulta; revisión de accesos.

## FE-17 · Eventos falsos a través de la integración logística

- **Actor:** atacante externo con la credencial de la integración, o empleado del proveedor (interno de tercero).
- **STRIDE:** S, T, E.
- **Cómo ocurre:** la credencial de servicio de la integración logística es compartida y tiene permisos amplios. Quien la obtiene envía a delivery-api eventos de "entregado" o cambios de dirección para órdenes específicas, sin pasar por la app del repartidor.
- **Señales:** eventos sin escaneos previos en la red logística; eventos desde IPs no habituales; secuencias de estados imposibles.
- **Controles:** credenciales por sistema con mTLS o firma; lista de IPs permitidas; validación de transiciones de estado; permisos de la integración limitados a informar estados.
