# Agente de IA corporativo tipo RAG — Ponqué Ponqué Calarcá (challenge Oracle ONE / Alura)

## Contexto

Challenge del bootcamp Oracle ONE (Alura): construir un agente conversacional tipo RAG
(Retrieval Augmented Generation) que responda preguntas sobre documentos internos de una
empresa, con ingesta multi-formato, cobertura multi-dominio, acceso abierto (sin roles) y
despliegue en Oracle Cloud Infrastructure (OCI) con evidencia en el README.

Este proyecto es un repositorio **nuevo e independiente** de `plataforma/` (la plataforma
real del negocio). Se inspira en el modelo de negocio y en la experiencia previa construyendo
el agente RAG real (LangChain + ChromaDB + embeddings), pero:

- Usa el **nombre real** "Ponqué Ponqué Calarcá" (sirve también como pieza de portafolio/marca).
- Todos los **documentos y datos son ficticios/de ejemplo** — nunca se publican cifras, clientes,
  empleados ni información real del negocio.
- No comparte código, base de datos ni credenciales con `plataforma/`.

Entrega objetivo: **esta semana**. La cuenta de OCI todavía no existe y hay que crearla
(Always Free) como parte del trabajo — es el mayor riesgo de tiempo del proyecto, más que la
lógica del RAG en sí.

## Alcance

Áreas documentales cubiertas (subconjunto realista, no las 10 sugeridas por el challenge):
**operaciones/logística, finanzas, marketing, RH básico, calidad/producto, comunicación interna.**

Formatos exigidos por el challenge, repartidos entre esas áreas para que los 8 aparezcan al
menos una vez: PDF, Word, Excel, PowerPoint, Markdown, CSV, JSON, HTML.

Acceso abierto: cualquier pregunta puede recuperar contexto de cualquier área — no hay control
de acceso por rol ni departamento.

## Arquitectura

**Repositorio**: `ponque-rag-challenge/` (hermano de `plataforma/`, git y GitHub propios,
público).

**Componentes:**

- `documentos/<area>/` — documentos ficticios organizados por área, cubriendo entre todos los
  8 formatos requeridos.
- `ingesta/` — un cargador por formato (basados en loaders de LangChain community: PyPDF,
  python-docx, openpyxl, python-pptx, markdown/BeautifulSoup, csv/json estándar), trocea el
  texto (`RecursiveCharacterTextSplitter`) y genera embeddings vía **OCI Generative AI**.
- `scripts/indexar_documentos.py` — corre la ingesta completa y guarda los vectores en
  **ChromaDB local persistido** (mismo patrón usado en la plataforma real).
- `app/` — FastAPI:
  - Endpoint `POST /chat`: recibe una pregunta → la embebe con OCI Generative AI → busca los
    fragmentos más similares en Chroma (sin filtrar por área) → arma un prompt con ese
    contexto → llama al modelo de chat de OCI Generative AI → responde citando el/los
    documento(s) fuente.
  - Página única (Jinja2 + JS vanilla) con la interfaz de chat (ver sección Interfaz web).
- `Dockerfile` + `docker-compose.yml` — para desplegar en una VM Always Free de OCI (ARM
  Ampere).
- `README.md` — instrucciones, arquitectura, y evidencia (captura/video) del agente corriendo
  en la URL pública de la VM.

**Motor de IA**: OCI Generative AI para embeddings y generación de respuesta (modelos
Cohere/Llama disponibles en OCI; el modelo exacto se confirma al crear la cuenta OCI, según
qué esté habilitado en la región elegida). Se elige en vez de OpenAI para cumplir el requisito
de "al menos un servicio OCI" de forma directa y para no depender de una API key de OpenAI en
un repo público.

**Despliegue**: VM Compute Always Free de OCI corriendo el contenedor vía Docker. Junto con
OCI Generative AI, esto cubre dos servicios OCI (Compute + Generative AI).

**Ingesta de documentos**: fija, no hay subida de archivos desde la interfaz. Los documentos
viven en el repo y se indexan una vez, antes de arrancar el servidor, corriendo
`scripts/indexar_documentos.py`.

