# STRIDE aplicado a un DFD de ecommerce

Documento curado para la memoria de largo plazo (segmento `ltm_amenazas`, fuente `stride`).
Cada sección de nivel 2 es un fragmento. Redacción propia del proyecto.

## STRIDE-S · Suplantación (Spoofing)

- **Propiedad que se viola:** autenticidad.
- **Elementos del DFD afectados:** entidades externas y procesos.
- **Qué es:** un actor se hace pasar por otro usuario, sistema o dispositivo para que el sistema acepte sus acciones o datos como legítimos.
- **Preguntas guía:** ¿cómo sabe el receptor quién envía cada flujo? ¿La identidad se basa en algo que el actor controla (un identificador en la petición, un dato del dispositivo, un correo)? ¿Una credencial de servicio se comparte entre varios sistemas o personas? ¿Se puede repetir un mensaje firmado?
- **Vectores prácticos en ecommerce:** relleno de credenciales para tomar cuentas de clientes; uso de la credencial compartida de una integración para enviar eventos falsos; ubicación GPS simulada en el teléfono del repartidor; código de retiro en tienda reenviado o interceptado; identificación falsa o de un tercero en el punto de recolección; notificación de pago falsificada hacia el webhook de la plataforma.
- **Controles típicos:** autenticación multifactor para clientes y empleados; credenciales de servicio individuales con mTLS o firma de mensajes y rotación; verificación de firma e idempotencia en notificaciones de pago; atestación del dispositivo; códigos de un solo uso ligados a la orden y al titular.

## STRIDE-T · Manipulación (Tampering)

- **Propiedad que se viola:** integridad.
- **Elementos del DFD afectados:** procesos, flujos de datos y almacenes de datos.
- **Qué es:** modificar datos en tránsito, en reposo o en la lógica del proceso para obtener un resultado distinto al permitido por las reglas de negocio.
- **Preguntas guía:** ¿qué valores que vienen del cliente se usan para calcular dinero (precio, descuento, costo de envío)? ¿Quién puede editar los atributos que determinan una regla? ¿Los cambios de estado siguen una máquina de estados o se pueden saltar pasos? ¿Dos peticiones simultáneas pueden usar el mismo recurso dos veces?
- **Vectores prácticos en ecommerce:** cambiar precio, cantidad o costo de envío en la petición del carrito; aplicar el mismo cupón en peticiones paralelas (condición de carrera); editar atributos del perfil para que el envío cueste menos; cambiar la dirección de entrega después del pago; marcar una orden como entregada o cancelada desde el backoffice sin evidencia; enviar un evento de estado fuera de orden desde la integración logística.
- **Controles típicos:** recalcular en el servidor todo valor monetario; validación de transiciones de estado; bloqueo o restricción única para el uso de cupones; registro de cambios con aprobación doble en atributos sensibles; firma o hash de eventos entre sistemas.

## STRIDE-R · Repudio (Repudiation)

- **Propiedad que se viola:** no repudio.
- **Elementos del DFD afectados:** entidades externas, procesos y almacenes que guardan registros.
- **Qué es:** un actor niega haber realizado una acción y el sistema no tiene evidencia suficiente para demostrar lo contrario.
- **Preguntas guía:** ¿cada cambio manual queda registrado con quién, cuándo, desde dónde y por qué? ¿La evidencia de entrega es verificable por un tercero? ¿Los registros pueden ser editados por el mismo actor que hizo la acción?
- **Vectores prácticos en ecommerce:** el cliente afirma no haber recibido un pedido entregado sin firma ni foto; un operador cambia un estado y luego niega haberlo hecho porque la cuenta es compartida; el repartidor alega que la ubicación era correcta; el proveedor logístico atribuye un faltante al almacén y viceversa por falta de escaneo en el traspaso.
- **Controles típicos:** bitácora inmutable de acciones; cuentas nominales sin usuarios compartidos; evidencia de entrega con código de confirmación del cliente, foto y marca de tiempo; escaneo obligatorio en cada traspaso de custodia.

## STRIDE-I · Divulgación de información (Information disclosure)

