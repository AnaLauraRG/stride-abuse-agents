"""Prepara los fragmentos de la memoria de largo plazo que WF-1 carga en Supabase.

Salida:
  data/memoria/negocio.json   fragmentos para ltm_negocio
  data/memoria/amenazas.json  fragmentos para ltm_amenazas
  data/fuentes.json           registro de fuentes: repositorio, commit fijo, licencia y SHA-256

Las fuentes públicas se descargan de GitHub en un commit fijo, así el contenido es siempre
el mismo y se puede verificar. Requiere git y acceso a github.com.

Uso:  python3 scripts/preparar_memoria.py
"""
import hashlib
import html
import json
import re
import subprocess
import tempfile
from datetime import date
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
DATA = RAIZ / "data"
SALIDA = DATA / "memoria"
MAX_CARACTERES = 4000  # un fragmento más largo se divide por secciones

FUENTES_PUBLICAS = {
    "owasp-api": {
        "nombre": "OWASP API Security Top 10 2023",
        "repo": "https://github.com/OWASP/API-Security.git",
        "commit": "33cea37b2ffde3e2e62f6b5d79a029a22a846633",
        "ruta": "editions/2023/en",
        "licencia": "CC BY-SA 4.0, © OWASP Foundation",
    },
    "owasp-oat": {
        "nombre": "OWASP Automated Threats to Web Applications",
        "repo": "https://github.com/OWASP/www-project-automated-threats-to-web-applications.git",
        "commit": "14da2ff2ca1f430b8c9d8742396fbc433a7240e6",
        "ruta": "assets/oats/EN",
        "licencia": "CC BY-SA 4.0, © OWASP Foundation",
    },
    "capec": {
        "nombre": "MITRE CAPEC (formato STIX 2.1, repositorio mitre/cti)",
        "repo": "https://github.com/mitre/cti.git",
        "commit": "e79c7c53d13c08cc21ba3ad77d4f8f49bf64ff07",
        "ruta": "capec/2.1/attack-pattern",
        "licencia": "CAPEC Terms of Use, © The MITRE Corporation",
    },
}

# Categorías STRIDE asignadas a cada riesgo de OWASP (criterio del proyecto).
STRIDE_API = {
    "API1": ["I", "T", "E"], "API2": ["S"], "API3": ["I", "T", "E"], "API4": ["D"],
    "API5": ["E"], "API6": ["T", "D", "E"], "API7": ["I", "E"], "API8": ["I", "E"],
    "API9": ["I", "E"], "API10": ["T", "S"],
}
STRIDE_OAT = {
    "OAT-001": ["S"], "OAT-002": ["I", "E"], "OAT-003": ["T", "D"], "OAT-004": ["I"],
    "OAT-005": ["D"], "OAT-006": ["T", "E"], "OAT-007": ["S"], "OAT-008": ["S"],
    "OAT-009": ["S", "E"], "OAT-010": ["S"], "OAT-011": ["I"], "OAT-012": ["S", "T"],
    "OAT-013": ["T", "E"], "OAT-014": ["I"], "OAT-015": ["D"], "OAT-016": ["T"],
    "OAT-017": ["T"], "OAT-018": ["I"], "OAT-019": ["S", "E"], "OAT-020": ["I", "S"],
    "OAT-021": ["D"],
}
# Consecuencias de CAPEC → STRIDE.
STRIDE_CAPEC = {
    "Authentication": "S", "Integrity": "T", "Non-Repudiation": "R", "Accountability": "R",
    "Confidentiality": "I", "Availability": "D", "Access_Control": "E", "Authorization": "E",
}
CAPEC_DOMINIOS = {"Software", "Social Engineering"}
CAPEC_ABSTRACCIONES = {"Meta", "Standard"}


def sha256(texto: str) -> str:
    return hashlib.sha256(texto.encode("utf-8")).hexdigest()


def sin_html(texto: str) -> str:
    texto = re.sub(r"<[^>]+>", " ", texto or "")
    return re.sub(r"\s+", " ", html.unescape(texto)).strip()


