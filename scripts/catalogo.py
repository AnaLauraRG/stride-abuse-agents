"""Catálogo consolidado de casos de abuso (Fase 8).

Une los resultados de WF-2 guardados como evidencia (docs/evidencias/fase7/*.json),
asigna el ID AV-NNNN con el que WF-3 consolidó cada caso en ltm_abusos, marca los casos
fuera de alcance y aplica los ajustes del analista. Lo usan generar_informe.py y el PDF final.

Uso:  python3 scripts/catalogo.py   →   data/casos_de_abuso.json
"""
import copy
import json
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
EVID = RAIZ / "docs" / "evidencias" / "fase7"

# Ejecuciones de WF-2 en el orden en que se consolidaron con WF-3.
EJECUCIONES = [
    ("UC-11", "02-resultado-uc11.json"),
    ("UC-12", "05-resultado-uc12.json"),
    ("Lote 1", "07-resultado-lote1-uc01-uc05.json"),
    ("Lote 2", "09-resultado-lote2-uc06-uc10.json"),
    ("Lote 3", "11-resultado-lote3-uc13-uc16.json"),
]

# Casos que el analista no consolidó por quedar fuera del alcance declarado.
FUERA_DE_ALCANCE = {
    "AC-UC03-04": "S-22: denegación de servicio volumétrica (saturación del endpoint de cotización).",
    "AC-UC05-07": "S-22: denegación de servicio volumétrica (cotizaciones masivas).",
    "AC-UC05-08": "S-24: interceptación en la red interna (suplantación ARP de APIs internas).",
    "AC-UC10-06": "S-22: denegación de servicio volumétrica (ráfaga de eventos).",
    "AC-UC14-07": "S-22: denegación de servicio volumétrica (búsquedas masivas en clients-api).",
    "AC-UC16-07": "S-22: denegación de servicio volumétrica (cambios masivos de estado).",
}

# Ajustes del analista sobre la salida de los agentes (se documentan en el informe).
AJUSTES = {
    "AC-UC11-03": "Actor combinado: el esquema admite un solo actor; se agrega el repartidor (interno de tercero) como participante.",
    "AC-UC12-06": "Referencia: OWASP OAT-012 (Cashing Out) se sustituye por OAT-021 (Denial of Inventory), que describe el abuso.",
    "AC-UC11-01": "Responsable: la atestación del dispositivo se implementa en la app del repartidor, que es del proveedor logístico.",
    "AC-UC12-04": "Responsable: la revisión del reclamo la hace soporte del ecommerce, no la pasarela.",
}


def aplicar_ajustes(c):
    if c["id"] == "AC-UC11-03":
        c["actores_adicionales"] = [{"tipo": "interno_tercero", "rol": "Repartidor"}]
    if c["id"] == "AC-UC12-06":
        c["referencias"] = ["OWASP OAT-021 Denial of Inventory" if "OAT-012" in r else r for r in c.get("referencias", [])]
    if c["id"] == "AC-UC11-01":
        for k in c["controles"]:
            if "Play Integrity" in k["control"]:
                k["responsable"] = "proveedor_logistico"
    if c["id"] == "AC-UC12-04":
        for k in c["controles"]:
            if k["tipo"] == "correctivo" and k["responsable"] == "pasarela_pago":
                k["responsable"] = "ecommerce"
    if c["id"] in AJUSTES:
        c["ajuste_analista"] = AJUSTES[c["id"]]


def limpiar_pasos(pasos):
    import re
    return [re.sub(r"^\s*\d+[\.\)]\s*", "", p).strip() for p in pasos]


def construir():
    casos, av = [], 0
    for nombre, archivo in EJECUCIONES:
        r = json.loads((EVID / archivo).read_text(encoding="utf-8"))
        for u in r["casos_de_uso"]:
            for c in u["casos_de_abuso"]:
                c = copy.deepcopy(c)
                c["ejecucion"] = nombre
                c["run_id"] = r["run_id"]
                c["como_ocurre"] = limpiar_pasos(c["como_ocurre"])
                if c["id"] in FUERA_DE_ALCANCE:
                    c["consolidado"] = None
                    c["fuera_de_alcance"] = FUERA_DE_ALCANCE[c["id"]]
                else:
                    av += 1                       # WF-3 numera en el orden del resultado
                    c["consolidado"] = f"AV-{av:04d}"
                aplicar_ajustes(c)
                casos.append(c)
    return casos


if __name__ == "__main__":
    casos = construir()
    salida = RAIZ / "data" / "casos_de_abuso.json"
    salida.write_text(json.dumps({"total": len(casos),
                                  "consolidados": sum(1 for c in casos if c["consolidado"]),
                                  "fuera_de_alcance": sum(1 for c in casos if not c["consolidado"]),
                                  "casos": casos}, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(len(casos), "casos;", sum(1 for c in casos if c["consolidado"]), "consolidados; último",
          max(c["consolidado"] for c in casos if c["consolidado"]))
