"""Genera docs/Entrega_Reto2_STRIDE_Abuse_Agents.pdf a partir de los documentos del repositorio.

Markdown → HTML (pandoc, con índice) → PDF (Chrome sin interfaz, con marcadores) → números de página (pypdf + reportlab).
Requiere: pandoc, google-chrome (o chromium), y los paquetes de Python pypdf y reportlab.

Uso:  python3 scripts/generar_pdf.py
"""
import datetime
import io
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

from pypdf import PdfReader, PdfWriter
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

RAIZ = Path(__file__).resolve().parent.parent
TMP = None
SALIDA = RAIZ / "docs" / "Entrega_Reto2_STRIDE_Abuse_Agents.pdf"

DOCUMENTOS = [
    ("README.md", "resumen"),
    ("REQUISITOS.md", "requisitos"),
    ("docs/01-casos-de-uso-y-supuestos.md", "01-casos-de-uso-y-supuestos"),
    ("docs/02-diagrama.md", "02-diagrama"),
    ("docs/03-arquitectura.md", "03-arquitectura"),
    ("docs/04-infraestructura.md", "04-infraestructura"),
    ("docs/05-memoria.md", "05-memoria"),
    ("docs/06-agentes.md", "06-agentes"),
    ("prompts/README.md", "prompts"),
    ("docs/07-ejecucion.md", "07-ejecucion"),
    ("docs/08-informe-stride.md", "08-informe-stride"),
]

EVIDENCIAS = [
    ("docs/evidencias/fase6/01-ltm-contexto-cuotas-uc11.png", "Recuperación de contexto con cuotas por fuente para UC-11 (ltm_contexto, datos reales)"),
    ("docs/evidencias/fase7/01-wf2-uc11-ejecucion.png", "WF-2 ejecutado con Claude real sobre UC-11"),
    ("docs/evidencias/fase7/03-wf3-consolidacion-uc11.png", "WF-3: consolidación de los casos de UC-11 en ltm_abusos"),
    ("docs/evidencias/fase7/04-ltm-abusos-patrones.png", "Patrones abstractos AV-0001 a AV-0004 en la memoria de largo plazo"),
    ("docs/evidencias/fase7/06-wf2-lote1-ejecucion.png", "WF-2, lote 1 (UC-01 a UC-05): 28 casos aprobados"),
    ("docs/evidencias/fase7/08-wf2-lote2-ejecucion.png", "WF-2, lote 2 (UC-06 a UC-10): 27 casos aprobados"),
    ("docs/evidencias/fase7/10-wf2-lote3-ejecucion.png", "WF-2, lote 3 (UC-13 a UC-16): 25 casos aprobados"),
    ("docs/evidencias/fase7/12-wf3-consolidacion-lote3.png", "WF-3: consolidación del lote 3 (AV-0062 en adelante)"),
]

CSS = """
@page { size: A4; margin: 18mm 16mm 20mm 16mm; }
html { font-family: 'DejaVu Sans', 'Liberation Sans', sans-serif; font-size: 9.6pt; color: #1d2327; line-height: 1.42; }
body { margin: 0; }
h1 { font-size: 19pt; color: #0b3d62; border-bottom: 2px solid #0b3d62; padding-bottom: 4px; page-break-before: always; margin-top: 0; }
h2 { font-size: 14pt; color: #0b3d62; margin-top: 18px; page-break-after: avoid; }
h3 { font-size: 11.5pt; color: #1f5f8b; margin-top: 14px; page-break-after: avoid; }
h4 { font-size: 10.2pt; color: #2b2b2b; margin: 12px 0 4px; page-break-after: avoid; }
p, li { orphans: 3; widows: 3; }
a { color: #1f5f8b; text-decoration: none; }
table { border-collapse: collapse; width: 100%; margin: 8px 0 12px; font-size: 8.3pt; page-break-inside: auto; }
tr { page-break-inside: avoid; }
th { background: #e8f0f6; text-align: left; }
th, td { border: 1px solid #c9d3db; padding: 3px 5px; vertical-align: top; }
code { font-family: 'Liberation Mono', 'DejaVu Sans Mono', monospace; font-size: 8.3pt; background: #f2f4f5; padding: 0 2px; border-radius: 2px; }
pre { background: #f6f8fa; border: 1px solid #dde3e8; padding: 7px; font-size: 7.8pt; white-space: pre-wrap; word-break: break-word; page-break-inside: avoid; }
pre code { background: none; padding: 0; }
img { max-width: 100%; max-height: 225mm; display: block; margin: 6px auto; page-break-inside: avoid; }
figure { margin: 8px 0; page-break-inside: avoid; }
figcaption { font-size: 8.3pt; color: #555; text-align: center; }
blockquote { border-left: 3px solid #9bb9cf; margin: 8px 0; padding: 2px 10px; color: #444; background: #f5f9fc; }
nav#TOC { page-break-before: always; }
nav#TOC > ul > li { margin-top: 5px; font-weight: bold; }
nav#TOC ul ul { font-weight: normal; }
nav#TOC ul { list-style: none; padding-left: 14px; }
.portada { height: 245mm; display: flex; flex-direction: column; justify-content: center; }
.portada h1 { page-break-before: avoid; border: none; font-size: 30pt; margin-bottom: 4px; }
.portada .sub { font-size: 14pt; color: #1f5f8b; margin: 0 0 26px; }
.portada table { width: auto; font-size: 10pt; }
.portada td { border: none; padding: 3px 14px 3px 0; }
"""

