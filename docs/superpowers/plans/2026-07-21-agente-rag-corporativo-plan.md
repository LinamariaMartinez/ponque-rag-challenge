# Agente RAG corporativo — Plan de implementación

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Construir el agente RAG corporativo de Ponqué Ponqué Calarcá (documentos ficticios, multi-formato, acceso abierto) descrito en `docs/superpowers/specs/2026-07-20-agente-rag-corporativo-design.md`, listo para desplegar en una VM Always Free de OCI.

**Architecture:** FastAPI sirve una página de chat y un endpoint `/chat`; un índice ChromaDB local guarda los fragmentos embebidos de los documentos ficticios; OCI Generative AI genera tanto los embeddings como la respuesta final citando la fuente. Un script de indexado corre antes del servidor para poblar Chroma desde `documentos/<area>/`.

**Tech Stack:** Python 3.12, FastAPI, ChromaDB, OCI Python SDK (`oci`), `langchain-text-splitters`, `pypdf`, `python-docx`, `openpyxl`, `python-pptx`, `beautifulsoup4`, `reportlab`, Docker.

## Global Constraints

- Todos los documentos y datos son **ficticios** — nunca información real del negocio (spec, sección Contexto).
- Se usa el nombre real "Ponqué Ponqué Calarcá"; los datos que aparecen en los documentos son inventados (spec, sección Contexto).
- Acceso abierto: sin control de acceso por rol ni departamento (spec, sección Alcance).
- La IA **nunca ejecuta `git add`/`git commit`/`git push`** en este repo. Linamaría hace todos los commits manualmente, uno por bloque de tareas. Cada bloque de este plan te da el mensaje exacto — en inglés, corto, directo y sucinto — listo para copiar.
- Repo independiente de `plataforma/`: no se comparte código, base de datos ni credenciales.
- Pruebas con `unittest` (no `pytest`), corriendo `python -m unittest discover tests` desde la raíz del repo. El cliente de OCI Generative AI **siempre se mockea** en pruebas automatizadas — ninguna prueba llama a OCI de verdad ni gasta cuota.
- La interfaz web (Task 10) se construye con la skill `ui-ux-pro-max:design`, no a mano.

---

## File Structure

```
ponque-rag-challenge/
├── .env.example
├── .gitignore
├── .dockerignore
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── README.md
├── app/
│   ├── __init__.py
│   ├── config.py            # rutas del proyecto + load_env()
│   ├── oci_genai.py         # wrapper del SDK de OCI: embed_texts(), chat()
│   ├── rag_index.py         # índice Chroma: indexar_fragmentos(), buscar(), hay_documentos()
│   ├── main.py               # FastAPI: GET /, POST /chat
│   ├── templates/
│   │   └── index.html        # chat UI (Task 10, vía skill de diseño)
│   └── static/
│       ├── logo.png          # copiado de plataforma/app/web/static/logo.png
│       ├── style.css          # Task 10
│       └── chat.js            # Task 10
├── ingesta/
│   ├── __init__.py
│   ├── chunking.py           # dividir_en_fragmentos()
│   └── cargadores.py         # cargar_documento() + un cargador por formato
├── documentos/
│   ├── rh/politica-vacaciones.docx
│   ├── finanzas/presupuesto-trimestral.xlsx
│   ├── marketing/plan-campana-dia-madre.pptx
│   ├── marketing/calendario-contenido.json
│   ├── operaciones/manual-despacho.pdf
│   ├── operaciones/rutas-entrega.csv
│   ├── calidad/checklist-calidad.md
│   └── comunicacion-interna/boletin-interno.html
├── scripts/
│   ├── __init__.py
│   ├── generar_documentos_ficticios.py   # crea los 4 archivos binarios de ejemplo
│   └── indexar_documentos.py              # indexa documentos/ hacia Chroma
└── tests/
    ├── __init__.py
    ├── test_config.py
    ├── test_oci_genai.py
    ├── test_chunking.py
    ├── test_cargadores_texto.py
    ├── test_cargadores_binarios.py
    ├── test_rag_index.py
    ├── test_indexar_documentos.py
    └── test_main.py
```

---

### Task 1: Scaffolding del proyecto y configuración

**Files:**
- Create: `requirements.txt`
- Create: `.gitignore`
- Create: `.env.example`
- Create: `app/__init__.py`
- Create: `app/config.py`
- Create: `tests/__init__.py`
- Create: `tests/test_config.py`

**Interfaces:**
- Produces: `app.config.BASE_DIR: Path`, `app.config.DOCUMENTOS_DIR: Path`, `app.config.CHROMA_DIR: Path`, `app.config.ENV_PATH: Path`, `app.config.load_env() -> None`

- [ ] **Step 1: Crear `requirements.txt`**

```
fastapi
uvicorn[standard]
jinja2
python-multipart
httpx
chromadb
oci
langchain-text-splitters
pypdf
python-docx
openpyxl
python-pptx
beautifulsoup4
reportlab
```

- [ ] **Step 2: Crear `.gitignore`**

```
.venv/
__pycache__/
*.pyc
.env
data/
```

- [ ] **Step 3: Crear `.env.example`**

```
OCI_CONFIG_PROFILE=DEFAULT
OCI_COMPARTMENT_ID=ocid1.compartment.oc1..reemplaza_con_el_tuyo
OCI_SERVICE_ENDPOINT=https://inference.generativeai.us-chicago-1.oci.oraclecloud.com
OCI_EMBED_MODEL_ID=cohere.embed-multilingual-v3.0
OCI_CHAT_MODEL_ID=cohere.command-r-08-2024
```

- [ ] **Step 4: Crear `app/__init__.py`** (vacío)

- [ ] **Step 5: Escribir la prueba que falla — `tests/__init__.py` y `tests/test_config.py`**

`tests/__init__.py` vacío.

```python
# tests/test_config.py
import os
import unittest
import tempfile
from pathlib import Path
from unittest.mock import patch

from app import config


class TestLoadEnv(unittest.TestCase):
    def test_carga_variables_del_archivo(self):
        with tempfile.TemporaryDirectory() as tmp:
            ruta_env = Path(tmp) / ".env"
            ruta_env.write_text(
                "OCI_COMPARTMENT_ID=ocid1.test\n# comentario\n\nOCI_CHAT_MODEL_ID=modelo-x\n",
                encoding="utf-8",
            )
            with patch.object(config, "ENV_PATH", ruta_env):
                os.environ.pop("OCI_COMPARTMENT_ID", None)
                os.environ.pop("OCI_CHAT_MODEL_ID", None)
                config.load_env()
            self.assertEqual(os.environ["OCI_COMPARTMENT_ID"], "ocid1.test")
            self.assertEqual(os.environ["OCI_CHAT_MODEL_ID"], "modelo-x")
            del os.environ["OCI_COMPARTMENT_ID"]
            del os.environ["OCI_CHAT_MODEL_ID"]

    def test_no_sobreescribe_variables_existentes(self):
        with tempfile.TemporaryDirectory() as tmp:
            ruta_env = Path(tmp) / ".env"
            ruta_env.write_text("OCI_COMPARTMENT_ID=del_archivo\n", encoding="utf-8")
            os.environ["OCI_COMPARTMENT_ID"] = "ya_definida"
            with patch.object(config, "ENV_PATH", ruta_env):
                config.load_env()
            self.assertEqual(os.environ["OCI_COMPARTMENT_ID"], "ya_definida")
            del os.environ["OCI_COMPARTMENT_ID"]
```

- [ ] **Step 6: Confirmar que falla (no existe `app/config.py` todavía)**

