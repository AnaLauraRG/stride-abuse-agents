"""Genera docs/08-informe-stride.md a partir de data/casos_de_abuso.json.

Las secciones narrativas (riesgos y controles) son la síntesis del analista; las tablas,
los conteos y los anexos salen de los datos, así que el informe no puede desalinearse de ellos.

Uso:  python3 scripts/catalogo.py && python3 scripts/generar_informe.py
"""
import collections
import json
import re
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
DATOS = json.loads((RAIZ / "data" / "casos_de_abuso.json").read_text(encoding="utf-8"))
UCS = {u["id"]: u for u in json.loads((RAIZ / "data" / "casos_de_uso.json").read_text(encoding="utf-8"))["casos_de_uso"]}
TODOS = DATOS["casos"]
CASOS = [c for c in TODOS if c["consolidado"]]
FUERA = [c for c in TODOS if not c["consolidado"]]

STRIDE = {"S": "Suplantación", "T": "Manipulación", "R": "Repudio", "I": "Divulgación de información",
          "D": "Denegación de servicio", "E": "Elevación de privilegios"}
ACTOR = {"externo": "externo", "interno": "interno", "interno_tercero": "interno de tercero"}
RESP = {"ecommerce": "ecommerce", "proveedor_logistico": "proveedor logístico", "pasarela_pago": "pasarela de pago"}

# ----------------------------------------------------------------------------- grupos de actores
def grupo_interno(c):
    rol = c["actor"]["rol"].lower()
    if c["id"] == "AC-UC11-03":
        return "Repartidor"
    if c["actor"]["tipo"] == "interno":
        for clave, g in [("operaciones", "Empleado de operaciones con acceso a órdenes"),
                         ("atención", "Operador de atención a clientes"), ("marketing", "Operador de marketing y promociones"),
                         ("entregas", "Operador de entregas"), ("rol de consulta", "Operador de entregas"),
                         ("almacén", "Personal de almacén"), ("tienda", "Personal de tienda")]:
            if clave in rol:
                return g
        return "Otro empleado"
    if c["actor"]["tipo"] == "interno_tercero":
        if rol.startswith("repartidor"):
            return "Repartidor"
        if "agencia" in rol:
            return "Agencia de marketing contratada"
        return "Personal del proveedor logístico"
    return None


def grupo_externo(c):
    if c["actor"]["tipo"] != "externo":
        return None
    rol = c["actor"]["rol"].lower()
    if c["id"] in ("AC-UC14-05", "AC-UC15-01", "AC-UC16-05"):
        return "Atacante externo contra cuentas de empleados"
    if rol.startswith("cliente"):
        return "Cliente"
    return "Atacante externo"


ORDEN_INTERNOS = ["Operador de atención a clientes", "Operador de marketing y promociones", "Operador de entregas",
                  "Personal de almacén", "Personal de tienda", "Empleado de operaciones con acceso a órdenes",
                  "Repartidor", "Personal del proveedor logístico", "Agencia de marketing contratada", "Otro empleado"]
ORDEN_EXTERNOS = ["Cliente", "Atacante externo", "Atacante externo contra cuentas de empleados"]

