# Fase 1 · Casos de uso y supuestos

Este documento descompone el flujo de venta de productos voluminosos en casos de uso y declara todos los supuestos del modelo. Es la base de las fases siguientes: el diagrama, la memoria de largo plazo de los agentes y el informe STRIDE.

Los casos de uso también están en [`data/casos_de_uso.json`](../data/casos_de_uso.json), que es la entrada que recibirán los agentes. Este documento se genera a partir de ese archivo, así que ambos siempre coinciden.

Cubre el requisito **C4** (supuestos) de la [matriz de requisitos](../REQUISITOS.md) y prepara los requisitos **B2** y **C2**.

## 1. Reglas de negocio

| ID | Regla |
|---|---|
| RN-1 | Cada cliente debe tener un único registro en la plataforma. |
| RN-2 | El costo de envío se calcula según el perfil del usuario. |
| RN-3 | El entregador debe estar en la localización de entrega cuando hace el registro de entrega (entregas a domicilio). |
| RN-4 | El usuario puede utilizar cupones de descuento. |

## 2. Actores

| Actor | Tipo | Interactúa con | Descripción |
|---|---|---|---|
| Cliente | Externo | Marketplace, punto de recolección, repartidor | Compra, paga, recibe, recoge en tienda y cancela. Puede ser legítimo o malicioso. |
| Atacante externo | Externo | Marketplace, integración logística | Sin relación legítima con la plataforma: usa cuentas robadas o credenciales filtradas. |
| Operador de atención a clientes | Interno | `clients-admin-front` | Consulta y modifica clientes y sus perfiles. |
| Operador de marketing y promociones | Interno | `cupons-frontend` | Crea, edita y distribuye cupones. |
| Operador de entregas | Interno | `delivery-admin-front` | Gestiona órdenes de entrega y sus excepciones. |
| Personal de almacén | Interno | Sistema de almacén, `delivery-api` | Prepara, empaqueta, despacha e inspecciona devoluciones. |
| Personal de tienda | Interno | Punto de recolección | Entrega productos en las recolecciones en tienda. |
| Empresa de logística | Tercero (sistema) | `logistic` → `delivery-api` | Transporta el producto y reporta los estados de entrega. |
| Personal de centros de distribución | Interno de tercero | Red de logística | Recibe, clasifica y despacha paquetes en tránsito. |
| Repartidor | Interno de tercero | App del repartidor, cliente | Entrega a domicilio y registra la entrega con su ubicación. |
| Pasarela de pago | Tercero (sistema) | Marketplace | Procesa pagos y reembolsos. |

## 3. Componentes e interacciones

Tomados del diagrama de componentes del documento. Los marcados con * no aparecen en el diagrama y se agregan como supuesto.

| Componente | Dominio | Función (según el diagrama) |
|---|---|---|
| Marketplace | Ecommerce | Sitio donde el comprador busca y compra |
| `clients-admin-front` | Ecommerce (interno) | Administrador interno de clientes y sus perfiles |
| `clients-api` | Ecommerce | Almacena clientes y sus perfiles (con base de datos) |
| `cupons-frontend` | Ecommerce (interno) | Administrador interno de cupones |
| `cupons-api` | Ecommerce | Cupones de descuento disponibles para los clientes (con base de datos) |
| `delivery-api` | Ecommerce | Calcula el costo de los envíos (con base de datos) |
| `delivery-admin-front` | Ecommerce (interno) | Administración interna para órdenes de entrega |
| `logistic` | Empresa de logística | Integración con la empresa de logística |
| Red de logística | Empresa de logística | Almacenes, transporte y entrega física |
| Pasarela de pago* | Tercero | Procesa pagos y reembolsos (S-04) |
| App del repartidor* | Empresa de logística | Registra la entrega y la ubicación (S-17) |
| Punto de recolección* | Ecommerce o aliado | Tienda donde el cliente recoge el producto (S-18) |

**Interacciones del diagrama:**

1. `clients-admin-front` → `clients-api`.
2. `cupons-frontend` → `cupons-api`.
3. `delivery-api` → `clients-api` y `cupons-api` (consulta perfil y cupones para calcular el envío).
4. `delivery-api` → `delivery-admin-front`.
5. `logistic` (empresa de logística) → `delivery-api`.
6. Red de logística → transporte → llegada al punto de entrega → entrega del paquete → comprador (flujo físico).
7. Comprador → Marketplace.