## Flujo de datos

1. **Indexado** (una vez, antes de arrancar el servidor): `scripts/indexar_documentos.py`
   recorre `documentos/<area>/`, cada archivo pasa por el loader de su formato → se trocea el
   texto → se generan embeddings vía OCI Generative AI → se guardan en Chroma junto con
   metadata (`archivo`, `área`, `formato`).
2. **Consulta**: el colaborador escribe una pregunta en el chat web → FastAPI embebe la
   pregunta con OCI Generative AI → busca los fragmentos más similares en Chroma (sin filtrar
   por área ni rol) → arma un prompt con esos fragmentos como contexto → el modelo de chat de
   OCI Generative AI genera la respuesta → la respuesta se muestra citando el/los documento(s)
   fuente (ej. "según `politica-vacaciones.docx`...").
3. **Sin restricciones**: cualquier pregunta puede traer contexto de cualquier área.

## Interfaz web

Una sola página, sin login ni navegación:

- **Encabezado**: logo real de Ponqué Ponqué Calarcá + título "Asistente interno Ponqué Ponqué
  Calarcá" + una línea aclarando que es un proyecto de challenge con datos de ejemplo.
- **Cuerpo**: chat tipo burbujas (pregunta a la derecha, respuesta a la izquierda), scroll
  vertical.
- **Cada respuesta** incluye debajo del texto una línea con el/los documento(s) fuente citados
  (ej. "Fuente: `politica-vacaciones.docx` — RH"), para que se note visualmente que es RAG.
- **Pie**: caja de texto + botón "Preguntar", con un par de preguntas de ejemplo como chips
  clicables.
- Sin framework de JS — HTML + Jinja2 + JavaScript vanilla (fetch al endpoint `/chat`).
- Reutiliza la paleta de colores de marca de Ponqué (la misma del dashboard real).

**Implementación de la interfaz**: se construye durante la fase de implementación con la skill
`ui-ux-pro-max:design`, siguiendo esta descripción como brief.

## Manejo de errores

- Documento no parseable durante el indexado (formato corrupto, encoding raro): se registra un
  aviso y se salta ese archivo; el indexado completo no se cae por uno malo.
- Falla en la llamada a OCI Generative AI (red, límite de uso, credencial vencida) durante una
  consulta: el chat muestra un mensaje de error amigable ("no pude conectar con el servicio de
  IA, intenta de nuevo") en vez de romperse.
- Índice de Chroma inexistente o vacío al arrancar el servidor: error claro pidiendo correr
  primero `scripts/indexar_documentos.py`.

## Pruebas

Con `unittest` (igual que en la plataforma real), sin las guardas de Telegram/base viva que no
aplican a este proyecto:

- Una prueba por loader de formato: confirma que cada tipo de archivo (PDF, Word, Excel, etc.)
  se lee y trocea correctamente usando un archivo de ejemplo pequeño.
- Una prueba de extremo a extremo del endpoint `/chat` con el cliente de OCI Generative AI
  *mockeado* (sin depender de credenciales reales ni gastar cuota en CI), verificando que dada
  una pregunta conocida se recupera el fragmento correcto de Chroma.
- No se prueba contra la cuenta OCI real en CI — eso se verifica manualmente al desplegar (la
  evidencia del README).

## Entregables

- Repositorio público en GitHub (`ponque-rag-challenge`).
- Despliegue accesible en una VM Always Free de OCI, usando OCI Compute + OCI Generative AI.
- README con instrucciones, arquitectura, y evidencia (captura o video) del agente corriendo en
  la URL pública de OCI.

## Fuera de alcance

- Subida de documentos en caliente desde la interfaz.
- Control de acceso por rol o departamento.
- Cobertura de las 10 áreas sugeridas por el challenge (se cubre un subconjunto realista de 6).
- Reutilización de código o datos de `plataforma/` (proyecto independiente).
- Vector search nativo en Oracle Autonomous Database (se usa Chroma local por simplicidad y
  menor riesgo de tiempo).
