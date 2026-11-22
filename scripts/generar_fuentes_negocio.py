"""Genera data/flujos.json y data/supuestos.json a partir de los documentos de las Fases 1 a 3.

Fuentes:
  docs/02-diagrama.md            sección 5, catálogo de flujos F1–F30
  docs/01-casos-de-uso-y-supuestos.md  sección 6, supuestos S-01–S-27
  docs/03-arquitectura.md        sección 10, supuestos S-28–S-35
  data/casos_de_uso.json         casos de uso que citan cada supuesto

Uso:  python3 scripts/generar_fuentes_negocio.py
"""
import json
import re
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
DOCS = RAIZ / "docs"
DATA = RAIZ / "data"


def filas_tabla(texto: str, encabezado: str) -> list[list[str]]:
    """Devuelve las filas de la primera tabla Markdown que sigue al encabezado dado."""
    inicio = texto.index(encabezado)
    filas = []
    en_tabla = False
    for linea in texto[inicio:].splitlines()[1:]:
        if linea.startswith("|"):
            en_tabla = True
            celdas = [c.strip() for c in linea.strip().strip("|").split("|")]
            if set("".join(celdas)) <= set("-: "):
                continue
            filas.append(celdas)
        elif en_tabla and not linea.strip():
            if filas:
                break
        elif en_tabla:
            break
    return filas[1:]  # sin la fila de encabezados


def ids(texto: str, prefijo: str) -> list[str]:
    """Expande 'UC-01 a UC-07, UC-12' en la lista completa de IDs."""
    resultado = []
    for a, b in re.findall(rf"{prefijo}-(\d+) a {prefijo}-(\d+)", texto):
        resultado += [f"{prefijo}-{n:02d}" for n in range(int(a), int(b) + 1)]
    texto = re.sub(rf"{prefijo}-\d+ a {prefijo}-\d+", "", texto)
    resultado += [f"{prefijo}-{int(n):02d}" for n in re.findall(rf"{prefijo}-(\d+)", texto)]
    return sorted(set(resultado))


def limpiar(texto: str) -> str:
    return texto.replace("`", "").replace("**", "").strip()


def flujos() -> list[dict]:
    texto = (DOCS / "02-diagrama.md").read_text(encoding="utf-8")
    resultado = []
    for flujo, origen_destino, datos, casos, limite in filas_tabla(texto, "## 5. Catálogo de flujos"):
        origen, destino = [p.strip() for p in re.split(r"→|↔", origen_destino, maxsplit=1)]
        resultado.append({
            "id": flujo,
            "origen": origen,
            "destino": destino,
            "bidireccional": "↔" in origen_destino,
            "datos": limpiar(datos),
            "casos_de_uso": ids(casos, "UC"),
            "limite_confianza": None if limite in ("—", "") else limite,
            "reglas_negocio": sorted(set(re.findall(r"RN-\d", datos))),
        })
    return resultado


def supuestos() -> list[dict]:
    casos = json.loads((DATA / "casos_de_uso.json").read_text(encoding="utf-8"))["casos_de_uso"]
    por_supuesto: dict[str, list[str]] = {}
    for uc in casos:
        for s in uc.get("supuestos", []):
            por_supuesto.setdefault(s, []).append(uc["id"])

    resultado = []
    doc1 = (DOCS / "01-casos-de-uso-y-supuestos.md").read_text(encoding="utf-8")
    for encabezado in ("### 6.1", "### 6.2", "### 6.3"):
        for fila in filas_tabla(doc1, encabezado):
            sid, tema, supuesto, implicacion = fila[0], fila[1], fila[2], fila[3]
            resultado.append({"id": limpiar(sid), "tema": limpiar(tema), "supuesto": limpiar(supuesto),
                              "implicacion": limpiar(implicacion), "fase": "1-2"})
    doc3 = (DOCS / "03-arquitectura.md").read_text(encoding="utf-8")
    for sid, supuesto, implicacion in filas_tabla(doc3, "## 10. Supuestos de la arquitectura"):
        resultado.append({"id": sid, "tema": "Arquitectura de agentes", "supuesto": limpiar(supuesto),
                          "implicacion": limpiar(implicacion), "fase": "3"})
    for s in resultado:
        s["casos_de_uso"] = por_supuesto.get(s["id"], [])
    resultado.sort(key=lambda s: int(s["id"].split("-")[1]))
    return resultado


def escribir(nombre: str, contenido: dict) -> None:
    (DATA / nombre).write_text(json.dumps(contenido, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    f = flujos()
    s = supuestos()
    escribir("flujos.json", {"fuente": "docs/02-diagrama.md", "flujos": f})
    escribir("supuestos.json", {"fuente": "docs/01-casos-de-uso-y-supuestos.md, docs/03-arquitectura.md", "supuestos": s})
    print(f"flujos: {len(f)}  supuestos: {len(s)}")