## 4. Límites de confianza

Las amenazas STRIDE se concentran donde los datos cruzan de una zona de confianza a otra. Estos límites se dibujan en el diagrama de la Fase 2.

| ID | Límite |
|---|---|
| LC-1 | Internet ↔ Marketplace: el cliente (no confiable) interactúa con la plataforma. |
| LC-2 | Marketplace ↔ APIs internas (clients-api, cupons-api, delivery-api). |
| LC-3 | Empleados ↔ frontends administrativos internos ↔ APIs internas. |
| LC-4 | Empresa de logística (tercero) ↔ delivery-api, mediante la integración logistic. |
| LC-5 | Mundo físico ↔ sistemas: dispositivo del repartidor, escaneos en almacén y centros de distribución, entrega y recolección física. |
| LC-6 | Plataforma ↔ pasarela de pago externa. |

## 5. Casos de uso

### Resumen

| ID | Caso de uso | Actores | Reglas | Límites |
|---|---|---|---|---|
| UC-01 | Registro y gestión de la cuenta del cliente | Cliente | RN-1, RN-2 | LC-1, LC-2 |
| UC-02 | Selección del producto y carrito | Cliente | Ninguna | LC-1 |
| UC-03 | Captura de datos de envío y contacto | Cliente | RN-2 | LC-1, LC-2 |
| UC-04 | Aplicación de cupón de descuento | Cliente | RN-4, RN-1 | LC-1, LC-2 |
| UC-05 | Cálculo del costo de envío según el perfil | Cliente, delivery-api | RN-2, RN-4 | LC-1, LC-2 |
| UC-06 | Elección de la modalidad de entrega | Cliente | RN-2 | LC-1, LC-2 |
| UC-07 | Pago y registro de la orden | Cliente, Pasarela de pago | RN-2, RN-4 | LC-1, LC-2, LC-6 |
| UC-08 | Preparación y empaquetado en almacén | Personal de almacén | Ninguna | LC-5 |
| UC-09 | Recolección y transporte por el proveedor logístico | Empresa de logística, Personal de centros de distribución, Repartidor | Ninguna | LC-4, LC-5 |
| UC-10 | Actualización de estados por la integración logística | Empresa de logística | RN-3 | LC-4 |
| UC-11 | Registro de entrega a domicilio con geolocalización | Repartidor, Cliente | RN-3 | LC-4, LC-5 |
| UC-12 | Recolección en tienda | Cliente, Personal de tienda | Ninguna | LC-1, LC-5 |
| UC-13 | Cancelación posterior a la recepción y devolución | Cliente, Empresa de logística, Personal de almacén | RN-4 | LC-1, LC-4, LC-5, LC-6 |
| UC-14 | Administración interna de clientes y perfiles | Operador de atención a clientes | RN-1, RN-2 | LC-3 |
| UC-15 | Administración interna de cupones | Operador de marketing y promociones | RN-4 | LC-3 |
| UC-16 | Administración interna de órdenes de entrega | Operador de entregas | RN-2, RN-3 | LC-3, LC-4 |

### UC-01 · Registro y gestión de la cuenta del cliente

El cliente crea su cuenta en el Marketplace y mantiene sus datos de perfil (identidad, contacto, direcciones).

| | |
|---|---|
| **Actores** | Cliente |
| **Componentes** | Marketplace, `clients-api` |
| **Reglas de negocio** | RN-1, RN-2 |
| **Límites de confianza** | LC-1, LC-2 |
| **Datos involucrados** | Datos personales, Correo y teléfono, Direcciones, Credenciales de acceso, Atributos del perfil |
| **Supuestos** | S-01, S-07, S-08, S-09 |

**Flujo:**

1. El cliente ingresa correo, teléfono y datos personales en el Marketplace.
2. clients-api valida que no exista otro registro con los mismos identificadores (RN-1).
3. Se verifican el correo y el teléfono con un código de un solo uso.
4. El cliente inicia sesión y edita su perfil y sus direcciones.

### UC-02 · Selección del producto y carrito

El cliente busca un producto voluminoso, lo selecciona y lo agrega al carrito con su cantidad y variante.

| | |
|---|---|
| **Actores** | Cliente |
| **Componentes** | Marketplace |
| **Reglas de negocio** | Ninguna |
| **Límites de confianza** | LC-1 |
| **Datos involucrados** | Identificador del producto, Precio, Cantidad, Disponibilidad |
| **Supuestos** | S-01, S-02 |