# ----------------------------------------------------------------------------- riesgos (síntesis del analista)
RIESGOS = {
    "R1": {
        "nombre": "Evidencia y registros que no prueban lo que ocurrió",
        "descripcion": "Entregas, retiros, traspasos de custodia, inspecciones y confirmaciones se registran con datos que genera o controla la misma parte que se beneficia (GPS del dispositivo, foto, firma ilegible, escaneo opcional, estado marcado a mano). El sistema acepta el registro como prueba del hecho físico, y ante un reclamo nadie puede demostrar qué pasó.",
        "donde": "LC-5 (mundo físico ↔ sistemas) en F14–F23; RN-3",
        "controles": [
            "Código de confirmación de un solo uso del cliente obligatorio para cerrar entregas y retiros de alto valor; foto o firma solo como complemento.",
            "Atestación del dispositivo y detección de ubicación simulada en la app del repartidor; registro de entrega firmado en el dispositivo.",
            "Escaneo conjunto con peso y foto en cada traspaso de custodia (almacén → proveedor → repartidor → cliente o tienda).",
            "Conciliación diaria entre despachos, escaneos del proveedor, entregas e inventario de tiendas.",
            "Registro inmutable de la orden con la referencia de pago, la dirección confirmada y la evidencia de entrega, para disputas y contracargos.",
        ],
    },
    "R2": {
        "nombre": "Montos y beneficios calculados con datos que controla el cliente",
        "descripcion": "Precio, cantidad, costo de envío, modalidad, tienda, atributos del perfil, reglas del cupón y monto del pago viajan en peticiones del cliente o entre servicios sin recalcularse ni firmarse. Quien intercepta su propio tráfico o encadena pasos fuera de orden paga menos o recibe beneficios que no le corresponden.",
        "donde": "LC-1 y LC-2 en F1, F3–F7, F9, F10; RN-2 y RN-4",
        "controles": [
            "Recalcular en el servidor, al confirmar la orden, todo valor monetario: precio desde el catálogo, envío con delivery-api, descuento con cupons-api.",
            "Cotización firmada y con vigencia corta, ligada a la orden, la dirección, la modalidad y la tienda; cualquier cambio obliga a recotizar.",
            "Atributos de beneficio del perfil (nivel, membresía, zona) editables solo por procesos del servidor; listas de campos permitidos en cada API.",
            "Reserva atómica del cupón (restricción única o bloqueo) antes del cobro, y validación con los datos de la orden final.",
            "Comparar el monto confirmado por la pasarela con el total registrado de la orden antes de liberarla.",
        ],
    },
    "R3": {
        "nombre": "Privilegios internos sin segregación ni trazabilidad",
        "descripcion": "Operadores de atención, marketing y entregas, personal de almacén y personal del proveedor pueden cambiar perfiles, cupones, direcciones, estados y asignaciones sin motivo, sin segunda aprobación, con cuentas compartidas o con permisos más amplios que su rol. Las APIs internas confían en que el frontend ya filtró lo que el operador puede hacer.",
        "donde": "LC-3 en F24–F29; LC-4 en F30; RN-1, RN-2 y RN-4",
        "controles": [
            "Autorización por función y por objeto en cada API interna, no solo en el frontend; mínimo privilegio y alcance por región, tienda o campaña.",
            "Doble aprobación para cambios sensibles: cupones de alto valor o sin límite, estados finales, direcciones de órdenes pagadas, atributos de beneficio.",
            "Motivo obligatorio y vínculo con un caso o ticket en cada cambio manual; acceso a datos personales solo con un caso abierto.",
            "Cuentas nominales con SSO y MFA; bitácora inmutable (quién, qué, cuándo, desde dónde, valor anterior y nuevo).",
            "Alertas por concentración: el mismo operador sobre las mismas cuentas, excepciones frecuentes, cambios fuera de horario.",
        ],
    },
    "R4": {
        "nombre": "Confianza ciega en la integración logística y en las confirmaciones de pago",
        "descripcion": "delivery-api acepta eventos de estado, entrega y ubicación de logistic con una credencial de servicio compartida y con permisos más amplios que informar estados; el Marketplace acepta confirmaciones de pago sin verificar firma, unicidad ni correspondencia con la orden. Quien obtiene la credencial, o un empleado del proveedor, fabrica o repite eventos que el sistema toma como verdad.",
        "donde": "LC-4 en F19 y F30; LC-6 en F6 y F7",
        "controles": [
            "Credenciales por sistema con mTLS o firma de mensajes, rotación y lista de IPs permitidas; permisos de la integración limitados a informar estados.",
            "Eventos firmados con identificador único, secuencia y marca de tiempo; rechazo de repeticiones y de transiciones de estado imposibles.",
            "Validar la firma de cada notificación de la pasarela y consultar el estado del pago a la pasarela antes de dar la orden por pagada.",
            "Referencias de pago de un solo uso, ligadas a la orden y al monto.",
            "Sanear y codificar los campos de texto de los eventos (ubicación, notas) antes de mostrarlos al cliente o en el backoffice.",
        ],
    },
    "R5": {
        "nombre": "Toma de cuentas de clientes y de empleados",
        "descripcion": "Con credenciales filtradas, sesiones robadas o phishing, un atacante entra a la cuenta de un cliente (y cambia dirección o contacto, agrega un autorizado o compra con el medio de pago guardado) o a la de un operador (y lee o modifica clientes, cupones y órdenes). La verificación del teléfono sin límite de intentos permite asociar el número de otra persona.",
        "donde": "LC-1 en F1 y F3; LC-3 en F24–F26",
        "controles": [
            "MFA para empleados siempre y para clientes en acciones sensibles: cambio de dirección o contacto, autorizados de retiro, uso de medios de pago guardados.",
            "Protección contra relleno de credenciales: límite de intentos, detección de automatización, credenciales filtradas y dispositivos nuevos.",
            "Códigos de verificación con pocos intentos, expiración corta y bloqueo progresivo.",
            "Aviso al titular por un canal independiente antes de que surta efecto un cambio de contacto, dirección o autorizado, con opción de revertirlo.",
        ],
    },
    "R6": {
        "nombre": "Reembolsos y restituciones antes de verificar la devolución",
        "descripcion": "El reembolso y la restitución del cupón se disparan con la solicitud de cancelación, con la confirmación de recolección del proveedor o con una inspección que registra una sola persona. El cliente devuelve otra cosa, cancela dos veces en paralelo o reutiliza el cupón; un empleado o un conductor confirma lo que no recibió.",
        "donde": "F5, F6, F14 y F30 en UC-13; S-11, S-12 y S-19",
        "controles": [
            "Reembolso solo después de la inspección en almacén, con número de serie, peso y fotos comparados con el despacho original.",
            "Inspecciones de alto valor confirmadas por una segunda persona.",
            "Cancelación idempotente: un identificador único de reembolso y una máquina de estados que impide reembolsar dos veces.",
            "Restitución del cupón solo cuando la devolución queda recibida e inspeccionada.",
        ],
    },
    "R7": {
        "nombre": "Exposición de datos personales y de negocio",
        "descripcion": "Perfiles, direcciones, órdenes, códigos de retiro y datos de stock se leen cambiando identificadores en las peticiones (autorización por objeto ausente), enumerando respuestas diferenciadas, abusando del acceso interno de consulta o leyendo etiquetas en el transporte. Un texto malicioso guardado por un cliente puede ejecutarse en el panel de un empleado.",
        "donde": "LC-1 y LC-2 en F1–F5; LC-3 en F27 y F29; F15–F20",
        "controles": [
            "Autorización por objeto en cada consulta (la orden, la dirección o el perfil pertenecen a quien pregunta); identificadores no predecibles.",
            "Respuestas mínimas y mensajes de error genéricos en registro, cupones y consultas de disponibilidad.",
            "Enmascaramiento de datos en backoffice, app del repartidor y etiquetas; límites de consulta y alertas de extracción masiva.",
            "Codificación de salida y política de seguridad de contenido en los paneles internos que muestran datos capturados por clientes.",
        ],
    },
    "R8": {
        "nombre": "Abuso de beneficios y de capacidad mediante automatización",
        "descripcion": "Cuentas creadas en masa (correo desechable y teléfono virtual eluden RN-1), enumeración de cupones y scripts que acaparan inventario, ventanas de entrega o espacio en puntos de recolección sin pagar ni retirar. No hace falta romper nada: basta repetir el flujo normal más veces de las previstas.",
        "donde": "LC-1 en F1, F4 y F5; RN-1 y RN-4",
        "controles": [
            "Unicidad del cliente con señales adicionales (dispositivo, dirección de entrega, medio de pago), no solo correo y teléfono.",
            "Protección contra automatización y límites por cuenta, dispositivo, dirección y medio de pago.",
            "Códigos de cupón largos y aleatorios, ligados a la cuenta destinataria; límite de intentos de validación.",
            "Reservas de inventario, ventanas y capacidad de tienda con expiración corta y tope de pendientes por cliente.",
        ],
    },
}