Run: `python -m unittest tests.test_config -v`
Expected: `ModuleNotFoundError: No module named 'app.config'` (o `ImportError`)

- [ ] **Step 7: Crear `app/config.py`**

```python
"""Rutas del proyecto y carga de variables de entorno (.env)."""

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DOCUMENTOS_DIR = BASE_DIR / "documentos"
CHROMA_DIR = BASE_DIR / "data" / "chroma"

ENV_PATH = BASE_DIR / ".env"


def load_env() -> None:
    """Carga las variables de .env al entorno, sin dependencias externas.

    Las líneas vacías o que empiezan con '#' se ignoran. Los valores ya
    presentes en el entorno no se sobreescriben.
    """
    if not ENV_PATH.exists():
        return
    for line in ENV_PATH.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        os.environ.setdefault(key.strip(), value.strip().strip("'\""))
```

- [ ] **Step 8: Confirmar que pasa**

Run: `python -m unittest tests.test_config -v`
Expected: `OK` (2 tests)

- [ ] **Step 9: Commit**

```bash
git add requirements.txt .gitignore .env.example app/__init__.py app/config.py tests/__init__.py tests/test_config.py
git commit -m "chore: scaffold project structure and env config"
```

---

### Task 2: Cliente de OCI Generative AI

**Files:**
- Create: `app/oci_genai.py`
- Create: `tests/test_oci_genai.py`

**Interfaces:**
- Consumes: nada de tareas anteriores.
- Produces: `app.oci_genai.embed_texts(textos: list[str]) -> list[list[float]]`, `app.oci_genai.chat(pregunta: str, contexto: list[str]) -> str`

> Si algún nombre de clase o campo del SDK `oci` no coincide con tu versión instalada, este es el único archivo que hay que tocar. La consola de OCI → Generative AI → Playground tiene un botón "View Code" que genera un snippet exacto con los nombres correctos para tu cuenta y modelo — úsalo como referencia si algo falla.

- [ ] **Step 1: Escribir la prueba que falla**

```python
# tests/test_oci_genai.py
import os
import unittest
from unittest.mock import MagicMock, patch

from app import oci_genai


class TestOciGenai(unittest.TestCase):
    def setUp(self):
        oci_genai._cliente = None
        self.env_patch = patch.dict(os.environ, {
            "OCI_SERVICE_ENDPOINT": "https://inference.generativeai.us-chicago-1.oci.oraclecloud.com",
            "OCI_COMPARTMENT_ID": "ocid1.compartment.oc1..test",
        })
        self.env_patch.start()

    def tearDown(self):
        self.env_patch.stop()
        oci_genai._cliente = None

    @patch("app.oci_genai._obtener_cliente")
    def test_embed_texts_devuelve_vectores(self, mock_obtener):
        cliente_falso = MagicMock()
        cliente_falso.embed_text.return_value.data.embeddings = [[0.1, 0.2], [0.3, 0.4]]
        mock_obtener.return_value = cliente_falso

        vectores = oci_genai.embed_texts(["texto uno", "texto dos"])

        self.assertEqual(vectores, [[0.1, 0.2], [0.3, 0.4]])
        cliente_falso.embed_text.assert_called_once()

    @patch("app.oci_genai._obtener_cliente")
    def test_chat_devuelve_texto(self, mock_obtener):
        cliente_falso = MagicMock()
        cliente_falso.chat.return_value.data.chat_response.text = "Respuesta generada"
        mock_obtener.return_value = cliente_falso

        respuesta = oci_genai.chat("¿pregunta?", ["contexto uno"])

        self.assertEqual(respuesta, "Respuesta generada")
        cliente_falso.chat.assert_called_once()
```

- [ ] **Step 2: Confirmar que falla**

Run: `python -m unittest tests.test_oci_genai -v`
Expected: `ModuleNotFoundError: No module named 'app.oci_genai'`

- [ ] **Step 3: Instalar dependencias y crear `app/oci_genai.py`**

Run primero: `pip install -r requirements.txt`

```python
"""Cliente delgado sobre OCI Generative AI: embeddings y chat con grounding.

Aísla el SDK de oci en un solo módulo para que el resto de la app no dependa
de sus tipos exactos ni de cómo está configurada la cuenta."""

import os

import oci
from oci.generative_ai_inference import GenerativeAiInferenceClient
from oci.generative_ai_inference.models import (
    ChatDetails,
    CohereChatRequest,
    EmbedTextDetails,
    OnDemandServingMode,
)

_cliente = None


def _obtener_cliente() -> GenerativeAiInferenceClient:
    global _cliente
    if _cliente is None:
        perfil = os.environ.get("OCI_CONFIG_PROFILE", "DEFAULT")
        configuracion = oci.config.from_file(profile_name=perfil)
        _cliente = GenerativeAiInferenceClient(
            config=configuracion,
            service_endpoint=os.environ["OCI_SERVICE_ENDPOINT"],
        )
    return _cliente


def embed_texts(textos: list[str]) -> list[list[float]]:
    """Genera un embedding por cada texto de entrada."""
    detalles = EmbedTextDetails(
        inputs=textos,
        serving_mode=OnDemandServingMode(
            model_id=os.environ.get("OCI_EMBED_MODEL_ID", "cohere.embed-multilingual-v3.0")
        ),
        compartment_id=os.environ["OCI_COMPARTMENT_ID"],
        truncate="END",
    )
    respuesta = _obtener_cliente().embed_text(detalles)
    return list(respuesta.data.embeddings)


def chat(pregunta: str, contexto: list[str]) -> str:
    """Genera una respuesta usando los fragmentos de contexto como grounding."""
    documentos = [{"snippet": fragmento} for fragmento in contexto]
    solicitud = CohereChatRequest(
        message=pregunta,
        documents=documentos,
        max_tokens=600,
        temperature=0.2,
        is_stream=False,
    )
    detalles = ChatDetails(
        serving_mode=OnDemandServingMode(
            model_id=os.environ.get("OCI_CHAT_MODEL_ID", "cohere.command-r-08-2024")
        ),
        chat_request=solicitud,
        compartment_id=os.environ["OCI_COMPARTMENT_ID"],
    )
    respuesta = _obtener_cliente().chat(detalles)
    return respuesta.data.chat_response.text
```

- [ ] **Step 4: Confirmar que pasa**

Run: `python -m unittest tests.test_oci_genai -v`
Expected: `OK` (2 tests)

- [ ] **Step 5: Commit**

```bash
git add app/oci_genai.py tests/test_oci_genai.py
git commit -m "feat: add OCI Generative AI client wrapper"
```

---

### Task 3: Troceo de texto (chunking)

**Files:**
- Create: `ingesta/__init__.py`
- Create: `ingesta/chunking.py`
- Create: `tests/test_chunking.py`

**Interfaces:**
- Produces: `ingesta.chunking.dividir_en_fragmentos(texto: str) -> list[str]`

- [ ] **Step 1: Escribir la prueba que falla**

```python
# tests/test_chunking.py
import unittest

from ingesta.chunking import dividir_en_fragmentos


class TestChunking(unittest.TestCase):
    def test_texto_vacio_no_produce_fragmentos(self):
        self.assertEqual(dividir_en_fragmentos(""), [])
        self.assertEqual(dividir_en_fragmentos("   "), [])

    def test_texto_corto_produce_un_fragmento(self):
        fragmentos = dividir_en_fragmentos("Texto corto de ejemplo.")
        self.assertEqual(fragmentos, ["Texto corto de ejemplo."])

    def test_texto_largo_produce_varios_fragmentos(self):
        parrafo = "Ponqué Ponqué Calarcá vende tortas. " * 60  # ~2200 caracteres
        fragmentos = dividir_en_fragmentos(parrafo)
        self.assertGreater(len(fragmentos), 1)
        for fragmento in fragmentos:
            self.assertLessEqual(len(fragmento), 900)
```

