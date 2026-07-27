# Asistente interno Ponqué Ponqué Calarcá (RAG) — Challenge Oracle ONE

**Ponqué Ponqué Calarcá** es la distribuidora exclusiva de la marca de tortas artesanales
**Ponqué Ponqué**. El negocio está en etapa de lanzamiento y vende a gimnasios, cafés y consumidores finales. 
Esterepositorio es el agente de inteligencia artificial interno del negocio: responde preguntas
de los colaboradores sobre sus propios documentos (políticas, procesos, finanzas, etc.) y es
el entregable del challenge del bootcamp Oracle ONE (Alura), construido como un agente
conversacional tipo RAG (Retrieval Augmented Generation).

> Los documentos indexados (`documentos/`) son **ficticios**, creados solo para este
> ejercicio. No contienen información real del negocio.

## Qué hace

- Ingesta multi-formato: PDF, Word, Excel, PowerPoint, Markdown, CSV, JSON y HTML.
- Cobertura multi-área: operaciones/logística, finanzas, marketing, RH, calidad y
  comunicación interna.
- Acceso abierto: cualquier colaborador puede preguntar sobre cualquier documento, sin
  restricción por rol ni departamento.
- Cada respuesta cita el/los documento(s) fuente que la respaldan.
- Panel de documentos: barra lateral con los documentos agrupados por área; al hacer clic
  en uno se abre una vista previa en modal con el contenido formateado y un botón para
  preguntarle directamente al asistente sobre ese documento.

## Arquitectura

- **Backend:** FastAPI (`app/main.py`), endpoint `POST /chat`.
- **Índice vectorial:** ChromaDB local persistido (`app/rag_index.py`).
- **Motor de IA:** [Ollama](https://ollama.com) local para embeddings y generación de
  respuesta (`app/local_llm.py`) — modelos abiertos (`llama3.2:3b` + `nomic-embed-text`)
  corriendo en la propia máquina/VM, sin costo de inferencia.
- **Ingesta:** un cargador por formato (`ingesta/cargadores.py`) + troceo con
  `langchain-text-splitters` (`ingesta/chunking.py`).
- **Interfaz:** página de chat de una sola vista (`app/templates/index.html`).

## Cómo correr en local

```bash
brew install ollama          # o https://ollama.com/download
ollama serve &                # o `brew services start ollama`
ollama pull llama3.2:3b
ollama pull nomic-embed-text

python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python scripts/indexar_documentos.py
uvicorn app.main:app --reload
```

Abre `http://localhost:8000`.

## Pruebas

```bash
python -m unittest discover tests
```

## Despliegue en OCI

Esta sección describe cómo llevar el contenedor del agente RAG a una VM Compute Always Free en Oracle Cloud. Asume que ya tienes una instancia Ubuntu (ARM Ampere) creada y accesible por SSH.

### Paso 1: Conectarte a la VM

Abre una terminal en tu computador y conectate con tu clave privada:

```bash
ssh -i <tu-clave-privada.pem> ubuntu@<IP-publica-de-la-VM>
```

Reemplaza `<tu-clave-privada.pem>` con la ruta a tu archivo de clave privada y `<IP-publica-de-la-VM>` con la dirección IP pública de tu instancia.

### Paso 2: Instalar Docker en la VM

Una vez conectado por SSH, actualiza el sistema e instala Docker:

```bash
sudo apt update && sudo apt install -y docker.io docker-compose-plugin
sudo usermod -aG docker $USER
```

Después de ejecutar estos comandos, **cierra la sesión SSH y vuelve a conectarte** para que el grupo `docker` tome efecto:

```bash
exit
ssh -i <tu-clave-privada.pem> ubuntu@<IP-publica-de-la-VM>
```

### Paso 3: Clonar el repositorio

El repositorio está público en GitHub. Clónalo en tu VM:

```bash
git clone https://github.com/LinamariaMartinez/ponque-rag-challenge.git
cd ponque-rag-challenge
```

### Paso 4: Copiar `.env` a la VM

Desde tu computador **local** (no desde la VM), copia el archivo `.env`:

```bash
scp -i <tu-clave-privada.pem> .env ubuntu@<IP-publica-de-la-VM>:~/ponque-rag-challenge/.env
```

No hace falta copiar ninguna credencial: el motor de IA es Ollama corriendo dentro de la
propia VM, no un servicio externo.

### Paso 5: Levantar los contenedores en la VM

Conectate nuevamente a la VM y corre Docker Compose:

```bash
ssh -i <tu-clave-privada.pem> ubuntu@<IP-publica-de-la-VM>
cd ponque-rag-challenge
docker compose up -d --build
docker compose logs -f
```

El primer arranque tarda varios minutos: el contenedor `ollama` descarga los modelos
(~2 GB) antes de que el contenedor `agente` pueda indexar los documentos y arrancar.
Espera a que los logs muestren las líneas `[ok]` del indexado y luego
`Uvicorn running on http://0.0.0.0:8000`. Esto indica que el servicio está listo.

### Paso 6: Abrir el puerto 8000 en el firewall

En la consola de Oracle Cloud, navega a la sección de **Redes** y edita el **Security List** (o Network Security Group) de la subred donde está tu VM. Agrega una regla de **ingreso** con los siguientes parámetros:

- **Protocolo:** TCP
- **Puerto de destino:** 8000
- **Origen:** `0.0.0.0/0` (acceso desde cualquier IP)

Guarda la regla.

### Paso 7: Verificar el despliegue

Desde tu computador local, verifica que el servicio está accesible:

```bash
curl -s -X POST http://<IP-publica-de-la-VM>:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"pregunta":"¿Cuál es la política de vacaciones?"}'
```

Deberías recibir un JSON con `"respuesta"` y `"fuentes"`.

También puedes abrir en tu navegador la URL `http://<IP-publica-de-la-VM>:8000` para acceder a la interfaz web del chat.

---

**Nota:** Reemplaza todos los placeholders (`<tu-clave-privada.pem>`, `<IP-publica-de-la-VM>`) con tus valores reales antes de ejecutar cualquier comando.

## Evidencia

![Chat del asistente respondiendo una pregunta](docs/evidencia/captura.png)

![Vista previa de un documento en modal, con panel lateral por área](docs/evidencia/modal-documento.png)

## Stack

FastAPI · ChromaDB · Ollama · Docker · OCI Compute (Always Free)
