# STRIDE Abuse Agents

Reto 2 del *Challenge Cybersecurity Engineer (BISO)*: modelado de amenazas STRIDE del flujo de venta de productos voluminosos en un ecommerce, con una **arquitectura de agentes de IA con memoria de largo plazo** que genera, revisa y mitiga casos de abuso. La arquitectura está implementada (n8n + Supabase + Claude + Ollama) y se ejecutó sobre los 16 casos de uso del flujo.

📄 **Documento de entrega:** [`docs/Entrega_Reto2_STRIDE_Abuse_Agents.pdf`](docs/Entrega_Reto2_STRIDE_Abuse_Agents.pdf). Reúne todo lo de este repositorio en un solo archivo (171 páginas, con índice navegable: cada título lleva a su página y el enlace «Índice» del pie regresa).

## Resultados

| | |
|---|---|
| Casos de uso analizados | 16, sobre un diagrama de flujo de datos con 30 flujos y 6 límites de confianza |
| Casos de abuso generados | 90, todos aprobados por el agente revisor; **84 en alcance** tras la revisión del analista |
| Cobertura STRIDE | Las 6 categorías: T 28 · E 15 · S 14 · R 11 · I 11 · D 5 (casos en alcance) |
| Actores | 34 casos de empleados (propios y del proveedor logístico) · 51 de clientes y atacantes externos |
| Memoria de largo plazo | 84 casos validados con patrón abstracto (AV-0001 a AV-0084); 38 de los 90 casos se construyeron a partir de patrones de ejecuciones anteriores |
| Controles propuestos | 397, preventivos, detectivos y correctivos, con responsable |
| Riesgos principales | 8, priorizados; los tres primeros son privilegios internos sin segregación, evidencia que no prueba los hechos físicos y exposición de datos |
| Costo de la ejecución | ≈ 4.4 USD en llamadas a Claude (estimado con el precio publicado) |

## Arquitectura

![Arquitectura](diagrams/arquitectura.png)

- **Fuentes de datos:** los casos de uso, flujos y supuestos propios, más conocimiento de amenazas (MITRE CAPEC, OWASP API Top 10, OWASP Automated Threats y patrones de fraude curados), descargado en commits fijos.
- **Memoria:**
  - *Largo plazo* en Supabase + pgvector, en tres segmentos: negocio, amenazas y casos de abuso validados.
  - *Corto plazo:* un registro por ejecución y por paso.
- **Capa agéntica (n8n):**
  - Un orquestador determinista y un recuperador con cuotas por fuente.
  - Agentes con Claude: generador (prompt público de 96 palabras), revisor, mitigación y abstracción.
  - El analista aprueba qué entra a la memoria.

## Qué hace cada flujo y quién lo ejecuta

| Flujo | Qué hace | Quién lo ejecuta |
|---|---|---|
| **WF-1 · Ingesta** | Carga la memoria de largo plazo con el negocio y el conocimiento de amenazas | El analista, al instalar y cuando cambian las fuentes |
| **WF-2 · Generación** | Genera, revisa y mitiga casos de abuso para 1 a 5 casos de uso | El analista, cada vez que analiza casos de uso |
| **WF-3 · Consolidación** | Guarda en la memoria los casos que el analista aprueba | El analista, después de revisar WF-2: es la aprobación humana |

Los agentes (generador, revisor, mitigación y abstracción) no tienen herramientas ni acceso a la base: solo reciben texto y devuelven JSON validado. Solo WF-3 escribe en la memoria de casos validados, y Supabase solo acepta la clave secreta guardada en n8n. El detalle de cada agente y la matriz de permisos están en [`docs/09-componentes-y-permisos.md`](docs/09-componentes-y-permisos.md).

## Dónde está cada requisito

La matriz completa está en [`REQUISITOS.md`](REQUISITOS.md).