- [ ] **Step 2: Confirmar que falla**

Run: `python -m unittest tests.test_chunking -v`
Expected: `ModuleNotFoundError: No module named 'ingesta'`

- [ ] **Step 3: Crear `ingesta/__init__.py`** (vacío) **y `ingesta/chunking.py`**

```python
"""Divide texto largo en fragmentos superpuestos, listos para embeber."""

from langchain_text_splitters import RecursiveCharacterTextSplitter

TAMANO_MAXIMO = 800
SUPERPOSICION = 100

_splitter = RecursiveCharacterTextSplitter(
    chunk_size=TAMANO_MAXIMO,
    chunk_overlap=SUPERPOSICION,
)


def dividir_en_fragmentos(texto: str) -> list[str]:
    texto = texto.strip()
    if not texto:
        return []
    return _splitter.split_text(texto)
```

- [ ] **Step 4: Confirmar que pasa**

Run: `python -m unittest tests.test_chunking -v`
Expected: `OK` (3 tests)

- [ ] **Step 5: Commit**

```bash
git add ingesta/__init__.py ingesta/chunking.py tests/test_chunking.py
git commit -m "feat: add text chunking utility"
```

---

### Task 4: Cargadores de formatos de texto plano (Markdown, CSV, JSON, HTML)

**Files:**
- Create: `ingesta/cargadores.py`
- Create: `tests/test_cargadores_texto.py`

**Interfaces:**
- Produces: `ingesta.cargadores.cargar_documento(ruta: Path) -> str` (lanza `ValueError` si la extensión no está soportada), `ingesta.cargadores.CARGADORES: dict[str, Callable]`

- [ ] **Step 1: Escribir la prueba que falla**

```python
# tests/test_cargadores_texto.py
import tempfile
import unittest
from pathlib import Path

from ingesta.cargadores import cargar_documento


class TestCargadoresTexto(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def test_carga_markdown(self):
        ruta = self.dir / "doc.md"
        ruta.write_text("# Título\n\nContenido de prueba.", encoding="utf-8")
        self.assertIn("Contenido de prueba", cargar_documento(ruta))

    def test_carga_csv(self):
        ruta = self.dir / "doc.csv"
        ruta.write_text("zona,dia\nNorte,Lunes\n", encoding="utf-8")
        texto = cargar_documento(ruta)
        self.assertIn("Norte", texto)
        self.assertIn("Lunes", texto)

    def test_carga_json(self):
        ruta = self.dir / "doc.json"
        ruta.write_text('{"tema": "prueba"}', encoding="utf-8")
        self.assertIn("prueba", cargar_documento(ruta))

    def test_carga_html(self):
        ruta = self.dir / "doc.html"
        ruta.write_text(
            "<html><body><h1>Aviso</h1><p>Texto de prueba</p></body></html>",
            encoding="utf-8",
        )
        texto = cargar_documento(ruta)
        self.assertIn("Aviso", texto)
        self.assertIn("Texto de prueba", texto)

    def test_formato_no_soportado_lanza_error(self):
        ruta = self.dir / "doc.txt"
        ruta.write_text("contenido", encoding="utf-8")
        with self.assertRaises(ValueError):
            cargar_documento(ruta)
```

- [ ] **Step 2: Confirmar que falla**

Run: `python -m unittest tests.test_cargadores_texto -v`
Expected: `ModuleNotFoundError: No module named 'ingesta.cargadores'`

- [ ] **Step 3: Crear `ingesta/cargadores.py`**

```python
"""Carga el texto plano de un documento según su formato."""

import csv
import json
from pathlib import Path

from bs4 import BeautifulSoup


def cargar_markdown(ruta: Path) -> str:
    return ruta.read_text(encoding="utf-8")


def cargar_csv(ruta: Path) -> str:
    with ruta.open(encoding="utf-8") as archivo:
        lector = csv.reader(archivo)
        return "\n".join(" | ".join(fila) for fila in lector)


def cargar_json(ruta: Path) -> str:
    datos = json.loads(ruta.read_text(encoding="utf-8"))
    return json.dumps(datos, ensure_ascii=False, indent=2)


def cargar_html(ruta: Path) -> str:
    sopa = BeautifulSoup(ruta.read_text(encoding="utf-8"), "html.parser")
    return sopa.get_text(separator="\n", strip=True)


CARGADORES = {
    ".md": cargar_markdown,
    ".csv": cargar_csv,
    ".json": cargar_json,
    ".html": cargar_html,
}


def cargar_documento(ruta: Path) -> str:
    cargador = CARGADORES.get(ruta.suffix.lower())
    if cargador is None:
        raise ValueError(f"Formato no soportado: {ruta.suffix}")
    return cargador(ruta)
```

- [ ] **Step 4: Confirmar que pasa**

Run: `python -m unittest tests.test_cargadores_texto -v`
Expected: `OK` (5 tests)

- [ ] **Step 5: Commit**

```bash
git add ingesta/cargadores.py tests/test_cargadores_texto.py
git commit -m "feat: add loaders for text-based document formats"
```

---

### Task 5: Cargadores de formatos binarios (PDF, Word, Excel, PowerPoint)

**Files:**
- Modify: `ingesta/cargadores.py`
- Create: `tests/test_cargadores_binarios.py`

**Interfaces:**
- Modifica `ingesta.cargadores.CARGADORES` para incluir `.pdf`, `.docx`, `.xlsx`, `.pptx`. `cargar_documento()` mantiene la misma firma.

- [ ] **Step 1: Escribir la prueba que falla**

```python
# tests/test_cargadores_binarios.py
import tempfile
import unittest
from pathlib import Path

from docx import Document
from openpyxl import Workbook
from pptx import Presentation
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

from ingesta.cargadores import cargar_documento


class TestCargadoresBinarios(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def test_carga_pdf(self):
        ruta = self.dir / "doc.pdf"
        lienzo = canvas.Canvas(str(ruta), pagesize=letter)
        lienzo.drawString(72, 720, "Contenido de prueba PDF")
        lienzo.save()
        self.assertIn("Contenido de prueba PDF", cargar_documento(ruta))

    def test_carga_docx(self):
        ruta = self.dir / "doc.docx"
        documento = Document()
        documento.add_paragraph("Contenido de prueba DOCX")
        documento.save(str(ruta))
        self.assertIn("Contenido de prueba DOCX", cargar_documento(ruta))

    def test_carga_xlsx(self):
        ruta = self.dir / "doc.xlsx"
        libro = Workbook()
        hoja = libro.active
        hoja.append(["Categoría", "Valor"])
        hoja.append(["Prueba", 100])
        libro.save(str(ruta))
        texto = cargar_documento(ruta)
        self.assertIn("Prueba", texto)
        self.assertIn("100", texto)

    def test_carga_pptx(self):
        ruta = self.dir / "doc.pptx"
        presentacion = Presentation()
        diapositiva = presentacion.slides.add_slide(presentacion.slide_layouts[1])
        diapositiva.shapes.title.text = "Contenido de prueba PPTX"
        presentacion.save(str(ruta))
        self.assertIn("Contenido de prueba PPTX", cargar_documento(ruta))
```

- [ ] **Step 2: Confirmar que falla**

Run: `python -m unittest tests.test_cargadores_binarios -v`
Expected: 4 `FAIL`/`ERROR` — `ValueError: Formato no soportado: .pdf` (y análogos)