ASIGNACION = {
    "R1": "UC03-06 UC07-05 UC08-01 UC08-02 UC09-01 UC09-02 UC09-04 UC11-01 UC11-02 UC11-03 UC11-04 UC12-01 UC12-02 UC12-04",
    "R2": "UC01-05 UC02-01 UC03-01 UC04-02 UC04-04 UC05-01 UC05-03 UC05-04 UC05-05 UC06-01 UC06-02 UC06-03 UC07-02 UC07-04",
    "R3": "UC04-05 UC05-02 UC05-06 UC07-07 UC08-03 UC09-03 UC09-06 UC14-02 UC14-03 UC14-04 UC14-06 UC15-02 UC15-04 UC15-05 UC16-01 UC16-02 UC16-04 UC16-06",
    "R4": "UC07-01 UC07-03 UC10-01 UC10-02 UC10-03 UC10-04 UC10-05 UC10-07",
    "R5": "UC01-02 UC01-03 UC03-03 UC12-03 UC14-05 UC15-01 UC16-05",
    "R6": "UC13-01 UC13-02 UC13-03 UC13-05 UC13-06",
    "R7": "UC01-04 UC01-06 UC02-03 UC03-02 UC03-05 UC07-06 UC09-05 UC12-05 UC13-04 UC14-01 UC15-03 UC16-03",
    "R8": "UC01-01 UC02-02 UC04-01 UC04-03 UC06-04 UC12-06",
}
RIESGO_DE = {}
for r, ids in ASIGNACION.items():
    for i in ids.split():
        RIESGO_DE["AC-" + i] = r