| Requisito del reto | Entregable |
|---|---|
| Diagrama del caso | [`docs/02-diagrama.md`](docs/02-diagrama.md) |
| Informe STRIDE: abusos de internos y externos, controles, riesgos principales | [`docs/08-informe-stride.md`](docs/08-informe-stride.md) |
| Arquitectura de agentes: memoria, memoria de largo plazo, fuentes de datos, capa agéntica | [`docs/03-arquitectura.md`](docs/03-arquitectura.md) |
| Implementación y evidencia de ejecución | [`docs/04`](docs/04-infraestructura.md) a [`docs/07`](docs/07-ejecucion.md), [`n8n/`](n8n), [`sql/`](sql), [`docs/evidencias/`](docs/evidencias) |
| Prompts de ≤100 palabras | [`prompts/README.md`](prompts/README.md) |
| Supuestos | [`docs/01`](docs/01-casos-de-uso-y-supuestos.md) §6, [`docs/03`](docs/03-arquitectura.md) §10, [`docs/08`](docs/08-informe-stride.md) §9 y anexo B |

## Documentos

| Archivo | Contenido |
|---|---|
| [`docs/01-casos-de-uso-y-supuestos.md`](docs/01-casos-de-uso-y-supuestos.md) | Actores, componentes, límites de confianza, 16 casos de uso y supuestos S-01 a S-27 |
| [`docs/02-diagrama.md`](docs/02-diagrama.md) | Diagrama de flujo de datos en tres vistas, zonas, límites de confianza y catálogo de flujos F1–F30 |
| [`docs/03-arquitectura.md`](docs/03-arquitectura.md) | Arquitectura de agentes: fuentes, memoria segmentada, capa agéntica, contratos, seguridad, costos y supuestos S-28 a S-35 |
| [`docs/04-infraestructura.md`](docs/04-infraestructura.md) | Instalación de n8n, Ollama y Supabase, credenciales, evidencias e incidencias |
| [`docs/05-memoria.md`](docs/05-memoria.md) | Fuentes de datos, fragmentos y flujo WF-1 de carga de la memoria de largo plazo |
| [`docs/06-agentes.md`](docs/06-agentes.md) | WF-2 (generación, revisión, mitigación) y WF-3 (consolidación en `ltm_abusos`) |
| [`docs/07-ejecucion.md`](docs/07-ejecucion.md) | Ejecución con Claude real: resultados, uso de la memoria, incidencias y evidencias |
| [`docs/08-informe-stride.md`](docs/08-informe-stride.md) | **Informe STRIDE** con el detalle de los 84 casos de abuso |
| [`docs/09-componentes-y-permisos.md`](docs/09-componentes-y-permisos.md) | Qué hace cada flujo y cada agente, quién lo ejecuta y esquema de permisos sobre la memoria |

## Paso a paso: descargar y ejecutar

Con estos pasos cualquier persona puede reproducir el sistema completo: la memoria de largo plazo, los agentes y la generación de casos de abuso. La infraestructura local (n8n y Ollama) corre en contenedores; la base de datos (Supabase) y el modelo de lenguaje (Claude) son servicios en la nube.

### 1. Requisitos

| Qué | Para qué | Notas |
|---|---|---|
| Git | Descargar el repositorio | `git --version` |
| Docker con Compose, o Podman | Ejecutar n8n y Ollama | `docker compose version`. Con Podman, activar antes su socket: `systemctl --user enable --now podman.socket` |
| Linux con unos 6 GB de RAM libres y 4 núcleos | El modelo de embeddings corre en CPU | Probado en una VM de Kali Linux en VirtualBox |
| Cuenta de Supabase | Memoria de largo y corto plazo | El plan gratuito alcanza |
| Clave de la API de Claude | Los agentes | Con un límite de gasto configurado; la ejecución completa de los 16 casos de uso costó ≈ 4.4 USD |
| Acceso al repositorio | Es privado | Hay que aceptar la invitación de GitHub |

### 2. Descargar el proyecto

GitHub pide autenticarse para clonar un repositorio privado. Usa **una** de estas opciones:

```bash
# A. HTTPS: como contraseña se usa un token personal de GitHub
#    (Settings → Developer settings → Personal access tokens), no la contraseña de la cuenta.
git clone https://github.com/AnaLauraRG/stride-abuse-agents.git

# B. SSH, si tienes una llave SSH registrada en GitHub
git clone git@github.com:AnaLauraRG/stride-abuse-agents.git

# C. GitHub CLI, después de `gh auth login`
gh repo clone AnaLauraRG/stride-abuse-agents

cd stride-abuse-agents
```

### 3. Levantar n8n y Ollama