def sin_markdown(texto: str) -> str:
    texto = re.sub(r"^---\n.*?\n---\n", "", texto, flags=re.S)       # front matter
    texto = re.sub(r"<[^>]+>", "", texto)                              # html
    texto = re.sub(r"!\[[^\]]*\]\([^)]*\)", "", texto)                 # imágenes
    texto = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", texto)             # enlaces
    texto = re.sub(r"\{%.*?%\}", "", texto)                            # liquid
    texto = re.sub(r"\n{3,}", "\n\n", texto)
    return texto.strip()


def fragmento(fuente: str, id_: str, content: str, **metadata) -> dict:
    content = content.strip()
    return {"content": content,
            "metadata": {"fuente": fuente, "id": id_, **metadata, "hash": sha256(content)}}


def dividir(fuente: str, id_: str, titulo: str, cuerpo: str, **metadata) -> list[dict]:
    """Un fragmento por elemento; si es muy largo, uno por sección con el título repetido."""
    completo = f"{titulo}\n\n{cuerpo}"
    if len(completo) <= MAX_CARACTERES:
        return [fragmento(fuente, id_, completo, **metadata)]
    partes, actual = [], ""
    for seccion in re.split(r"\n(?=#{2,3} )", cuerpo):
        if actual and len(actual) + len(seccion) > MAX_CARACTERES - len(titulo):
            partes.append(actual)
            actual = ""
        actual += ("\n" if actual else "") + seccion
    partes.append(actual)
    return [fragmento(fuente, id_, f"{titulo} (parte {i}/{len(partes)})\n\n{p[:MAX_CARACTERES]}",
                      parte=i, **metadata)
            for i, p in enumerate(partes, 1)]


# ------------------------------------------------------------------ negocio
def fragmentos_negocio() -> list[dict]:
    casos = json.loads((DATA / "casos_de_uso.json").read_text(encoding="utf-8"))
    flujos = json.loads((DATA / "flujos.json").read_text(encoding="utf-8"))["flujos"]
    supuestos = json.loads((DATA / "supuestos.json").read_text(encoding="utf-8"))["supuestos"]
    salida = []

    for rn, descripcion in casos["reglas_negocio"].items():
        usos = [uc["id"] for uc in casos["casos_de_uso"] if rn in uc.get("reglas_negocio", [])]
        texto = f"Regla de negocio {rn}: {descripcion}\nCasos de uso donde aplica: {', '.join(usos)}"
        salida.append(fragmento("reglas", rn, texto, tipo="regla", casos_de_uso=usos))

    for lc, descripcion in casos["limites_confianza"].items():
        usos = [uc["id"] for uc in casos["casos_de_uso"] if lc in uc.get("limites_confianza", [])]
        texto = f"Límite de confianza {lc}: {descripcion}\nCasos de uso que lo cruzan: {', '.join(usos)}"
        salida.append(fragmento("limites", lc, texto, tipo="limite", casos_de_uso=usos))

    for uc in casos["casos_de_uso"]:
        pasos = "\n".join(f"{i}. {p}" for i, p in enumerate(uc["flujo"], 1))
        texto = (f"Caso de uso {uc['id']}: {uc['nombre']}\n{uc['descripcion']}\n"
                 f"Actores: {', '.join(uc['actores'])}\n"
                 f"Componentes: {', '.join(uc['componentes'])}\n"
                 f"Flujo:\n{pasos}\n"
                 f"Datos: {', '.join(uc['datos'])}\n"
                 f"Reglas de negocio: {', '.join(uc['reglas_negocio']) or 'ninguna'}\n"
                 f"Límites de confianza: {', '.join(uc['limites_confianza']) or 'ninguno'}\n"
                 f"Supuestos: {', '.join(uc['supuestos'])}")
        salida.append(fragmento("casos_de_uso", uc["id"], texto, tipo="caso_de_uso",
                                casos_de_uso=[uc["id"]], componentes=uc["componentes"],
                                limites_confianza=uc["limites_confianza"]))

    for f in flujos:
        flecha = "↔" if f["bidireccional"] else "→"
        texto = (f"Flujo de datos {f['id']}: {f['origen']} {flecha} {f['destino']}\n"
                 f"Datos: {f['datos']}\n"
                 f"Casos de uso: {', '.join(f['casos_de_uso'])}\n"
                 f"Límite de confianza que cruza: {f['limite_confianza'] or 'ninguno'}")
        salida.append(fragmento("flujos", f["id"], texto, tipo="flujo", casos_de_uso=f["casos_de_uso"],
                                limite_confianza=f["limite_confianza"]))

    for s in supuestos:
        texto = (f"Supuesto {s['id']} ({s['tema']}): {s['supuesto']}\n"
                 f"Implicación para el análisis: {s['implicacion']}")
        salida.append(fragmento("supuestos", s["id"], texto, tipo="supuesto", casos_de_uso=s["casos_de_uso"]))
    return salida