**Flujo:**

1. El cliente busca y abre la ficha del producto voluminoso.
2. Agrega el producto al carrito indicando cantidad y variante.
3. El Marketplace calcula el subtotal y muestra el carrito.

### UC-03 · Captura de datos de envío y contacto

Durante el pago, el cliente indica la dirección de entrega y los datos de contacto para la orden.

| | |
|---|---|
| **Actores** | Cliente |
| **Componentes** | Marketplace, `clients-api`, `delivery-api` |
| **Reglas de negocio** | RN-2 |
| **Límites de confianza** | LC-1, LC-2 |
| **Datos involucrados** | Dirección de entrega, Coordenadas o código postal, Nombre y teléfono de contacto |
| **Supuestos** | S-09, S-10 |

**Flujo:**

1. El cliente elige una dirección guardada o captura una nueva.
2. Indica nombre y teléfono de contacto para la entrega.
3. La dirección se envía a delivery-api para determinar la cobertura y el costo de envío.

### UC-04 · Aplicación de cupón de descuento

El cliente ingresa un código de cupón que se valida y se aplica a la orden o al envío.

| | |
|---|---|
| **Actores** | Cliente |
| **Componentes** | Marketplace, `cupons-api`, `delivery-api` |
| **Reglas de negocio** | RN-4, RN-1 |
| **Límites de confianza** | LC-1, LC-2 |
| **Datos involucrados** | Código del cupón, Reglas del cupón, Historial de uso por cliente |
| **Supuestos** | S-11, S-12 |

**Flujo:**

1. El cliente escribe un código de cupón en el checkout.
2. cupons-api valida vigencia, elegibilidad del cliente, monto mínimo y usos disponibles.
3. El descuento se aplica al total del producto o al costo de envío.
4. El uso del cupón se consume al confirmar el pago.

### UC-05 · Cálculo del costo de envío según el perfil

delivery-api calcula el costo de envío del producto voluminoso a partir del perfil del cliente, la dirección, el producto y los cupones.

| | |
|---|---|
| **Actores** | Cliente, delivery-api |
| **Componentes** | `delivery-api`, `clients-api`, `cupons-api`, Marketplace |
| **Reglas de negocio** | RN-2, RN-4 |
| **Límites de confianza** | LC-1, LC-2 |
| **Datos involucrados** | Atributos del perfil, Dimensiones y peso del producto, Dirección de destino, Tarifa calculada |
| **Supuestos** | S-03, S-09, S-10 |

**Flujo:**

1. El Marketplace solicita la cotización de envío a delivery-api.
2. delivery-api consulta a clients-api los atributos del perfil (nivel, membresía, zona).
3. delivery-api consulta a cupons-api si hay un cupón de envío aplicable.
4. delivery-api calcula el costo según peso, volumen, distancia y perfil, y lo devuelve al Marketplace.

### UC-06 · Elección de la modalidad de entrega

El cliente elige entre entrega a domicilio y recolección en tienda, con su costo y ventana de entrega.

| | |
|---|---|
| **Actores** | Cliente |
| **Componentes** | Marketplace, `delivery-api` |
| **Reglas de negocio** | RN-2 |
| **Límites de confianza** | LC-1, LC-2 |
| **Datos involucrados** | Modalidad de entrega, Tienda de recolección, Ventana de entrega, Costo de cada opción |
| **Supuestos** | S-10, S-18 |

**Flujo:**

1. delivery-api devuelve las opciones disponibles con su costo y fecha estimada.
2. El cliente selecciona entrega a domicilio o recolección en una tienda.
3. Si elige recolección, selecciona la tienda y se asigna a la orden.

### UC-07 · Pago y registro de la orden

El cliente paga y la orden queda registrada con su producto, precio, descuento, envío y modalidad de entrega.

| | |
|---|---|
| **Actores** | Cliente, Pasarela de pago |
| **Componentes** | Marketplace, Pasarela de pago, `delivery-api` |
| **Reglas de negocio** | RN-2, RN-4 |
| **Límites de confianza** | LC-1, LC-2, LC-6 |
| **Datos involucrados** | Total de la orden, Confirmación de pago, Medio de pago tokenizado, Orden de entrega |
| **Supuestos** | S-02, S-04, S-05 |

**Flujo:**