- [ ] **Step 3: Modificar `ingesta/cargadores.py`**

Agrega estos imports al principio del archivo, junto a los existentes:

```python
from docx import Document as DocxDocument
from openpyxl import load_workbook
from pptx import Presentation
from pypdf import PdfReader
```

Agrega estas funciones antes de `CARGADORES`:

```python
def cargar_pdf(ruta: Path) -> str:
    lector = PdfReader(str(ruta))
    return "\n".join(pagina.extract_text() or "" for pagina in lector.pages)


def cargar_docx(ruta: Path) -> str:
    documento = DocxDocument(str(ruta))
    return "\n".join(p.text for p in documento.paragraphs if p.text.strip())


def cargar_xlsx(ruta: Path) -> str:
    libro = load_workbook(str(ruta), data_only=True)
    lineas = []
    for hoja in libro.worksheets:
        lineas.append(f"Hoja: {hoja.title}")
        for fila in hoja.iter_rows(values_only=True):
            valores = [str(v) for v in fila if v is not None]
            if valores:
                lineas.append(" | ".join(valores))
    return "\n".join(lineas)


def cargar_pptx(ruta: Path) -> str:
    presentacion = Presentation(str(ruta))
    lineas = []
    for i, diapositiva in enumerate(presentacion.slides, start=1):
        lineas.append(f"Diapositiva {i}")
        for forma in diapositiva.shapes:
            if forma.has_text_frame and forma.text_frame.text.strip():
                lineas.append(forma.text_frame.text.strip())
    return "\n".join(lineas)
```

Y reemplaza el diccionario `CARGADORES` para incluir los cuatro formatos nuevos:

```python
CARGADORES = {
    ".md": cargar_markdown,
    ".csv": cargar_csv,
    ".json": cargar_json,
    ".html": cargar_html,
    ".pdf": cargar_pdf,
    ".docx": cargar_docx,
    ".xlsx": cargar_xlsx,
    ".pptx": cargar_pptx,
}
```

- [ ] **Step 4: Confirmar que pasa**

Run: `python -m unittest tests.test_cargadores_binarios tests.test_cargadores_texto -v`
Expected: `OK` (9 tests)

- [ ] **Step 5: Commit**

```bash
git add ingesta/cargadores.py tests/test_cargadores_binarios.py
git commit -m "feat: add loaders for binary document formats"
```

---

### Task 6: Índice vectorial en ChromaDB

**Files:**
- Create: `app/rag_index.py`
- Create: `tests/test_rag_index.py`

**Interfaces:**
- Consumes: `app.oci_genai.embed_texts(textos: list[str]) -> list[list[float]]` (Task 2)
- Produces: `app.rag_index.indexar_fragmentos(fragmentos: list[str], metadatas: list[dict], ids: list[str]) -> None`, `app.rag_index.buscar(pregunta: str, n: int = 4) -> list[dict]` (cada dict: `{"texto": str, "archivo": str, "area": str}`), `app.rag_index.hay_documentos() -> bool`

- [ ] **Step 1: Escribir la prueba que falla**

```python
# tests/test_rag_index.py
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import app.rag_index as rag_index


class TestRagIndex(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        rag_index._cliente = None
        rag_index._coleccion = None
        self.parche_dir = patch("app.rag_index.CHROMA_DIR", Path(self.tmp.name))
        self.parche_dir.start()

    def tearDown(self):
        self.parche_dir.stop()
        rag_index._cliente = None
        rag_index._coleccion = None
        self.tmp.cleanup()

    def test_hay_documentos_falso_si_vacio(self):
        self.assertFalse(rag_index.hay_documentos())

    @patch("app.rag_index.embed_texts")
    def test_indexar_y_buscar(self, mock_embed):
        mock_embed.side_effect = [
            [[1.0, 0.0], [0.0, 1.0]],  # embeddings de los dos fragmentos indexados
            [[1.0, 0.0]],               # embedding de la pregunta
        ]
        rag_index.indexar_fragmentos(
            fragmentos=["Fragmento sobre vacaciones", "Fragmento sobre presupuesto"],
            metadatas=[
                {"area": "rh", "archivo": "a.docx"},
                {"area": "finanzas", "archivo": "b.xlsx"},
            ],
            ids=["rh:a:0", "finanzas:b:0"],
        )
        self.assertTrue(rag_index.hay_documentos())

        resultados = rag_index.buscar("¿Cuántos días de vacaciones tengo?", n=1)

        self.assertEqual(resultados[0]["archivo"], "a.docx")
        self.assertEqual(resultados[0]["area"], "rh")
```

- [ ] **Step 2: Confirmar que falla**

Run: `python -m unittest tests.test_rag_index -v`
Expected: `ModuleNotFoundError: No module named 'app.rag_index'`

- [ ] **Step 3: Crear `app/rag_index.py`**

```python
"""Índice vectorial en ChromaDB: indexa fragmentos y busca los más afines."""

import chromadb

from app.config import CHROMA_DIR
from app.oci_genai import embed_texts

COLECCION = "ponque_docs"

_cliente = None
_coleccion = None


def _obtener_coleccion():
    global _cliente, _coleccion
    if _coleccion is None:
        _cliente = chromadb.PersistentClient(path=str(CHROMA_DIR))
        _coleccion = _cliente.get_or_create_collection(
            COLECCION, metadata={"hnsw:space": "cosine"}
        )
    return _coleccion


def hay_documentos() -> bool:
    return _obtener_coleccion().count() > 0


def indexar_fragmentos(fragmentos: list[str], metadatas: list[dict], ids: list[str]) -> None:
    coleccion = _obtener_coleccion()
    vectores = embed_texts(fragmentos)
    coleccion.add(ids=ids, embeddings=vectores, documents=fragmentos, metadatas=metadatas)


def buscar(pregunta: str, n: int = 4) -> list[dict]:
    coleccion = _obtener_coleccion()
    if coleccion.count() == 0:
        return []
    vector_pregunta = embed_texts([pregunta])[0]
    resultado = coleccion.query(
        query_embeddings=[vector_pregunta], n_results=min(n, coleccion.count())
    )
    return [
        {"texto": doc, "archivo": meta.get("archivo"), "area": meta.get("area")}
        for doc, meta in zip(resultado["documents"][0], resultado["metadatas"][0])
    ]
```

- [ ] **Step 4: Confirmar que pasa**

Run: `python -m unittest tests.test_rag_index -v`
Expected: `OK` (2 tests)

- [ ] **Step 5: Commit**

```bash
git add app/rag_index.py tests/test_rag_index.py
git commit -m "feat: add Chroma vector index wrapper"
```

---

### Task 7: Documentos ficticios de muestra

**Files:**
- Create: `documentos/marketing/calendario-contenido.json`
- Create: `documentos/operaciones/rutas-entrega.csv`
- Create: `documentos/calidad/checklist-calidad.md`
- Create: `documentos/comunicacion-interna/boletin-interno.html`
- Create: `scripts/__init__.py`
- Create: `scripts/generar_documentos_ficticios.py`

No lleva pruebas unitarias (son datos de muestra, no lógica) — la verificación es visual/manual en el Step 3.

- [ ] **Step 1: Crear los 4 documentos de texto plano**

`documentos/marketing/calendario-contenido.json`:

```json
[
  {"fecha": "2026-08-03", "plataforma": "Instagram", "tema": "Presentación torta de proteína"},
  {"fecha": "2026-08-10", "plataforma": "WhatsApp", "tema": "Catálogo de sabores para pedidos grandes"},
  {"fecha": "2026-08-17", "plataforma": "Instagram", "tema": "Detrás de cámaras en la fábrica"},
  {"fecha": "2026-08-24", "plataforma": "Facebook", "tema": "Testimonios de clientes frecuentes"},
  {"fecha": "2026-08-31", "plataforma": "WhatsApp", "tema": "Promoción de fin de mes"}
]
```