# Buenas prácticas transversales: patrón de búsqueda sobre el texto de los controles propuestos.
PRACTICAS = [
    ("Alertas y monitoreo de patrones de abuso", r"alerta|monitoreo|SIEM"),
    ("Firma, mTLS o integridad criptográfica de datos entre partes", r"\bfirma\b|\bfirmad|HMAC|mTLS"),
    ("Conciliación entre registros (despachos, escaneos, entregas, pagos)", r"concilia"),
    ("Notificación al titular de cambios y eventos sensibles", r"notific|aviso al|avisar al"),
    ("Recalcular en el servidor los valores que envía el cliente", r"recalcul|en el servidor|autoritativ"),
    ("Código de confirmación o escaneo obligatorio", r"código de confirmación|escaneo|escanear"),
    ("Bitácora inmutable de acciones", r"inmutable|append-only"),
    ("Doble aprobación o segregación de funciones", r"segundo usuario|doble aprobaci|aprobación de (un|otra|otro)|segregaci|supervisor"),
    ("Motivo obligatorio o vínculo con un caso de soporte", r"caso abierto|ticket|motivo obligatorio|con motivo|justificaci"),
    ("Mínimo privilegio y alcance por rol", r"mínimo privilegio|por rol|topes del rol|alcance"),
    ("Idempotencia, identificadores únicos y códigos de un solo uso", r"idempoten|un solo uso|nonce"),
    ("Límites de frecuencia y protección contra automatización", r"rate limit|limitación de tasa|límite de (intentos|peticiones)|automatizaci|CAPTCHA"),
    ("Autenticación multifactor", r"\bMFA\b|segundo factor|multifactor"),
    ("Autorización por objeto y por función en las APIs", r"autorización a nivel|por objeto|pertenencia|propiedad de|nivel de función"),
]

# ----------------------------------------------------------------------------- utilidades
def uc_nombre(uc_id):
    return f"{uc_id} {UCS[uc_id]['nombre']}" if uc_id in UCS else uc_id


def esc(t):
    return str(t).replace("|", "\\|").replace("\n", " ")


def stride_txt(c):
    s = c["stride"]["principal"]
    sec = [x for x in c["stride"].get("secundarias", []) if x != s]
    return s + (f" ({', '.join(sec)})" if sec else "")


def riesgo_txt(c):
    r = c.get("riesgo")
    return f"{r['nivel']} ({r['probabilidad']}×{r['impacto']})" if r else "—"


def ancla(c):
    return f"[{c['consolidado']}](#{c['consolidado'].lower()})"


def tabla_casos(casos):
    filas = ["| Caso | Caso de uso | STRIDE | Abuso | Riesgo | Tema |", "|---|---|---|---|---|---|"]
    for c in casos:
        filas.append(f"| {ancla(c)} | {c['caso_de_uso']} | {stride_txt(c)} | {esc(c['titulo'])} | {riesgo_txt(c)} | {RIESGO_DE.get(c['id'], '—')} |")
    return "\n".join(filas)


def orden(c):
    return int(c["consolidado"].split("-")[1])


# ----------------------------------------------------------------------------- secciones
def seccion_resumen():
    n = len(CASOS)
    porst = collections.Counter(c["stride"]["principal"] for c in CASOS)
    internos = [c for c in CASOS if grupo_interno(c)]
    externos = [c for c in CASOS if grupo_externo(c)]
    altos = sum(1 for c in CASOS if c.get("riesgo", {}).get("nivel") == "alto")
    ranking = ranking_riesgos()
    top = "\n".join(f"{i}. **{r} · {RIESGOS[r]['nombre']}** ({s['n']} casos, {s['altos']} de riesgo alto)"
                    for i, (r, s) in enumerate(ranking[:4], 1))
    return f"""## 1. Resumen ejecutivo

Se modeló con STRIDE el flujo de venta de productos voluminosos (16 casos de uso, 30 flujos de datos y 6 límites de confianza) y se obtuvieron **{n} casos de abuso** dentro del alcance, más {len(FUERA)} fuera de alcance que se documentan aparte. Los casos los generó la capa de agentes (Claude con memoria de largo plazo), los revisó un agente revisor y los aprobó un analista.

| | |
|---|---|
| Casos de abuso en alcance | **{n}**, en los 16 casos de uso |
| Por categoría STRIDE | {" · ".join(f"{k} {porst[k]}" for k in "STRIDE")} |
| Por actor | {len(externos)} de actores externos · {len(internos)} de empleados (propios o del proveedor logístico); la colusión AC-UC11-03 cuenta en ambos |
| Riesgo alto | {altos} casos |
| Controles propuestos | {sum(len(c['controles']) for c in CASOS)} (preventivos, detectivos y correctivos) |

**Hallazgo central.** La mayoría de los abusos no necesita una vulnerabilidad técnica clásica: explotan que el sistema **confía en datos que controla quien se beneficia**: el precio y el envío que manda el cliente, el GPS del repartidor, el estado que marca un operador, el evento que envía el proveedor con una credencial compartida. Los riesgos principales son:

{top}

**Primeras medidas recomendadas:** recalcular y firmar en el servidor todo valor monetario; exigir una prueba que no controle quien se beneficia (código del cliente, escaneo conjunto, segunda aprobación) para cerrar entregas, retiros, inspecciones y cambios manuales; individualizar y firmar la integración logística; y aplicar autorización por objeto y por función en cada API interna."""