1. El Marketplace muestra el total final (producto, envío y descuentos).
2. El cliente paga en la pasarela de pago externa.
3. La pasarela confirma el pago al Marketplace.
4. Se registra la orden y se crea la orden de entrega en delivery-api, que inicia la preparación.

### UC-08 · Preparación y empaquetado en almacén

El almacén recibe la orden, prepara y empaqueta el producto voluminoso y lo deja listo para el proveedor logístico.

| | |
|---|---|
| **Actores** | Personal de almacén |
| **Componentes** | `delivery-api`, Red de logística |
| **Reglas de negocio** | Ninguna |
| **Límites de confianza** | LC-5 |
| **Datos involucrados** | Orden de entrega, Etiqueta y código del paquete, Peso y dimensiones reales, Estado de la orden |
| **Supuestos** | S-13, S-14 |

**Flujo:**

1. La orden aparece en la cola de preparación del almacén.
2. El personal localiza el producto, lo inspecciona y lo empaqueta.
3. Se registra peso y dimensiones, se etiqueta y se escanea el paquete.
4. La orden cambia a estado listo para recolección.

### UC-09 · Recolección y transporte por el proveedor logístico

El proveedor logístico recoge el paquete y lo transporta a través de centros de distribución y puntos de control hasta el destino.

| | |
|---|---|
| **Actores** | Empresa de logística, Personal de centros de distribución, Repartidor |
| **Componentes** | Red de logística, `logistic` |
| **Reglas de negocio** | Ninguna |
| **Límites de confianza** | LC-4, LC-5 |
| **Datos involucrados** | Eventos de escaneo, Ubicación del paquete, Asignación de ruta y repartidor |
| **Supuestos** | S-06, S-14, S-15 |

**Flujo:**

1. El proveedor logístico recoge el paquete en el almacén y escanea la entrega.
2. El paquete pasa por uno o más centros de distribución y puntos de control.
3. En cada punto se escanea el paquete y se registra el evento.
4. El paquete se asigna a una ruta y a un repartidor para la entrega final.

### UC-10 · Actualización de estados por la integración logística

La empresa de logística envía a delivery-api, mediante la integración logistic, los cambios de estado de la orden de entrega.

| | |
|---|---|
| **Actores** | Empresa de logística |
| **Componentes** | `logistic`, `delivery-api`, Marketplace |
| **Reglas de negocio** | RN-3 |
| **Límites de confianza** | LC-4 |
| **Datos involucrados** | Identificador de la orden, Estado de entrega, Marca de tiempo, Ubicación reportada, Credencial de integración |
| **Supuestos** | S-06, S-15, S-16 |

**Flujo:**

1. El sistema del proveedor logístico genera un evento (recolectado, en tránsito, en reparto, entregado, fallido).
2. logistic envía el evento a delivery-api con la credencial de la integración.
3. delivery-api actualiza el estado de la orden de entrega.
4. El Marketplace muestra el nuevo estado al cliente.

### UC-11 · Registro de entrega a domicilio con geolocalización

El repartidor registra la entrega en la dirección del cliente; el registro solo es válido si su ubicación coincide con la de entrega.

| | |
|---|---|
| **Actores** | Repartidor, Cliente |
| **Componentes** | App del repartidor, `logistic`, `delivery-api` |
| **Reglas de negocio** | RN-3 |
| **Límites de confianza** | LC-4, LC-5 |
| **Datos involucrados** | Coordenadas del dispositivo, Marca de tiempo, Evidencia de entrega, Código de confirmación |
| **Supuestos** | S-15, S-16, S-17 |

**Flujo:**

1. El repartidor llega a la dirección y entrega el producto al cliente o a quien lo recibe.
2. En su app registra la entrega con la evidencia (código de confirmación, foto o firma).
3. La app adjunta la geolocalización del dispositivo.
4. logistic envía el registro a delivery-api, que valida la distancia a la dirección de entrega (RN-3) y marca la orden como entregada.

### UC-12 · Recolección en tienda

El cliente recoge el producto voluminoso en la tienda elegida, identificándose con los datos de la orden.

| | |
|---|---|
| **Actores** | Cliente, Personal de tienda |
| **Componentes** | Marketplace, `delivery-api`, Punto de recolección |
| **Reglas de negocio** | Ninguna |
| **Límites de confianza** | LC-1, LC-5 |
| **Datos involucrados** | Código de retiro, Identificación del cliente o autorizado, Estado de la orden |
| **Supuestos** | S-18 |