FILTRO_LUA = r"""
local docs = {}
function Link(el)
  local t = el.target
  if t:match('^https?://') or t:match('^#') or t:match('^mailto:') then return el end
  local base = t:match('([%w%-_]+)%.md')
  if base and DOCS[base] then
    el.target = '#doc-' .. DOCS[base]
    return el
  end
  return el.content
end
"""


OPTIMIZADAS = {}


def optimizar(src: str, tmp: Path) -> str:
    """Copia reducida de la imagen para el PDF: capturas en JPEG, diagramas en PNG de menor resolución."""
    from PIL import Image
    if src in OPTIMIZADAS:
        return OPTIMIZADAS[src]
    origen = (RAIZ / src).resolve()
    im = Image.open(origen)
    es_diagrama = "diagrams/" in src
    maximo = 2200 if es_diagrama else 1600
    if im.width > maximo:
        im = im.resize((maximo, int(im.height * maximo / im.width)), Image.LANCZOS)
    destino = tmp / "img" / (src.replace("/", "_").rsplit(".", 1)[0] + (".png" if es_diagrama else ".jpg"))
    destino.parent.mkdir(exist_ok=True)
    if es_diagrama:
        im.save(destino, optimize=True)
    else:
        im.convert("RGB").save(destino, quality=82, optimize=True)
    OPTIMIZADAS[src] = destino.as_posix()
    return OPTIMIZADAS[src]


def preparar_markdown(ruta: Path, ident: str) -> str:
    texto = ruta.read_text(encoding="utf-8")
    if ruta.name == "README.md" and ruta.parent == RAIZ:
        texto = re.sub(r"^📄 \*\*Documento de entrega:\*\*.*\n", "", texto, flags=re.M)
        texto = texto.replace("# STRIDE Abuse Agents", "# Resumen de la entrega", 1)
    # Las imágenes se resuelven desde la carpeta del documento.
    carpeta = ruta.parent.relative_to(RAIZ)
    def img(m):
        alt, src = m.group(1), m.group(2)
        if src.startswith("http"):
            return m.group(0)
        return f"![{alt}]({optimizar((carpeta / src).as_posix(), TMP)})"
    texto = re.sub(r"!\[([^\]]*)\]\(([^)]+)\)", img, texto)
    # Sin emojis: la fuente de emojis a color multiplica el tamaño del PDF.
    for emoji, simbolo in {"✅": "✔", "🟨": "◐", "⬜": "☐", "📄 ": "", "⚠️": "⚠"}.items():
        texto = texto.replace(emoji, simbolo)
    # Ancla al inicio de cada documento para los enlaces entre documentos.
    texto = re.sub(r"^# (.+)$", lambda m: f"# {m.group(1)} {{#doc-{ident}}}", texto, count=1, flags=re.M)
    return texto


def portada() -> str:
    hoy = datetime.date.today().strftime("%d/%m/%Y")
    return f"""<div class="portada">
<h1>STRIDE Abuse Agents</h1>
<p class="sub">Reto 2 · Challenge Cybersecurity Engineer (BISO)<br/>Modelado de amenazas STRIDE con una arquitectura de agentes de IA con memoria de largo plazo</p>
<table>
<tr><td><b>Caso</b></td><td>Flujo de venta de productos voluminosos en un ecommerce</td></tr>
<tr><td><b>Alcance</b></td><td>16 casos de uso · 30 flujos de datos · 6 límites de confianza</td></tr>
<tr><td><b>Resultado</b></td><td>84 casos de abuso en alcance · 397 controles · 8 riesgos principales</td></tr>
<tr><td><b>Implementación</b></td><td>n8n · Supabase + pgvector · Claude (Anthropic) · Ollama bge-m3</td></tr>
<tr><td><b>Repositorio</b></td><td>github.com/AnaLauraRG/stride-abuse-agents</td></tr>
<tr><td><b>Fecha</b></td><td>{hoy}</td></tr>
</table>
</div>
"""