# ------------------------------------------------------------------ amenazas
def secciones_curadas(archivo: Path, fuente: str) -> list[dict]:
    texto = archivo.read_text(encoding="utf-8")
    salida = []
    for bloque in re.split(r"\n(?=## )", texto)[1:]:
        titulo = bloque.splitlines()[0].lstrip("# ").strip()
        id_ = titulo.split(" · ")[0] if " · " in titulo else re.sub(r"\W+", "-", titulo).strip("-")
        stride = []
        m = re.search(r"\*\*STRIDE:\*\*\s*([SRTIDE, ]+)", bloque)
        if m:
            stride = [x.strip() for x in m.group(1).split(",") if x.strip()]
        elif id_.startswith("STRIDE-"):
            stride = [id_.split("-")[1]]
        salida.append(fragmento(fuente, id_, bloque.replace("**", "").strip(), nombre=titulo, stride=stride))
    return salida


def owasp_api(ruta: Path) -> list[dict]:
    salida = []
    for archivo in sorted(ruta.glob("0xa*.md")):
        texto = sin_markdown(archivo.read_text(encoding="utf-8"))
        titulo = texto.splitlines()[0].lstrip("# ").strip()          # "API1:2023 Broken Object ..."
        cuerpo = "\n".join(texto.splitlines()[1:]).strip()
        cuerpo = re.sub(r"^## References.*", "", cuerpo, flags=re.S | re.M).strip()
        id_ = titulo.split(" ")[0]                                     # "API1:2023"
        clave = id_.split(":")[0]
        salida += dividir("owasp-api", id_, f"OWASP API Security Top 10 · {titulo}", cuerpo,
                          nombre=titulo, stride=STRIDE_API.get(clave, []),
                          url="https://owasp.org/API-Security/editions/2023/en/0x11-t10/")
    return salida


def owasp_oat(ruta: Path) -> list[dict]:
    salida = []
    for archivo in sorted(ruta.glob("OAT-*.md")):
        if archivo.name == "OAT-003_Ad_Fraud.md":   # sustituido por OAT-003 Cost-Inflation Fraud
            continue
        texto = sin_markdown(archivo.read_text(encoding="utf-8"))
        texto = re.sub(r"Return to OWASP Automated Threats.*", "", texto, flags=re.S)
        texto = re.sub(r"^.*?(?=## Definition)", "", texto, flags=re.S)
        texto = re.sub(r"### Indicative Diagram\s*", "", texto)
        id_ = archivo.name[:7]
        nombre = archivo.stem[8:].replace("_", " ")
        salida += dividir("owasp-oat", id_, f"OWASP Automated Threat {id_} · {nombre}", texto,
                          nombre=nombre, stride=STRIDE_OAT.get(id_, []),
                          url=f"https://owasp.org/www-project-automated-threats-to-web-applications/assets/oats/EN/{archivo.stem}")
    return salida