**Flujo:**

1. El cliente recibe la notificación de que su producto está listo para recolección.
2. En la tienda presenta el código de retiro y una identificación.
3. El personal valida el código contra la orden y entrega el producto.
4. La orden se marca como entregada.

### UC-13 · Cancelación posterior a la recepción y devolución

Después de recibir el producto, el cliente cancela la compra desde la aplicación; el producto se devuelve y se emite el reembolso.

| | |
|---|---|
| **Actores** | Cliente, Empresa de logística, Personal de almacén |
| **Componentes** | Marketplace, `delivery-api`, `logistic`, Pasarela de pago |
| **Reglas de negocio** | RN-4 |
| **Límites de confianza** | LC-1, LC-4, LC-5, LC-6 |
| **Datos involucrados** | Motivo de cancelación, Orden de recolección inversa, Resultado de la inspección, Reembolso |
| **Supuestos** | S-12, S-19, S-20 |

**Flujo:**

1. El cliente solicita la cancelación desde la misma aplicación donde compró, indicando el motivo.
2. Se genera una orden de recolección inversa del producto voluminoso.
3. El proveedor logístico recoge el producto y lo lleva al almacén.
4. El almacén inspecciona el producto devuelto.
5. Se emite el reembolso y, si aplica, se restituye el cupón.

### UC-14 · Administración interna de clientes y perfiles

Un empleado consulta y modifica clientes y sus perfiles desde clients-admin-front.

| | |
|---|---|
| **Actores** | Operador de atención a clientes |
| **Componentes** | `clients-admin-front`, `clients-api` |
| **Reglas de negocio** | RN-1, RN-2 |
| **Límites de confianza** | LC-3 |
| **Datos involucrados** | Datos personales, Atributos del perfil, Historial de cambios |
| **Supuestos** | S-07, S-09, S-21 |

**Flujo:**

1. El empleado se autentica en clients-admin-front.
2. Busca un cliente y consulta su perfil y sus datos personales.
3. Modifica datos o atributos del perfil (por ejemplo, nivel o membresía).
4. clients-api guarda el cambio.

### UC-15 · Administración interna de cupones

Un empleado crea, modifica y distribuye cupones de descuento desde cupons-frontend.

| | |
|---|---|
| **Actores** | Operador de marketing y promociones |
| **Componentes** | `cupons-frontend`, `cupons-api` |
| **Reglas de negocio** | RN-4 |
| **Límites de confianza** | LC-3 |
| **Datos involucrados** | Definición del cupón, Segmento asignado, Presupuesto de la campaña |
| **Supuestos** | S-11, S-21 |

**Flujo:**

1. El empleado se autentica en cupons-frontend.
2. Crea o edita un cupón: valor, vigencia, usos, monto mínimo y segmento de clientes.
3. Activa el cupón y lo asigna o distribuye.
4. cupons-api lo deja disponible para su validación en el checkout.

### UC-16 · Administración interna de órdenes de entrega

Un empleado gestiona órdenes de entrega desde delivery-admin-front: consulta, reasignación, cambios de dirección y excepciones.

| | |
|---|---|
| **Actores** | Operador de entregas |
| **Componentes** | `delivery-admin-front`, `delivery-api` |
| **Reglas de negocio** | RN-2, RN-3 |
| **Límites de confianza** | LC-3, LC-4 |
| **Datos involucrados** | Órdenes de entrega, Direcciones, Estados, Costos de envío |
| **Supuestos** | S-16, S-21 |

**Flujo:**

1. El empleado se autentica en delivery-admin-front.
2. Consulta órdenes de entrega y su estado.
3. Gestiona excepciones: reprograma, cambia la dirección o la tienda, o cambia el estado manualmente.
4. delivery-api registra el cambio y lo comunica al proveedor logístico.

## 6. Supuestos

El documento pide detallar claramente todos los supuestos del modelo y del análisis de vulnerabilidades, riesgos y mitigantes. Cada supuesto indica qué implica para el análisis: cuando la información del caso no es suficiente, se declara el supuesto más razonable y se analiza también el escenario contrario si cambia el riesgo.

Los supuestos sobre controles existentes y sobre la implementación de los agentes se agregarán en las fases correspondientes.

### 6.1 Supuestos sobre el flujo y los componentes