def evidencias_md() -> str:
    partes = ["# Anexo · Evidencias de ejecución {#doc-evidencias}", "",
              "Capturas de las ejecuciones reales. Las de la infraestructura (Fase 4) y la carga de la memoria (Fase 5) están en sus capítulos; los resultados completos en JSON están en `docs/evidencias/fase7/` del repositorio.", ""]
    for ruta, pie in EVIDENCIAS:
        partes += [f"![{pie}]({optimizar(ruta, TMP)})", "", f"*{pie}.*", ""]
    return "\n".join(partes)


def numerar(pdf: Path) -> None:
    lector = PdfReader(str(pdf))
    escritor = PdfWriter(clone_from=lector)
    total = len(escritor.pages)
    for i, pagina in enumerate(escritor.pages):
        if i == 0:
            continue
        buf = io.BytesIO()
        ancho = float(pagina.mediabox.width)
        c = canvas.Canvas(buf, pagesize=(ancho, float(pagina.mediabox.height)))
        c.setFont("Helvetica", 7.5)
        c.setFillGray(0.45)
        c.drawString(16 * 2.835, 9 * 2.835, "STRIDE Abuse Agents · Reto 2")
        c.drawRightString(ancho - 16 * 2.835, 9 * 2.835, f"{i + 1} / {total}")
        c.save()
        buf.seek(0)
        pagina.merge_page(PdfReader(buf).pages[0])
        pagina.compress_content_streams()
    escritor.compress_identical_objects(remove_duplicates=True, remove_unreferenced=True)
    with open(pdf, "wb") as f:
        escritor.write(f)


def main():
    chrome = shutil.which("google-chrome") or shutil.which("chromium") or shutil.which("chromium-browser")
    if not chrome or not shutil.which("pandoc"):
        raise SystemExit("Se requieren pandoc y google-chrome/chromium")
    global TMP
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        TMP = tmp
        mapa = {Path(r).stem if Path(r).name != "README.md" else ("prompts" if r.startswith("prompts") else "README"): i
                for r, i in DOCUMENTOS}
        mapa.update({"REQUISITOS": "requisitos"})
        lua = "DOCS = {" + ", ".join(f'["{k}"]="{v}"' for k, v in mapa.items()) + "}\n" + FILTRO_LUA
        (tmp / "enlaces.lua").write_text(lua, encoding="utf-8")
        (tmp / "estilo.css").write_text(CSS, encoding="utf-8")
        (tmp / "portada.html").write_text(portada(), encoding="utf-8")
        md = "\n\n".join(preparar_markdown(RAIZ / r, i) for r, i in DOCUMENTOS) + "\n\n" + evidencias_md()
        (tmp / "entrega.md").write_text(md, encoding="utf-8")
        html = tmp / "entrega.html"
        subprocess.run(["pandoc", str(tmp / "entrega.md"), "-f", "gfm+attributes+raw_html", "-t", "html5", "-s",
                        "--toc", "--toc-depth=2", "-M", "title=STRIDE Abuse Agents · Reto 2", "-M", "toc-title=Índice",
                        "-V", "lang=es", "--css", str(tmp / "estilo.css"), "--embed-resources",
                        "--resource-path", str(RAIZ), "--lua-filter", str(tmp / "enlaces.lua"),
                        "-B", str(tmp / "portada.html"), "-o", str(html)], check=True, cwd=RAIZ)
        # El título de pandoc se oculta: la portada ya lo muestra.
        contenido = html.read_text(encoding="utf-8")
        contenido = re.sub(r'<header id="title-block-header">.*?</header>', "", contenido, flags=re.S)
        html.write_text(contenido, encoding="utf-8")
        pdf = tmp / "entrega.pdf"
        subprocess.run([chrome, "--headless=new", "--no-sandbox", "--disable-gpu", "--no-pdf-header-footer",
                        "--generate-pdf-document-outline", f"--print-to-pdf={pdf}", html.as_uri()],
                       check=True, capture_output=True, timeout=600)
        print("Chrome:", f"{pdf.stat().st_size / 1e6:.1f} MB")
        numerar(pdf)
        shutil.copy(pdf, SALIDA)
    print("PDF:", SALIDA, f"({SALIDA.stat().st_size / 1e6:.1f} MB,", len(PdfReader(str(SALIDA)).pages), "páginas)")


if __name__ == "__main__":
    main()