def seccion_metodo():
    return """## 2. Alcance y método

**Alcance.** Lógica de negocio e integraciones del flujo descrito en [`01-casos-de-uso-y-supuestos.md`](01-casos-de-uso-y-supuestos.md), sobre el diagrama de [`02-diagrama.md`](02-diagrama.md). Fuera de alcance (S-22): denegación de servicio volumétrica, infraestructura de nube y seguridad física, salvo cuando afectan la lógica del flujo. Las APIs internas no están expuestas a internet (S-24).

**Método.**
1. **STRIDE por elemento del DFD.** Entidades externas: S, R. Procesos: S, T, R, I, D, E. Almacenes de datos: T, R, I, D. Flujos: T, I, D. La búsqueda se concentró en los flujos que cruzan un límite de confianza (LC-1 a LC-6) y tocan una regla de negocio (RN-1 a RN-4).
2. **Generación asistida por LLM** (requisito del reto). WF-2 ([`06-agentes.md`](06-agentes.md)) recupera para cada caso de uso el contexto de la memoria de largo plazo (negocio, CAPEC, OWASP, patrones de fraude y casos ya validados), y el agente generador propone casos de abuso con el prompt público de 96 palabras ([`../prompts/README.md`](../prompts/README.md)).
3. **Revisión en dos niveles.** El agente revisor exige pasos concretos, vector práctico, categoría STRIDE correcta, coherencia con los supuestos y que no se repitan casos validados; los rechazados vuelven al generador con observaciones. Después, el analista decide qué se consolida ([`07-ejecucion.md`](07-ejecucion.md)).
4. **Riesgo.** Probabilidad e impacto de 1 a 3 estimados por el agente de mitigación; nivel = producto (1–2 bajo, 3–4 medio, 6–9 alto). Los temas de riesgo de la sección 7 son la agrupación del analista.

**Ajustes del analista** sobre la salida de los agentes:

""" + "\n".join(f"- **{c['id']}:** {c['ajuste_analista']}" for c in CASOS if c.get("ajuste_analista"))


def seccion_matriz():
    lineas = ["## 3. Matriz STRIDE", "",
              "Número de casos de abuso por caso de uso y categoría principal. Cada caso aparece una vez, en su categoría principal; las secundarias están en el anexo A.", "",
              "| Caso de uso | S | T | R | I | D | E | Total | Internos | Externos |", "|---|---|---|---|---|---|---|---|---|---|"]
    tot = collections.Counter()
    for uc in sorted({c["caso_de_uso"] for c in CASOS}):
        cs = [c for c in CASOS if c["caso_de_uso"] == uc]
        cnt = collections.Counter(c["stride"]["principal"] for c in cs)
        tot.update(cnt)
        ni = sum(1 for c in cs if grupo_interno(c))
        ne = sum(1 for c in cs if grupo_externo(c))
        lineas.append(f"| {uc_nombre(uc)} | " + " | ".join(str(cnt[k] or "·") for k in "STRIDE") + f" | **{len(cs)}** | {ni} | {ne} |")
    ni = sum(1 for c in CASOS if grupo_interno(c))
    ne = sum(1 for c in CASOS if grupo_externo(c))
    lineas.append("| **Total** | " + " | ".join(f"**{tot[k]}**" for k in "STRIDE") + f" | **{len(CASOS)}** | **{ni}** | **{ne}** |")
    lineas += ["", "El caso AC-UC11-03 (colusión cliente–repartidor) cuenta en las dos columnas de actores.", "",
               "**Por límite de confianza** (un caso puede cruzar varios):", "",
               "| Límite | Casos | Descripción |", "|---|---|---|"]
    desc = json.loads((RAIZ / "data" / "casos_de_uso.json").read_text(encoding="utf-8"))["limites_confianza"]
    porlc = collections.Counter(lc for c in CASOS for lc in set(c.get("limites_confianza", [])) if lc in desc)
    for lc in sorted(desc):
        lineas.append(f"| {lc} | {porlc[lc]} | {esc(desc[lc])} |")
    return "\n".join(lineas)


def seccion_grupo(titulo, intro, grupo_fn, orden_grupos):
    lineas = [titulo, "", intro, ""]
    grupos = collections.defaultdict(list)
    for c in CASOS:
        g = grupo_fn(c)
        if g:
            grupos[g].append(c)
    for g in orden_grupos:
        if g not in grupos:
            continue
        cs = sorted(grupos[g], key=orden)
        altos = sum(1 for c in cs if c.get("riesgo", {}).get("nivel") == "alto")
        lineas += [f"### {g} ({len(cs)} {'caso' if len(cs) == 1 else 'casos'}, {altos} de riesgo alto)", "", tabla_casos(cs), ""]
    return "\n".join(lineas)