- **Propiedad que se viola:** confidencialidad.
- **Elementos del DFD afectados:** procesos, flujos de datos y almacenes de datos.
- **Qué es:** exponer datos a quien no debería verlos, ya sea por exceso de datos en una respuesta, por falta de autorización a nivel de objeto o por acceso interno excesivo.
- **Preguntas guía:** ¿una API devuelve más campos de los que la pantalla necesita? ¿Se valida que el objeto pedido pertenece a quien lo pide? ¿Qué datos personales ve un operador o un repartidor y por cuánto tiempo?
- **Vectores prácticos en ecommerce:** enumerar identificadores de órdenes para leer direcciones y teléfonos de otros clientes; usar mensajes de error del registro para saber qué correos tienen cuenta; empleado de atención que exporta datos de clientes; repartidor que conserva direcciones y horarios de entrega de productos de alto valor.
- **Controles típicos:** autorización a nivel de objeto; respuestas mínimas; mensajes de error genéricos; enmascaramiento de datos en backoffice y app del repartidor; límites de consulta y alertas de exportación masiva.

## STRIDE-D · Denegación de servicio (Denial of service)

- **Propiedad que se viola:** disponibilidad.
- **Elementos del DFD afectados:** procesos, flujos de datos y almacenes de datos.
- **Qué es:** impedir que usuarios legítimos usen el servicio o un recurso del negocio. En este análisis interesa la denegación a nivel de lógica de negocio, no la saturación de red.
- **Preguntas guía:** ¿se puede reservar inventario o franjas de entrega sin pagar? ¿Se puede bloquear la cuenta de otro cliente con intentos fallidos? ¿Hay operaciones costosas sin límite de frecuencia?
- **Vectores prácticos en ecommerce:** carritos o pedidos sin pagar que acaparan inventario de productos voluminosos (denegación de inventario); reservar todas las franjas de recolección en tienda; bloquear cuentas ajenas con intentos de inicio de sesión; agotar cupones de cantidad limitada con cuentas automatizadas.
- **Controles típicos:** tiempo de expiración en reservas; límites por cliente, dispositivo y dirección; protección contra automatización; bloqueo progresivo en lugar de bloqueo total.

## STRIDE-E · Elevación de privilegios (Elevation of privilege)

- **Propiedad que se viola:** autorización.
- **Elementos del DFD afectados:** procesos.
- **Qué es:** un actor ejecuta acciones fuera de su rol, ya sea por fallas de autorización a nivel de función o porque un rol legítimo tiene más permisos de los necesarios.
- **Preguntas guía:** ¿las APIs internas validan el rol de quien llama o confían en que el frontend ya lo hizo? ¿Un cliente puede llamar funciones administrativas? ¿Un operador puede aprobar sus propias acciones? ¿Hay segregación de funciones entre quien crea un cupón y quien lo aprueba?
- **Vectores prácticos en ecommerce:** llamar directamente a un endpoint administrativo de cupons-api desde fuera del backoffice; operador de marketing que crea un cupón de 100 % sin límite y lo usa o lo vende; operador de atención que cambia el perfil de un conocido para darle envío gratis; integración logística con permisos para modificar órdenes, no solo para informar estados.
- **Controles típicos:** autorización a nivel de función en cada API; mínimo privilegio por rol; segregación de funciones y aprobación doble para montos altos; revisiones periódicas de accesos.

## STRIDE por tipo de elemento del DFD

- **Entidad externa** (cliente, operador, repartidor, pasarela, empresa de logística): S, R.
- **Proceso** (Marketplace, APIs, frontends administrativos, logistic, app del repartidor): S, T, R, I, D, E.
- **Almacén de datos** (órdenes, clientes, cupones, estados de entrega): T, I, D, y R si guarda registros de auditoría.
- **Flujo de datos** (F1–F30): T, I, D.
- **Límite de confianza:** cada flujo que cruza un límite (LC-1 a LC-6) es el lugar donde el receptor debe validar autenticidad, integridad y autorización; ahí se concentran los casos de abuso.
- **Uso en el análisis:** para cada caso de uso se recorren sus elementos y flujos, se aplican solo las categorías que corresponden a cada tipo de elemento y se buscan vectores que combinen un cruce de límite con una regla de negocio (RN-1 a RN-4).