| ID | Tema | Supuesto | Implicación para el análisis | Casos de uso |
|---|---|---|---|---|
| S-01 | Arquitectura | El Marketplace es el frontend web y móvil del cliente. Se comunica con las APIs internas a través de un API gateway o backend-for-frontend que no aparece en el diagrama (en el diagrama, el Marketplace no tiene flechas hacia las APIs). | Las peticiones del cliente cruzan LC-1 y LC-2. Todo dato enviado desde el Marketplace se considera controlable por el cliente. | UC-01, UC-02 |
| S-02 | Arquitectura | El precio del producto y el total de la orden se recalculan en el servidor al confirmar el pago; el cliente solo envía identificadores, cantidades y códigos. | No se conoce la implementación real. El análisis evalúa también el escenario en que algún valor (precio, descuento, costo de envío) se acepte desde el cliente. | UC-02, UC-07 |
| S-03 | Arquitectura | delivery-api consulta a clients-api (atributos del perfil) y a cupons-api (cupones de envío) para calcular el costo de envío, según las flechas del diagrama. | delivery-api confía en los datos de las otras dos APIs: un perfil o un cupón manipulado se traduce en un costo de envío incorrecto. | UC-05 |
| S-04 | Pagos | El pago se procesa en una pasarela externa (no dibujada). El ecommerce no almacena datos completos de tarjeta, solo tokens y la confirmación del pago. | El cumplimiento PCI DSS de la pasarela queda fuera de alcance; sí se analiza la integración con ella (LC-6). | UC-07 |
| S-05 | Pagos | La orden se registra cuando el Marketplace recibe la confirmación de pago de la pasarela (redirección o notificación asíncrona). | La confirmación de pago es un punto de abuso: si no se valida su autenticidad y su monto, una orden podría registrarse como pagada sin estarlo. | UC-07 |
| S-06 | Integración logística | La empresa de logística es un tercero. logistic es la integración entre su sistema y delivery-api (API o webhooks por internet), autenticada con una credencial de servicio compartida. El mecanismo exacto no se conoce. | Se analiza la integración como un límite de confianza (LC-4): la credencial puede filtrarse y los eventos pueden falsificarse o repetirse. | UC-09, UC-10 |
| S-07 | Identidad | Los clientes se autentican con usuario y contraseña, con un segundo factor opcional, y mantienen la sesión con un token. | Se consideran escenarios de cuentas comprometidas (credential stuffing, robo de sesión) como origen de abusos externos. | UC-01, UC-14 |
| S-08 | Identidad | La regla de registro único (RN-1) se valida con correo y teléfono verificados. No se exige un documento de identidad. | Un mismo individuo puede crear varias cuentas con correos y números distintos. Es el supuesto que más afecta a los abusos de cupones y de perfil. | UC-01 |
| S-09 | Perfil | El perfil que determina el costo de envío (RN-2) combina atributos editables por el cliente (direcciones, datos de contacto) con atributos que solo cambian los empleados o el sistema (nivel de lealtad, membresía, historial, zona). | Ambos tipos de atributos son objetivo de abuso: los primeros por el cliente, los segundos por empleados (UC-14). | UC-01, UC-03, UC-05, UC-14 |
| S-10 | Envío | La cotización de envío se calcula al elegir la dirección y la modalidad, y se asume que se vuelve a validar al confirmar el pago. | Se analiza el escenario en que la cotización no se revalida: cambiar dirección o perfil entre la cotización y el pago para obtener un envío más barato. | UC-03, UC-05, UC-06 |
| S-11 | Cupones | Cada cupón tiene reglas de valor, vigencia, usos totales, usos por cliente, monto mínimo y segmento. Los crean empleados en cupons-frontend y los valida cupons-api. | El límite de usos por cliente depende directamente de RN-1: si la unicidad del cliente se evade, también el límite del cupón. | UC-04, UC-15 |
| S-12 | Cupones | El uso de un cupón se consume al confirmar el pago y, si la compra se cancela, el cupón se restituye. La política real de restitución no está definida. | Se analiza la combinación de cupón y cancelación (UC-04 y UC-13) como vía para reutilizar cupones de un solo uso. | UC-04, UC-13 |
| S-13 | Almacén | El almacén lo opera el propio ecommerce con personal interno y un sistema de gestión de almacén conectado a delivery-api (no dibujado). | El personal de almacén se trata como usuario interno (empleado). | UC-08 |
| S-14 | Custodia | Cada paquete lleva una etiqueta con código único, y cada traspaso de custodia (almacén, proveedor, centro de distribución, repartidor) se registra con un escaneo. | La cadena de custodia permite detectar pérdidas y sustituciones; los puntos sin escaneo son oportunidades de abuso interno. | UC-08, UC-09 |
| S-15 | Actores | Los repartidores y el personal de los centros de distribución son empleados del proveedor logístico. Para el análisis se tratan como usuarios internos extendidos (insiders de un tercero). | El documento pide abusos de usuarios internos (empleados) y externos (clientes). Estos actores se clasifican como internos de tercero y se reportan junto a los internos. | UC-09, UC-10, UC-11 |
| S-16 | Estados de entrega | Los estados de entrega, incluido "entregado", los reporta el proveedor a través de logistic. Además, delivery-admin-front permite cambiar estados manualmente. | Un estado puede alterarse por dos vías (integración y panel interno); ambas se analizan. | UC-10, UC-11, UC-16 |
| S-17 | Geolocalización | La ubicación la obtiene el dispositivo móvil del repartidor y se envía al registrar la entrega. delivery-api la compara con las coordenadas de la dirección dentro de un radio de tolerancia (RN-3). | La ubicación es un dato generado del lado del cliente (el dispositivo del repartidor) y, por tanto, falsificable. Es el supuesto central para los abusos de UC-11. | UC-11 |
| S-18 | Recolección en tienda | Las tiendas de recolección las opera el ecommerce o un aliado. El retiro se valida con un código de la orden y una identificación, y el cliente puede autorizar a un tercero. | El personal de tienda se trata como usuario interno; la autorización a terceros es un punto de abuso. | UC-06, UC-12 |
| S-19 | Cancelación | La cancelación posterior a la recepción requiere una recolección inversa del producto voluminoso. El reembolso se emite cuando el proveedor confirma la recolección y el almacén inspecciona el producto, dentro de una ventana de días desde la entrega. | No se conoce si el reembolso se emite antes de la inspección. El análisis evalúa ambos escenarios, porque determinan el riesgo de devolver un artículo distinto o dañado. | UC-13 |
| S-20 | Cancelación | El reembolso se realiza al medio de pago original a través de la pasarela. | Se analiza el desvío de reembolsos (cambio del medio de reembolso) solo si se permitiera; por defecto se asume que no. | UC-13 |
| S-21 | Identidad interna | Los empleados se autentican con el SSO corporativo y cada frontend administrativo tiene roles. No se conoce la granularidad: si existen aprobaciones dobles, límites por monto o segregación de funciones. | Se analiza el caso en que un solo empleado puede crear y usar beneficios (cupones, cambios de perfil o de estado) sin aprobación de otra persona. | UC-14, UC-15, UC-16 |