def ranking_riesgos():
    stats = {}
    for r in RIESGOS:
        cs = [c for c in CASOS if RIESGO_DE.get(c["id"]) == r]
        stats[r] = {"n": len(cs), "altos": sum(1 for c in cs if c.get("riesgo", {}).get("nivel") == "alto"),
                    "ucs": sorted({c["caso_de_uso"] for c in cs}),
                    "internos": sum(1 for c in cs if grupo_interno(c)), "externos": sum(1 for c in cs if grupo_externo(c)),
                    "casos": sorted(cs, key=orden)}
    return sorted(stats.items(), key=lambda kv: (-kv[1]["altos"], -kv[1]["n"], kv[0]))


def seccion_controles():
    lineas = ["## 6. Controles de seguridad y buenas prácticas", "",
              f"Los agentes propusieron **{sum(len(c['controles']) for c in CASOS)} controles** para los {len(CASOS)} casos (cada caso tiene al menos uno preventivo y uno detectivo; el detalle está en el anexo A). Esta sección los agrupa.", "",
              "### 6.1 Controles prioritarios por riesgo", ""]
    for r, s in ranking_riesgos():
        lineas += [f"**{r} · {RIESGOS[r]['nombre']}**", ""] + [f"- {x}" for x in RIESGOS[r]["controles"]] + [""]
    lineas += ["### 6.2 Buenas prácticas transversales", "",
               "Prácticas que se repiten en los controles propuestos para casos de abuso distintos. El número indica en cuántos casos aparece (búsqueda por palabras clave sobre el texto de los controles; es una aproximación).", "",
               "| Buena práctica | Casos en que se propone |", "|---|---|"]
    textos = {c["id"]: " ".join(k["control"] for k in c["controles"]) for c in CASOS}
    filas = []
    for nombre, patron in PRACTICAS:
        n = sum(1 for t in textos.values() if re.search(patron, t, re.I))
        filas.append((n, nombre))
    for n, nombre in sorted(filas, reverse=True):
        lineas.append(f"| {nombre} | {n} |")
    resp = collections.Counter((k["tipo"], k["responsable"]) for c in CASOS for k in c["controles"])
    lineas += ["", "### 6.3 Quién implementa los controles", "",
               "| Tipo | Ecommerce | Proveedor logístico | Pasarela de pago | Total |", "|---|---|---|---|---|"]
    for t in ["preventivo", "detectivo", "correctivo"]:
        fila = [resp[(t, r)] for r in RESP]
        lineas.append(f"| {t.capitalize()} | " + " | ".join(map(str, fila)) + f" | {sum(fila)} |")
    lineas += ["", "Una parte de los controles depende del **proveedor logístico** (app del repartidor, escaneos, credenciales de la integración). Deben quedar en el contrato como requisitos de seguridad con evidencia verificable, porque el ecommerce no los opera."]
    return "\n".join(lineas)


def seccion_riesgos():
    lineas = ["## 7. Principales riesgos", "",
              "Agrupación de los casos de abuso por la debilidad de fondo que explotan, ordenada por número de casos de riesgo alto.", "",
              "| # | Riesgo | Casos | Riesgo alto | Internos / externos | Casos de uso |", "|---|---|---|---|---|---|"]
    rk = ranking_riesgos()
    for i, (r, s) in enumerate(rk, 1):
        lineas.append(f"| {i} | **{r}** {RIESGOS[r]['nombre']} | {s['n']} | {s['altos']} | {s['internos']} / {s['externos']} | {', '.join(s['ucs'])} |")
    for r, s in rk:
        lineas += ["", f"### {r} · {RIESGOS[r]['nombre']}", "", RIESGOS[r]["descripcion"], "",
                   f"- **Dónde:** {RIESGOS[r]['donde']}.",
                   f"- **Casos:** {', '.join(ancla(c) for c in s['casos'])}.",
                   f"- **Controles prioritarios:** ver 6.1."]
    mapa = collections.Counter((c["riesgo"]["probabilidad"], c["riesgo"]["impacto"]) for c in CASOS if c.get("riesgo"))
    lineas += ["", "### Mapa de calor (probabilidad × impacto)", "",
               "| Probabilidad \\ Impacto | 1 bajo | 2 medio | 3 alto |", "|---|---|---|---|"]
    for p in (3, 2, 1):
        lineas.append(f"| {p} {'alta' if p == 3 else 'media' if p == 2 else 'baja'} | " + " | ".join(str(mapa[(p, i)] or "·") for i in (1, 2, 3)) + " |")
    altos = sorted([c for c in CASOS if c["riesgo"]["probabilidad"] == 3 and c["riesgo"]["impacto"] == 3], key=orden)
    if altos:
        lineas += ["", "Casos en la celda de mayor riesgo (probabilidad 3 e impacto 3): " + ", ".join(f"{ancla(c)} ({esc(c['titulo'])})" for c in altos) + "."]
    return "\n".join(lineas)