`documentos/operaciones/rutas-entrega.csv`:

```csv
zona,dia,conductor,vehiculo
Norte,Lunes,Carlos Ramírez,Moto
Sur,Martes,Diana Osorio,Moto
Centro,Miércoles,Carlos Ramírez,Carro
Norte,Jueves,Fernando Gil,Moto
Sur,Viernes,Diana Osorio,Carro
```

`documentos/calidad/checklist-calidad.md`:

```markdown
# Checklist de calidad antes de despacho (ejemplo)

Documento de ejemplo (datos ficticios) para el agente RAG.

## Revisión visual

- [ ] La torta no tiene golpes ni hundimientos en la superficie.
- [ ] El color del glaseado es uniforme, sin manchas.
- [ ] La decoración coincide con el pedido (sabor, tamaño, mensaje).

## Empaque

- [ ] La caja no tiene humedad ni manchas de grasa.
- [ ] El sello de seguridad está intacto y visible.
- [ ] La etiqueta con los datos del cliente es legible.

## Registro

- [ ] Se registró la hora de empaque en la planilla de calidad.
- [ ] Se registró el nombre de quien hizo la revisión.
```

`documentos/comunicacion-interna/boletin-interno.html`:

```html
<!DOCTYPE html>
<html lang="es">
<head><meta charset="utf-8"><title>Boletín interno — edición de ejemplo</title></head>
<body>
  <h1>Boletín interno — edición de ejemplo</h1>
  <p>Documento de ejemplo (datos ficticios) para el agente RAG.</p>

  <h2>Bienvenida</h2>
  <p>Le damos la bienvenida a Mariana Ruiz, quien se une al equipo de logística
  esta semana. Mariana apoyará las rutas de entrega de la zona Norte.</p>

  <h2>Recordatorio de horario</h2>
  <p>El horario de atención en fábrica los sábados cambia de 8:00 a.m. a 1:00 p.m.,
  a partir del primer sábado del próximo mes.</p>

  <h2>Próxima reunión general</h2>
  <p>La reunión mensual del equipo será el último viernes del mes a las 3:00 p.m.</p>
</body>
</html>
```

- [ ] **Step 2: Crear `scripts/__init__.py`** (vacío) **y `scripts/generar_documentos_ficticios.py`**

```python
"""Genera los documentos ficticios en formato binario (DOCX, XLSX, PPTX, PDF)
para documentos/. Los formatos de texto plano (JSON, CSV, MD, HTML) ya están
creados directamente como archivos y no pasan por este script."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from docx import Document
from openpyxl import Workbook
from pptx import Presentation
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

from app.config import DOCUMENTOS_DIR


def generar_politica_vacaciones() -> None:
    ruta = DOCUMENTOS_DIR / "rh" / "politica-vacaciones.docx"
    ruta.parent.mkdir(parents=True, exist_ok=True)
    documento = Document()
    documento.add_heading("Política de Vacaciones — Ponqué Ponqué Calarcá", level=1)
    documento.add_paragraph("Documento de ejemplo (datos ficticios) para el agente RAG.")
    documento.add_heading("Días disponibles", level=2)
    documento.add_paragraph(
        "Cada colaborador con más de un año de antigüedad tiene derecho a 15 días "
        "hábiles de vacaciones remuneradas por año."
    )
    documento.add_heading("Cómo solicitarlas", level=2)
    documento.add_paragraph(
        "La solicitud se hace por escrito al área de Recursos Humanos con al menos "
        "15 días calendario de anticipación. RH confirma la aprobación en un plazo "
        "máximo de 3 días hábiles."
    )
    documento.add_heading("Pago", level=2)
    documento.add_paragraph(
        "El pago de vacaciones se realiza junto con la nómina del mes en que inicia "
        "el periodo de descanso."
    )
    documento.save(str(ruta))
    print(f"  [ok] {ruta.relative_to(DOCUMENTOS_DIR.parent)}")


def generar_presupuesto() -> None:
    ruta = DOCUMENTOS_DIR / "finanzas" / "presupuesto-trimestral.xlsx"
    ruta.parent.mkdir(parents=True, exist_ok=True)
    libro = Workbook()
    hoja = libro.active
    hoja.title = "Presupuesto Q3 2026"
    hoja.append(["Categoría", "Presupuestado (COP)", "Ejecutado (COP)"])
    filas = [
        ("Materia prima fábrica", 18000000, 17250000),
        ("Transporte y logística", 4500000, 4800000),
        ("Publicidad", 3000000, 2100000),
        ("Nómina", 12000000, 12000000),
        ("Empaques", 2200000, 2350000),
    ]
    for fila in filas:
        hoja.append(list(fila))
    libro.save(str(ruta))
    print(f"  [ok] {ruta.relative_to(DOCUMENTOS_DIR.parent)}")


def generar_plan_campana() -> None:
    ruta = DOCUMENTOS_DIR / "marketing" / "plan-campana-dia-madre.pptx"
    ruta.parent.mkdir(parents=True, exist_ok=True)
    presentacion = Presentation()

    diapositiva = presentacion.slides.add_slide(presentacion.slide_layouts[0])
    diapositiva.shapes.title.text = "Campaña Día de la Madre 2026 (ejemplo)"
    diapositiva.placeholders[1].text = "Ponqué Ponqué Calarcá — plan de marketing ficticio"

    layout_contenido = presentacion.slide_layouts[1]

    diapositiva = presentacion.slides.add_slide(layout_contenido)
    diapositiva.shapes.title.text = "Objetivo"
    diapositiva.placeholders[1].text = (
        "Aumentar en 20% los pedidos de la semana del Día de la Madre frente al mes "
        "anterior (meta ficticia de ejemplo)."
    )

    diapositiva = presentacion.slides.add_slide(layout_contenido)
    diapositiva.shapes.title.text = "Canales"
    marco = diapositiva.placeholders[1].text_frame
    marco.text = "Instagram (pauta + orgánico)"
    marco.add_paragraph().text = "WhatsApp (catálogo a clientes frecuentes)"
    marco.add_paragraph().text = "Volanteo en puntos de venta aliados"

    diapositiva = presentacion.slides.add_slide(layout_contenido)
    diapositiva.shapes.title.text = "Presupuesto y cronograma"
    marco = diapositiva.placeholders[1].text_frame
    marco.text = "Presupuesto: $1.500.000 COP (ficticio)"
    marco.add_paragraph().text = "Del 20 de abril al 10 de mayo de 2026"

    presentacion.save(str(ruta))
    print(f"  [ok] {ruta.relative_to(DOCUMENTOS_DIR.parent)}")


def generar_manual_despacho() -> None:
    ruta = DOCUMENTOS_DIR / "operaciones" / "manual-despacho.pdf"
    ruta.parent.mkdir(parents=True, exist_ok=True)
    lienzo = canvas.Canvas(str(ruta), pagesize=letter)
    _, alto = letter
    y = alto - 72

    def linea(texto: str, salto: int = 18, tamano: int = 11) -> None:
        nonlocal y
        lienzo.setFont("Helvetica", tamano)
        lienzo.drawString(72, y, texto)
        y -= salto

    linea("Manual de Empaque y Despacho — Ponqué Ponqué Calarcá", tamano=14)
    linea("Documento de ejemplo (datos ficticios) para el agente RAG.", salto=28)
    linea("1. Verificar el pedido contra la orden antes de empacar.")
    linea("2. Usar caja rígida para transportes de más de 30 minutos.")
    linea("3. Sellar la caja con cinta de seguridad con el logo de la marca.")
    linea("4. Confirmar la dirección y el nombre del cliente antes de despachar.")
    linea("5. Registrar la hora de salida del domiciliario en la planilla diaria.")
    lienzo.save()
    print(f"  [ok] {ruta.relative_to(DOCUMENTOS_DIR.parent)}")


def main() -> None:
    print("Generando documentos ficticios binarios...")
    generar_politica_vacaciones()
    generar_presupuesto()
    generar_plan_campana()
    generar_manual_despacho()
    print("Listo.")


if __name__ == "__main__":
    main()
```