```bash
cd infra
cp .env.example .env
sed -i "s/^N8N_ENCRYPTION_KEY=.*/N8N_ENCRYPTION_KEY=$(openssl rand -hex 32)/" .env
docker compose up -d
docker compose exec ollama ollama pull bge-m3
```

- `N8N_ENCRYPTION_KEY` cifra las credenciales que guardarás en n8n. El archivo `infra/.env` no se sube al repositorio; si lo pierdes, hay que volver a capturar las credenciales.
- n8n queda en `http://localhost:5678`, accesible solo desde la propia máquina. Ollama no publica puertos: n8n lo alcanza por la red interna.
- Para comprobar que el modelo de embeddings responde (debe imprimir `dimensiones: 1024`):

```bash
docker compose exec n8n node -e "fetch('http://ollama:11434/api/embed',{method:'POST',body:JSON.stringify({model:'bge-m3',input:'prueba'})}).then(r=>r.json()).then(j=>console.log('dimensiones:', j.embeddings[0].length))"
```

### 4. Crear la base de datos en Supabase

1. En [supabase.com](https://supabase.com), crea un proyecto nuevo (nombre, contraseña de la base y región) y espera a que termine de aprovisionarse.
2. Abre el **SQL Editor** y ejecuta, en este orden, el contenido de cada archivo (pégalo en una consulta nueva y pulsa *Run*):
   1. [`sql/001_esquema.sql`](sql/001_esquema.sql): tablas de memoria, índices vectoriales, funciones de búsqueda y permisos.
   2. [`sql/004_permisos_service_role.sql`](sql/004_permisos_service_role.sql): permisos explícitos para la clave secreta.
   3. [`sql/005_capa_agentica.sql`](sql/005_capa_agentica.sql): recuperación con cuotas por fuente.
3. Verifica con [`sql/002_verificacion.sql`](sql/002_verificacion.sql): deben existir las cinco tablas, con RLS activado.
4. Copia dos datos, que usarás en n8n:
   - **Project URL** (`https://<ref>.supabase.co`), en *Project Settings → Data API*.
   - **Clave secreta** (`sb_secret_…`), en *Project Settings → API Keys → Secret keys*. Trátala como una contraseña: no la pegues en documentos, capturas ni en el repositorio.

### 5. Crear la clave de la API de Claude

En [platform.claude.com](https://platform.claude.com), crea una clave en *API Keys* y configura un **límite de gasto mensual** en la sección de facturación. Igual que la de Supabase, la clave solo se escribe dentro de n8n.

### 6. Configurar n8n

1. Abre `http://localhost:5678` y crea la cuenta de propietario. Es local: no envía correos.
2. En **Credentials → Create credential**, crea dos credenciales:

   | Tipo | Campos |
   |---|---|
   | *Supabase API* | **Host:** la Project URL. **Service Role Secret:** la clave `sb_secret_…` |
   | *Anthropic* | **API Key:** la clave de Claude |

   Ollama no necesita credencial: los flujos lo llaman por la URL de la red interna.
3. Importa los tres flujos de [`n8n/`](n8n), uno por uno: crea un flujo nuevo (**Create workflow**), abre el menú **⋯** de arriba a la derecha y elige **Import from File**.
4. En cada flujo:
   - Abre el nodo **Configuración** y cambia el **valor** de `supabase_url` por tu Project URL. Edita solo la caja del valor (a la derecha); si escribes en la caja del nombre, el campo cambia de nombre y el flujo falla.
   - Abre los nodos que muestran un aviso de credencial y selecciona las que creaste.
   - Guarda (**Save**).

### 7. Cargar la memoria de largo plazo (WF-1)

Abre **WF-1 · Ingesta** y pulsa **Execute workflow**. Calcula los embeddings de 372 fragmentos con bge-m3 en CPU: tarda unos 15 minutos. El flujo está en verde cuando terminó.

Verifica con [`sql/003_verificar_memoria.sql`](sql/003_verificar_memoria.sql) en el SQL Editor: `ltm_negocio` debe tener 91 fragmentos y `ltm_amenazas` 281, ninguno sin vector.

### 8. Generar casos de abuso (WF-2)

1. Abre **WF-2 · Generación**, nodo **Entrada**, y escribe en el **valor** de `casos_de_uso` los casos de uso a analizar, de 1 a 5. Por ejemplo `["UC-11"]` o `["UC-01","UC-02","UC-03"]`. La lista de casos de uso (UC-01 a UC-16) está en [`docs/01-casos-de-uso-y-supuestos.md`](docs/01-casos-de-uso-y-supuestos.md).
2. Pulsa **Execute workflow**. Cada caso de uso tarda de 1 a 3 minutos.
3. El último nodo, **Resultado**, muestra el `run_id`, los casos de abuso con sus controles (en JSON y en Markdown) y los tokens usados. La misma información queda en la tabla `ejecuciones` de Supabase.

### 9. Consolidar en la memoria (WF-3)

Este paso es la **aprobación humana**: solo lo que apruebes entra a la memoria de largo plazo y se usa en las siguientes ejecuciones.

1. Abre **WF-3 · Consolidación**, nodo **Selección del analista**, y completa los valores:
   - `run_id`: el de la ejecución de WF-2.
   - `aprobar`: `"todos"`, o una lista como `["AC-UC11-01","AC-UC11-03"]`.
   - `aprobado_por`: tu nombre o rol.
2. Pulsa **Execute workflow**. Verifica en el SQL Editor:

```sql
select metadata->>'id' as id, metadata->>'origen' as caso, metadata->>'patron' as patron,
       metadata->>'aprobado_por' as aprobado_por
from public.ltm_abusos order by id;
```

### 10. Detener o reiniciar

```bash
cd infra
docker compose down          # detiene n8n y Ollama; flujos, credenciales y modelo se conservan
docker compose up -d         # vuelve a levantarlos
docker compose down -v       # además BORRA flujos, credenciales y el modelo descargado
```

La memoria vive en Supabase y no se borra al detener los contenedores. Para vaciar solo los casos aprendidos y empezar de nuevo: `truncate public.ltm_abusos;` en el SQL Editor.

### Regenerar los documentos

| Qué | Comando |
|---|---|
| Fragmentos de memoria | `python3 scripts/generar_fuentes_negocio.py && python3 scripts/preparar_memoria.py` |
| Informe | `python3 scripts/catalogo.py && python3 scripts/generar_informe.py` |
| PDF | `python3 scripts/generar_pdf.py` (requiere pandoc, Chrome, `pypdf`, `reportlab` y `pillow`) |

## Seguridad del propio sistema

- Las claves (Claude, Supabase) solo existen cifradas dentro de las credenciales de n8n. `infra/.env` y los zip están en `.gitignore`.
- Supabase tiene RLS activado y sin políticas. Solo la clave secreta accede, y las funciones están retiradas a `anon` y `authenticated`.
- n8n escucha solo en `127.0.0.1`, y Ollama no publica puertos.
- Los agentes no tienen herramientas con efectos. El contenido variable va entre etiquetas como datos, y la salida está restringida por esquema (*structured outputs*).
- Solo WF-3 escribe en `ltm_abusos`, y siempre después de la aprobación de una persona.
- No se usaron datos reales de clientes.

## Fases

| Fase | Entregable | Estado |
|---|---|---|
| 1 | Casos de uso y supuestos | ✅ |
| 2 | Diagrama del flujo con límites de confianza | ✅ |
| 3 | Diseño de la arquitectura de agentes | ✅ |
| 4 | Infraestructura: n8n, Supabase, Ollama, API de Claude | ✅ |
| 5 | Carga de la memoria de largo plazo | ✅ |
| 6 | Agentes y prompts | ✅ |
| 7 | Ejecución y evidencias | ✅ |
| 8 | Informe de threat modeling STRIDE | ✅ |
| 9 | Extra opcional: mitigación implementada con agentes | No realizada |
| 10 | Documentación y entrega | ✅ |

## Estructura del repositorio

```
├── REQUISITOS.md            matriz de cumplimiento
├── data/                    casos de uso, flujos, supuestos, conocimiento, fragmentos de memoria, catálogo de casos de abuso
├── diagrams/                diagramas (Graphviz .dot, SVG, PNG)
├── docs/                    documentos 01–09, evidencias y PDF de entrega
├── infra/                   Compose de n8n y Ollama
├── n8n/                     flujos WF-1, WF-2 y WF-3
├── prompts/                 prompts y esquemas de salida
├── scripts/                 generación de fuentes, memoria, catálogo, informe y PDF
└── sql/                     esquema y consultas de Supabase
```
