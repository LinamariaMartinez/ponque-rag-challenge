"""FastAPI: interfaz de chat y endpoint /chat del agente RAG."""

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field

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
    pregunta: str = Field(max_length=500)


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