- [ ] **Step 3: Correr el script y verificar los 8 archivos**

Run: `python scripts/generar_documentos_ficticios.py`
Expected: 4 líneas `[ok]`, una por archivo binario.

Run: `find documentos -type f | sort`
Expected: 8 archivos — uno por cada formato (`.docx`, `.xlsx`, `.pptx`, `.json`, `.pdf`, `.csv`, `.md`, `.html`), repartidos en las 6 áreas.

- [ ] **Step 4: Commit**

```bash
git add documentos scripts/__init__.py scripts/generar_documentos_ficticios.py
git commit -m "feat: add fictional sample documents for all formats"
```

---

### Task 8: Script de indexado

**Files:**
- Create: `scripts/indexar_documentos.py`
- Create: `tests/test_indexar_documentos.py`

**Interfaces:**
- Consumes: `ingesta.cargadores.cargar_documento` (Task 4/5), `ingesta.chunking.dividir_en_fragmentos` (Task 3), `app.rag_index.indexar_fragmentos` (Task 6)
- Produces: `scripts.indexar_documentos.indexar_todos(directorio: Path = DOCUMENTOS_DIR) -> int` (devuelve el total de fragmentos indexados), `scripts.indexar_documentos.main() -> None`

- [ ] **Step 1: Escribir la prueba que falla**

```python
# tests/test_indexar_documentos.py
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts.indexar_documentos import indexar_todos


class TestIndexarDocumentos(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self.tmp.name)
        (self.dir / "rh").mkdir()
        (self.dir / "rh" / "politica.md").write_text(
            "# Política\n\nContenido de ejemplo con suficiente texto para un fragmento.",
            encoding="utf-8",
        )

    def tearDown(self):
        self.tmp.cleanup()

    @patch("scripts.indexar_documentos.indexar_fragmentos")
    def test_indexa_archivo_valido(self, mock_indexar):
        total = indexar_todos(self.dir)
        self.assertEqual(total, 1)
        mock_indexar.assert_called_once()

    @patch("scripts.indexar_documentos.indexar_fragmentos")
    def test_omite_formato_no_soportado(self, mock_indexar):
        (self.dir / "rh" / "notas.txt").write_text("contenido", encoding="utf-8")
        indexar_todos(self.dir)
        mock_indexar.assert_called_once()  # solo el .md; el .txt se omite sin tumbar el resto
```

- [ ] **Step 2: Confirmar que falla**

Run: `python -m unittest tests.test_indexar_documentos -v`
Expected: `ModuleNotFoundError: No module named 'scripts.indexar_documentos'`

- [ ] **Step 3: Crear `scripts/indexar_documentos.py`**

```python
"""Indexa todos los documentos de documentos/<area>/ hacia ChromaDB."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.config import DOCUMENTOS_DIR, load_env
from app.rag_index import indexar_fragmentos
from ingesta.cargadores import cargar_documento
from ingesta.chunking import dividir_en_fragmentos


def indexar_todos(directorio: Path = DOCUMENTOS_DIR) -> int:
    total_fragmentos = 0
    for area_dir in sorted(p for p in directorio.iterdir() if p.is_dir()):
        area = area_dir.name
        for archivo in sorted(area_dir.iterdir()):
            if archivo.name.startswith("."):
                continue
            try:
                texto = cargar_documento(archivo)
            except ValueError as error:
                print(f"  [omitido] {archivo.name}: {error}")
                continue
            except Exception as error:  # noqa: BLE001 — un archivo malo no tumba el indexado
                print(f"  [error] {archivo.name}: {error}")
                continue
            fragmentos = dividir_en_fragmentos(texto)
            if not fragmentos:
                print(f"  [vacío] {archivo.name}")
                continue
            ids = [f"{area}:{archivo.stem}:{i}" for i in range(len(fragmentos))]
            metadatas = [{"area": area, "archivo": archivo.name} for _ in fragmentos]
            indexar_fragmentos(fragmentos, metadatas, ids)
            total_fragmentos += len(fragmentos)
            print(f"  [ok] {archivo.name}: {len(fragmentos)} fragmentos")
    return total_fragmentos


def main() -> None:
    load_env()
    print(f"Indexando documentos de {DOCUMENTOS_DIR}...")
    total = indexar_todos()
    print(f"\nTotal indexado: {total} fragmentos")


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Confirmar que pasa**

Run: `python -m unittest tests.test_indexar_documentos -v`
Expected: `OK` (2 tests)

- [ ] **Step 5: Commit**

```bash
git add scripts/indexar_documentos.py tests/test_indexar_documentos.py
git commit -m "feat: add document indexing script"
```

> **Nota:** correr `python scripts/indexar_documentos.py` de verdad contra los 8 documentos de `documentos/` (en vez de la prueba mockeada) requiere las credenciales de OCI configuradas — eso lo resolvemos en el paso aparte de configuración de la cuenta. Cuando esté listo, corre el script y confirma que imprime 8 líneas `[ok]` antes de seguir con el despliegue (Task 12).

---

### Task 9: Backend FastAPI y endpoint `/chat`

**Files:**
- Create: `app/main.py`
- Create: `tests/test_main.py`

**Interfaces:**
- Consumes: `app.rag_index.buscar` (Task 6), `app.oci_genai.chat` (Task 2)
- Produces: `app.main.app` (instancia de `FastAPI`); `POST /chat` recibe `{"pregunta": str}` y devuelve `{"respuesta": str, "fuentes": list[str]}`; `GET /` sirve `app/templates/index.html`

- [ ] **Step 1: Escribir la prueba que falla**

```python
# tests/test_main.py
import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient

from app.main import app