### 6.2 Supuestos generales y de alcance

| ID | Tema | Supuesto | Implicación para el análisis | Casos de uso |
|---|---|---|---|---|
| S-22 | Alcance | El análisis se centra en la lógica de negocio y en las integraciones del flujo. Quedan fuera de alcance los ataques volumétricos de denegación de servicio, la infraestructura de nube y la seguridad física de los almacenes, salvo cuando afectan la lógica del flujo (por ejemplo, el robo interno de un paquete). | El informe prioriza abusos que explotan reglas y procesos, que es lo que pide el reto. | Todos |
| S-23 | Alcance | Los productos voluminosos son de alto valor y difíciles de manipular: la entrega se agenda, puede requerir dos personas y deja evidencia (foto, firma o código de confirmación). | El alto valor por orden aumenta el impacto de cada abuso exitoso; la evidencia de entrega es un control a evaluar. | Todos |
| S-24 | Arquitectura | La comunicación entre componentes usa HTTPS y las APIs internas no están expuestas a internet, salvo a través del gateway del Marketplace (S-01) y de la integración logística (S-06). | Las amenazas de interceptación en la red interna se consideran de baja probabilidad y no son foco del análisis. | Todos |
| S-25 | Actores de amenaza | Externos: clientes legítimos que abusan de las reglas, defraudadores organizados y atacantes con cuentas robadas. Internos: empleados del ecommerce (atención a clientes, marketing, entregas, almacén, tiendas). Internos de tercero: repartidores y personal del proveedor logístico. | Cada caso de abuso del informe indica a cuál de estos grupos pertenece el actor. | Todos |