def seccion_fuera():
    lineas = ["## 8. Casos fuera de alcance", "",
              "Pasaron la revisión automática, pero el analista no los consolidó en la memoria por los supuestos de alcance. Su detalle completo está en los resultados de [`evidencias/fase7/`](evidencias/fase7).", "",
              "| Caso | Caso de uso | STRIDE | Abuso | Motivo |", "|---|---|---|---|---|"]
    for c in FUERA:
        lineas.append(f"| {c['id']} | {c['caso_de_uso']} | {stride_txt(c)} | {esc(c['titulo'])} | {esc(c['fuera_de_alcance'])} |")
    return "\n".join(lineas)


def seccion_supuestos():
    lineas = ["## 9. Supuestos", "",
              "Los supuestos del modelo están en [`01-casos-de-uso-y-supuestos.md`](01-casos-de-uso-y-supuestos.md) §6 (S-01 a S-27) y en [`03-arquitectura.md`](03-arquitectura.md) §10 (S-28 a S-35). Además, para que cada caso de abuso sea posible, los agentes declararon **supuestos derivados**: condiciones del sistema que el caso da por ciertas, como la ausencia de un control. Se listan en el anexo B. En una revisión con el equipo del sistema, cada supuesto derivado se confirma o se descarta; si se descarta, el caso baja de riesgo o desaparece.", "",
              "Supuestos del análisis de riesgos:", "",
              "- La probabilidad y el impacto los estimó el agente de mitigación con la información del caso, sin datos de incidentes reales; sirven para priorizar, no como medición.",
              "- Los controles describen qué hacer; su costo y su factibilidad no se evaluaron.",
              "- Los productos voluminosos se tratan como de alto valor (S-23), lo que eleva el impacto de los abusos que terminan en pérdida del producto.",
              "- Los temas de riesgo agrupan casos por su debilidad de fondo; un caso se asigna a un solo tema, aunque toque varios."]
    return "\n".join(lineas)


def seccion_limitaciones():
    return """## 10. Limitaciones

- Los casos de abuso los generó un modelo de lenguaje con el contexto disponible. El revisor automático y el analista filtraron calidad y alcance, pero no se probaron contra un sistema real: son hipótesis de abuso a validar.
- Algunos casos parecidos aparecen en casos de uso distintos del mismo lote (por ejemplo, lectura de datos ajenos cambiando el identificador en AC-UC01-06, AC-UC03-02 y AC-UC07-06), porque la memoria solo los conoce después de consolidar el lote. Se conservaron porque afectan a objetos distintos; los temas de riesgo los agrupan.
- El esquema admite un solo actor por caso; las colusiones se registraron con un actor principal (ver ajustes del analista).
- Las referencias a CAPEC y OWASP son orientativas: el modelo las eligió entre el contexto recuperado."""


def anexo_a():
    lineas = ["## Anexo A · Detalle de los casos de abuso", "",
              "Ordenados por su ID en la memoria de largo plazo (`ltm_abusos`). Entre paréntesis, el ID original de la ejecución de WF-2.", ""]
    for uc in sorted({c["caso_de_uso"] for c in CASOS}):
        lineas += [f"### {uc_nombre(uc)}", ""]
        for c in sorted([x for x in CASOS if x["caso_de_uso"] == uc], key=orden):
            actor = f"{c['actor']['rol']} ({ACTOR[c['actor']['tipo']]})"
            if c.get("actores_adicionales"):
                actor += " + " + ", ".join(f"{a['rol']} ({ACTOR[a['tipo']]})" for a in c["actores_adicionales"])
            lineas += [f'<a id="{c["consolidado"].lower()}"></a>', f"#### {c['consolidado']} · {esc(c['titulo'])}", "",
                       f"- **ID de origen:** {c['id']} · **Ejecución:** {c['ejecucion']} · **Tema de riesgo:** {RIESGO_DE.get(c['id'], '—')}",
                       f"- **STRIDE:** {stride_txt(c)} — {STRIDE[c['stride']['principal']]}",
                       f"- **Actor:** {actor}",
                       f"- **Elementos del DFD:** {', '.join(c.get('elementos_dfd', [])) or '—'} · **Límites:** {', '.join(c.get('limites_confianza', [])) or '—'}",
                       "- **Precondiciones:**"] + [f"  - {p}" for p in c["precondiciones"]] + \
                      ["- **Cómo ocurre:**"] + [f"  {i}. {p}" for i, p in enumerate(c["como_ocurre"], 1)] + \
                      [f"- **Vector práctico:** {c['vector_practico']}",
                       f"- **Impacto:** {c['impacto']}",
                       f"- **Riesgo:** {riesgo_txt(c)}. {c['riesgo'].get('justificacion', '') if c.get('riesgo') else ''}",
                       "- **Controles:**"] + [f"  - *{k['tipo']}* ({RESP[k['responsable']]}): {k['control']}" for k in c["controles"]]
            refs = list(dict.fromkeys(c.get("referencias", []) + c.get("patrones_usados", [])))
            lineas.append(f"- **Referencias y patrones:** {', '.join(refs) or '—'}")
            if c.get("ajuste_analista"):
                lineas.append(f"- **Ajuste del analista:** {c['ajuste_analista']}")
            lineas.append("")
    return "\n".join(lineas)