class TestChatEndpoint(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    @patch("app.main.generar_respuesta")
    @patch("app.main.buscar")
    def test_responde_con_fuentes(self, mock_buscar, mock_generar):
        mock_buscar.return_value = [
            {"texto": "15 días hábiles al año.", "archivo": "politica-vacaciones.docx", "area": "rh"}
        ]
        mock_generar.return_value = "Tienes 15 días hábiles de vacaciones al año."

        respuesta = self.client.post("/chat", json={"pregunta": "¿Cuántos días de vacaciones tengo?"})

        self.assertEqual(respuesta.status_code, 200)
        cuerpo = respuesta.json()
        self.assertIn("15 días hábiles", cuerpo["respuesta"])
        self.assertIn("politica-vacaciones.docx — rh", cuerpo["fuentes"])

    @patch("app.main.buscar")
    def test_sin_documentos_indexados(self, mock_buscar):
        mock_buscar.return_value = []

        respuesta = self.client.post("/chat", json={"pregunta": "cualquier cosa"})

        self.assertEqual(respuesta.status_code, 200)
        self.assertIn("indexar_documentos.py", respuesta.json()["respuesta"])

    @patch("app.main.generar_respuesta")
    @patch("app.main.buscar")
    def test_error_del_servicio_ia(self, mock_buscar, mock_generar):
        mock_buscar.return_value = [{"texto": "algo", "archivo": "a.md", "area": "calidad"}]
        mock_generar.side_effect = Exception("timeout")

        respuesta = self.client.post("/chat", json={"pregunta": "¿algo?"})

        self.assertEqual(respuesta.status_code, 200)
        self.assertIn("No pude conectar", respuesta.json()["respuesta"])

    def test_pagina_principal_carga(self):
        respuesta = self.client.get("/")
        self.assertEqual(respuesta.status_code, 200)
```

- [ ] **Step 2: Confirmar que falla**

Run: `python -m unittest tests.test_main -v`
Expected: `ModuleNotFoundError: No module named 'app.main'`

- [ ] **Step 3: Crear `app/templates/index.html` mínimo (temporal, Task 10 lo reemplaza)**

```html
<!DOCTYPE html>
<html lang="es">
<head><meta charset="utf-8"><title>Asistente interno Ponqué Ponqué Calarcá</title></head>
<body><h1>Asistente interno Ponqué Ponqué Calarcá</h1></body>
</html>
```

- [ ] **Step 4: Crear `app/main.py`**

```python
"""FastAPI: interfaz de chat y endpoint /chat del agente RAG."""

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

from app.config import BASE_DIR, load_env
from app.oci_genai import chat as generar_respuesta
from app.rag_index import buscar, hay_documentos

load_env()

app = FastAPI(title="Asistente interno Ponqué Ponqué Calarcá")
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "app" / "static")), name="static")
templates = Jinja2Templates(directory=str(BASE_DIR / "app" / "templates"))

MENSAJE_SIN_INDICE = (
    "Todavía no hay documentos indexados. Corre scripts/indexar_documentos.py primero."
)


class PreguntaEntrada(BaseModel):
    pregunta: str


@app.on_event("startup")
def verificar_indice() -> None:
    if not hay_documentos():
        print(f"ADVERTENCIA: {MENSAJE_SIN_INDICE}")


@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse(request, "index.html")


@app.post("/chat")
def responder(entrada: PreguntaEntrada) -> dict:
    fragmentos = buscar(entrada.pregunta)
    if not fragmentos:
        return {"respuesta": MENSAJE_SIN_INDICE, "fuentes": []}
    try:
        texto = generar_respuesta(entrada.pregunta, [f["texto"] for f in fragmentos])
    except Exception:  # noqa: BLE001 — cualquier falla de OCI debe dar un mensaje amable
        return {
            "respuesta": "No pude conectar con el servicio de IA. Intenta de nuevo en un momento.",
            "fuentes": [],
        }
    fuentes = sorted({f'{f["archivo"]} — {f["area"]}' for f in fragmentos})
    return {"respuesta": texto, "fuentes": fuentes}
```

Crea también `app/static/.gitkeep` vacío para que la carpeta exista antes de la Task 10.

- [ ] **Step 5: Confirmar que pasa**

Run: `python -m unittest tests.test_main -v`
Expected: `OK` (4 tests)

- [ ] **Step 6: Commit**

```bash
git add app/main.py app/templates/index.html app/static/.gitkeep tests/test_main.py
git commit -m "feat: add FastAPI backend with /chat endpoint"
```

---

### Task 10: Interfaz web del chat

**Files:**
- Modify: `app/templates/index.html`
- Create: `app/static/style.css`
- Create: `app/static/chat.js`
- Modify (copiar): `app/static/logo.png` (desde `plataforma/app/web/static/logo.png`)

**Interfaces:**
- Consumes: `POST /chat` (Task 9) — envía `{"pregunta": str}`, recibe `{"respuesta": str, "fuentes": list[str]}`

- [ ] **Step 1: Copiar el logo real**

```bash
cp "../plataforma/app/web/static/logo.png" app/static/logo.png
```

- [ ] **Step 2: Invocar la skill `ui-ux-pro-max:design`**

Usa este brief (ya acordado en el spec, sección "Interfaz web"):

> Construye una página de chat de una sola vista para "Asistente interno Ponqué Ponqué Calarcá", en `app/templates/index.html` + `app/static/style.css` + `app/static/chat.js` (JS vanilla, sin framework). Sin login ni navegación.
>
> - **Encabezado:** logo en `/static/logo.png` + título "Asistente interno Ponqué Ponqué Calarcá" + una línea pequeña aclarando que es un proyecto de challenge con datos de ejemplo.
> - **Cuerpo:** chat tipo burbujas (pregunta del usuario a la derecha, respuesta del agente a la izquierda), con scroll vertical.
> - **Cada respuesta del agente** muestra debajo del texto una línea pequeña con las fuentes citadas, ej. "Fuente: politica-vacaciones.docx — rh" (una por cada elemento del array `fuentes` que devuelve la API).
> - **Pie:** caja de texto + botón "Preguntar", más 2-3 chips de preguntas de ejemplo clicables (ej. "¿Cuál es la política de vacaciones?", "¿Cuánto se presupuestó para publicidad?") que rellenan la caja de texto al hacer clic.
> - **Integración:** al enviar, hacer `fetch("/chat", {method: "POST", headers: {"Content-Type": "application/json"}, body: JSON.stringify({pregunta})})`, mostrar `respuesta` en una burbuja nueva y `fuentes` debajo.
> - **Paleta de marca** (tomada de `plataforma/app/web/static/style.css`): naranja/caramelo `#d98e4a` y `#b5651d` como acento, fondo crema `#fdf9f3` / `#faf6f0`, texto café oscuro `#3d2417` / `#5a3a26`, verde `#2e7d32` / `#e8f5e9` para estados positivos, rojo `#c62828` / `#ffebee` para errores. Tipografía: `-apple-system, BlinkMacSystemFont, "Segoe UI", "Helvetica Neue", sans-serif`.

- [ ] **Step 3: Prueba manual end-to-end**

Requiere OCI configurado y `python scripts/indexar_documentos.py` ya corrido con éxito (Task 8, nota final).

Run: `uvicorn app.main:app --reload`

Abre `http://localhost:8000`, haz clic en un chip de pregunta de ejemplo, confirma que aparece la respuesta con su fuente citada debajo.

- [ ] **Step 4: Confirmar que las pruebas automatizadas siguen pasando**

Run: `python -m unittest discover tests -v`
Expected: `OK` (todas las pruebas, incluida `test_pagina_principal_carga`)

- [ ] **Step 5: Commit**

```bash
git add app/templates/index.html app/static/style.css app/static/chat.js app/static/logo.png
git commit -m "feat: add web chat interface"
```

---

### Task 11: Empaquetado con Docker

**Files:**
- Create: `Dockerfile`
- Create: `docker-compose.yml`
- Create: `.dockerignore`

**Interfaces:**
- Consumes: `requirements.txt` (Task 1), `app/main.py` (Task 9), `scripts/indexar_documentos.py` (Task 8)

- [ ] **Step 1: Crear `.dockerignore`**

```
.venv/
__pycache__/
*.pyc
.git/
data/
.env
```

- [ ] **Step 2: Crear `Dockerfile`**

```dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["sh", "-c", "python scripts/indexar_documentos.py && uvicorn app.main:app --host 0.0.0.0 --port 8000"]
```

- [ ] **Step 3: Crear `docker-compose.yml`**

```yaml
services:
  agente:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - chroma_data:/app/data/chroma
      - ~/.oci:/root/.oci:ro
    env_file:
      - .env

volumes:
  chroma_data:
```

- [ ] **Step 4: Construir y correr localmente**