def capec(ruta: Path) -> list[dict]:
    salida = []
    for archivo in sorted(ruta.glob("*.json")):
        o = json.loads(archivo.read_text(encoding="utf-8"))["objects"][0]
        if o.get("revoked") or o.get("x_capec_status") == "Deprecated":
            continue
        if o.get("x_capec_abstraction") not in CAPEC_ABSTRACCIONES:
            continue
        if not CAPEC_DOMINIOS & set(o.get("x_capec_domains", [])):
            continue
        ref = next(r for r in o["external_references"] if r.get("source_name") == "capec")
        cwes = [r["external_id"] for r in o["external_references"] if r.get("source_name") == "cwe"]
        consecuencias = o.get("x_capec_consequences", {})
        stride = sorted({STRIDE_CAPEC[k] for k in consecuencias if k in STRIDE_CAPEC}, key="STRIDE".index)
        partes = [f"MITRE CAPEC · {ref['external_id']} {o['name']} ({o['x_capec_abstraction']})",
                  f"Descripción: {sin_html(o.get('description'))}"]
        if o.get("x_capec_prerequisites"):
            partes.append("Prerrequisitos: " + " ".join(sin_html(p) for p in o["x_capec_prerequisites"]))
        if o.get("x_capec_example_instances"):
            partes.append("Ejemplo: " + sin_html(o["x_capec_example_instances"][0])[:900])
        if consecuencias:
            partes.append("Consecuencias: " + "; ".join(f"{k}: {', '.join(v)}" for k, v in consecuencias.items()))
        if cwes:
            partes.append("CWE relacionados: " + ", ".join(cwes[:8]))
        content = "\n".join(partes)[:MAX_CARACTERES]
        salida.append(fragmento("capec", ref["external_id"], content, nombre=o["name"], stride=stride,
                                abstraccion=o["x_capec_abstraction"], url=ref.get("url")))
    salida.sort(key=lambda f: int(f["metadata"]["id"].split("-")[1]))
    return salida


def descargar(destino: Path) -> dict[str, Path]:
    rutas = {}
    for clave, f in FUENTES_PUBLICAS.items():
        carpeta = destino / clave
        subprocess.run(["git", "init", "-q", str(carpeta)], check=True)
        subprocess.run(["git", "-C", str(carpeta), "remote", "add", "origin", f["repo"]], check=True)
        subprocess.run(["git", "-C", str(carpeta), "sparse-checkout", "set", f["ruta"]], check=True)
        subprocess.run(["git", "-C", str(carpeta), "fetch", "-q", "--depth", "1", "--filter=blob:none",
                        "origin", f["commit"]], check=True)
        subprocess.run(["git", "-C", str(carpeta), "checkout", "-q", "FETCH_HEAD"], check=True)
        rutas[clave] = carpeta / f["ruta"]
    return rutas


def escribir(nombre: str, tabla: str, fragmentos: list[dict]) -> str:
    SALIDA.mkdir(parents=True, exist_ok=True)
    contenido = {"tabla": tabla, "total": len(fragmentos), "fragmentos": fragmentos}
    texto = json.dumps(contenido, ensure_ascii=False, indent=1) + "\n"
    (SALIDA / nombre).write_text(texto, encoding="utf-8")
    return sha256(texto)


if __name__ == "__main__":
    negocio = fragmentos_negocio()
    amenazas = (secciones_curadas(DATA / "conocimiento" / "stride.md", "stride")
                + secciones_curadas(DATA / "conocimiento" / "fraude-ecommerce.md", "fraude"))
    with tempfile.TemporaryDirectory() as tmp:
        rutas = descargar(Path(tmp))
        amenazas += owasp_api(rutas["owasp-api"]) + owasp_oat(rutas["owasp-oat"]) + capec(rutas["capec"])

    hash_negocio = escribir("negocio.json", "ltm_negocio", negocio)
    hash_amenazas = escribir("amenazas.json", "ltm_amenazas", amenazas)

    conteo = {}
    for f in negocio + amenazas:
        conteo[f["metadata"]["fuente"]] = conteo.get(f["metadata"]["fuente"], 0) + 1
    registro = {
        "generado": date.today().isoformat(),
        "publicas": FUENTES_PUBLICAS,
        "propias": {
            "casos_de_uso": "data/casos_de_uso.json", "flujos": "data/flujos.json",
            "supuestos": "data/supuestos.json", "stride": "data/conocimiento/stride.md",
            "fraude": "data/conocimiento/fraude-ecommerce.md",
        },
        "fragmentos_por_fuente": conteo,
        "archivos": {
            "data/memoria/negocio.json": {"tabla": "ltm_negocio", "fragmentos": len(negocio), "sha256": hash_negocio},
            "data/memoria/amenazas.json": {"tabla": "ltm_amenazas", "fragmentos": len(amenazas), "sha256": hash_amenazas},
        },
    }
    (DATA / "fuentes.json").write_text(json.dumps(registro, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(conteo, indent=1))
    print(f"negocio: {len(negocio)}  amenazas: {len(amenazas)}")