def anexo_b():
    lineas = ["## Anexo B · Supuestos derivados declarados por los agentes", "",
              "Condiciones que cada caso de abuso da por ciertas. Las referencias a supuestos del modelo (S-xx) se omiten aquí porque ya están documentadas.", ""]
    for uc in sorted({c["caso_de_uso"] for c in CASOS}):
        filas = []
        for c in sorted([x for x in CASOS if x["caso_de_uso"] == uc], key=orden):
            for s in c.get("supuestos", []):
                if re.fullmatch(r"\s*S-\d+\s*", s):
                    continue
                filas.append(f"| {c['consolidado']} | {esc(s)} |")
        if filas:
            lineas += [f"### {uc_nombre(uc)}", "", "| Caso | Supuesto |", "|---|---|"] + filas + [""]
    return "\n".join(lineas)


def generar():
    ext_intro = ("Abusos de **clientes** (con su propia cuenta y su propio tráfico) y de **atacantes externos** "
                 "(con credenciales robadas, automatización o suplantación). El grupo final son ataques externos cuyo objetivo es la cuenta de un empleado.")
    int_intro = ("Abusos cometidos por **empleados del ecommerce** (backoffice, almacén, tienda) y por **personal del proveedor logístico** "
                 "(repartidores, centros de distribución), que en el modelo son internos de un tercero (S-15). En la mayoría el empleado usa permisos legítimos: "
                 "el problema es que el proceso no limita, no exige una segunda persona o no deja rastro.")
    partes = [
        "# Fase 8 · Informe de modelado de amenazas STRIDE",
        "",
        "Informe de los requisitos **C2** (modelado de amenazas con STRIDE), **C2a** (abusos de usuarios internos), **C2b** (abusos de usuarios externos), **C2c** (controles y buenas prácticas) y **C2d** (principales riesgos). Se genera con `scripts/generar_informe.py` a partir de [`../data/casos_de_abuso.json`](../data/casos_de_abuso.json), el catálogo de los casos de abuso producidos y consolidados en la Fase 7.",
        "",
        "**Contenido:** 1 Resumen · 2 Alcance y método · 3 Matriz STRIDE · 4 Abusos de usuarios internos · 5 Abusos de usuarios externos · 6 Controles · 7 Principales riesgos · 8 Fuera de alcance · 9 Supuestos · 10 Limitaciones · Anexo A Detalle de los casos · Anexo B Supuestos derivados",
        "",
        seccion_resumen(), seccion_metodo(), seccion_matriz(),
        seccion_grupo("## 4. Abusos de usuarios internos (empleados)", int_intro, grupo_interno, ORDEN_INTERNOS),
        seccion_grupo("## 5. Abusos de usuarios externos (clientes y atacantes)", ext_intro, grupo_externo, ORDEN_EXTERNOS),
        seccion_controles(), seccion_riesgos(), seccion_fuera(), seccion_supuestos(), seccion_limitaciones(),
        anexo_a(), anexo_b(),
    ]
    texto = "\n\n".join(p.strip() for p in partes if p.strip()) + "\n"
    (RAIZ / "docs" / "08-informe-stride.md").write_text(texto, encoding="utf-8")
    sin_tema = [c["id"] for c in CASOS if c["id"] not in RIESGO_DE]
    sobrantes = [i for i in RIESGO_DE if i not in {c["id"] for c in CASOS}]
    sin_grupo = [c["id"] for c in CASOS if not grupo_interno(c) and not grupo_externo(c)]
    print("líneas", texto.count("\n"), "| sin tema:", sin_tema, "| asignados fuera del catálogo:", sobrantes, "| sin grupo:", sin_grupo)


if __name__ == "__main__":
    generar()