Requiere `.env` completo (copiado de `.env.example`) y `~/.oci/config` + tu clave privada configurados en tu máquina.

Run: `docker compose up --build`
Expected: el contenedor indexa los documentos y arranca uvicorn en el puerto 8000 sin errores.

Run (en otra terminal): `curl -s -X POST http://localhost:8000/chat -H "Content-Type: application/json" -d '{"pregunta":"¿Cuál es la política de vacaciones?"}'`
Expected: JSON con `"respuesta"` y `"fuentes"` no vacíos.

Run: `docker compose down`

- [ ] **Step 5: Commit**

```bash
git add Dockerfile docker-compose.yml .dockerignore
git commit -m "chore: containerize app with Docker"
```

---

### Task 12: Despliegue en OCI

**Files:**
- Modify: `README.md` (sección de despliegue)

**Interfaces:**
- Ninguna — este bloque es operativo, no cambia código.

> Asume que ya tienes una VM Compute Always Free (Ubuntu, ARM Ampere) creada y accesible por SSH — eso se resuelve en la conversación aparte sobre configurar la cuenta de OCI. Aquí solo van los pasos para llevar el contenedor a esa VM.

- [ ] **Step 1: Conectarte a la VM**

```bash
ssh -i <tu-clave-privada.pem> ubuntu@<IP-publica-de-la-VM>
```

- [ ] **Step 2: Instalar Docker en la VM**

```bash
sudo apt update && sudo apt install -y docker.io docker-compose-plugin
sudo usermod -aG docker $USER
```

Cierra sesión y vuelve a conectarte por SSH para que el grupo `docker` tome efecto.

- [ ] **Step 3: Clonar el repo (ya público en GitHub)**

```bash
git clone https://github.com/LinamariaMartinez/ponque-rag-challenge.git
cd ponque-rag-challenge
```

- [ ] **Step 4: Copiar `.env` y credenciales de OCI a la VM**

Desde tu computador (no desde la VM):

```bash
scp -i <tu-clave-privada.pem> .env ubuntu@<IP-publica-de-la-VM>:~/ponque-rag-challenge/.env
scp -i <tu-clave-privada.pem> -r ~/.oci ubuntu@<IP-publica-de-la-VM>:~/.oci
```

- [ ] **Step 5: Levantar el contenedor en la VM**

```bash
docker compose up -d --build
docker compose logs -f
```

Expected: en los logs, las líneas `[ok]` del indexado y luego `Uvicorn running on http://0.0.0.0:8000`.

- [ ] **Step 6: Abrir el puerto 8000**

En la consola de OCI, agrega una regla de ingreso al Security List (o Network Security Group) de la subred de la VM: puerto TCP 8000, origen `0.0.0.0/0`.

- [ ] **Step 7: Verificar desde tu computador**

```bash
curl -s -X POST http://<IP-publica-de-la-VM>:8000/chat -H "Content-Type: application/json" -d '{"pregunta":"¿Cuál es la política de vacaciones?"}'
```

Expected: JSON con `"respuesta"` y `"fuentes"`. También abre `http://<IP-publica-de-la-VM>:8000` en el navegador y prueba el chat.

- [ ] **Step 8: Documentar el despliegue en el README**

Agrega a `README.md` una sección "## Despliegue en OCI" resumiendo los pasos 1-7 (sin las claves/IPs reales).

- [ ] **Step 9: Commit**

```bash
git add README.md
git commit -m "docs: add OCI deployment instructions"
```

---

### Task 13: README final y evidencia

**Files:**
- Modify: `README.md`

**Interfaces:**
- Ninguna.

- [ ] **Step 1: Completar `README.md`**

```markdown
# Asistente interno Ponqué Ponqué Calarcá (RAG) — Challenge Oracle ONE

Agente conversacional tipo RAG (Retrieval Augmented Generation) que responde preguntas sobre
documentos internos de Ponqué Ponqué Calarcá. Construido para el challenge del bootcamp
Oracle ONE (Alura).

> Los documentos indexados (`documentos/`) son **ficticios**, creados solo para este
> ejercicio. No contienen información real del negocio.

## Qué hace

- Ingesta multi-formato: PDF, Word, Excel, PowerPoint, Markdown, CSV, JSON y HTML.
- Cobertura multi-área: operaciones/logística, finanzas, marketing, RH, calidad y
  comunicación interna.
- Acceso abierto: cualquier colaborador puede preguntar sobre cualquier documento, sin
  restricción por rol ni departamento.
- Cada respuesta cita el/los documento(s) fuente que la respaldan.

## Arquitectura

- **Backend:** FastAPI (`app/main.py`), endpoint `POST /chat`.
- **Índice vectorial:** ChromaDB local persistido (`app/rag_index.py`).
- **Motor de IA:** OCI Generative AI para embeddings y generación de respuesta
  (`app/oci_genai.py`).
- **Ingesta:** un cargador por formato (`ingesta/cargadores.py`) + troceo con
  `langchain-text-splitters` (`ingesta/chunking.py`).
- **Interfaz:** página de chat de una sola vista (`app/templates/index.html`).

## Cómo correr en local

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # completa tus credenciales de OCI
python scripts/indexar_documentos.py
uvicorn app.main:app --reload
```

Abre `http://localhost:8000`.

## Pruebas

```bash
python -m unittest discover tests
```

## Despliegue en OCI

Ver la sección agregada en la Task 12 de
`docs/superpowers/plans/2026-07-21-agente-rag-corporativo-plan.md` (o el resumen que quede
aquí mismo tras ese paso).

## Evidencia

<!-- Reemplaza esta línea con una captura o el enlace a un video del agente
     corriendo en la URL pública de la VM de OCI. -->

## Stack

FastAPI · ChromaDB · OCI Generative AI · Docker
```

- [ ] **Step 2: Capturar la evidencia (manual, después de que la Task 12 esté desplegada y verificada)**

Toma una captura de pantalla del chat respondiendo una pregunta en `http://<IP-publica-de-la-VM>:8000`, o graba un video corto. Guarda el archivo como `docs/evidencia-oci.png` (o `.mp4`/enlace) y reemplaza el comentario de la sección "Evidencia" del README por la imagen o el enlace.

- [ ] **Step 3: Commit**

```bash
git add README.md docs/evidencia-oci.png
git commit -m "docs: finalize README with usage and evidence"
```

---

## Self-Review

**Cobertura del spec:** ingesta multi-formato (Tasks 4-5), multi-área con datos ficticios (Task 7), acceso abierto sin roles (Task 9, sin ningún parámetro de usuario/rol en `/chat`), OCI Generative AI para embeddings+chat (Task 2), ChromaDB local (Task 6), FastAPI (Task 9), interfaz web vía skill de diseño (Task 10), Docker (Task 11), despliegue OCI (Task 12), README con evidencia (Task 13), pruebas `unittest` con OCI mockeado (todas las tasks con tests), manejo de errores (documento no parseable → Task 8; falla de OCI → Task 9; índice vacío → Task 9). Sin huecos.

**Placeholders:** ninguno en los bloques de código — las únicas referencias a pasos futuros (evidencia de despliegue, credenciales OCI reales) son notas explícitas de secuencia, no código a medio escribir.

**Consistencia de tipos:** `buscar()` siempre devuelve `list[dict]` con claves `texto`/`archivo`/`area` (Task 6, consumido igual en Task 9); `cargar_documento(ruta: Path) -> str` no cambia de firma entre Task 4 y Task 5 (Task 5 solo añade entradas al diccionario `CARGADORES`); `embed_texts`/`chat` de Task 2 se consumen con la misma firma en Task 6 y Task 9.
