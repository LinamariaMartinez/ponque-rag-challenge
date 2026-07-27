"""Cliente delgado sobre la API de Groq (chat) para el despliegue en Streamlit Cloud.

Groq no ofrece un endpoint de embeddings, así que esos se generan localmente
con fastembed (ver app/streamlit_rag.py). Aquí solo se resuelve el chat.
"""

import os

import httpx

_GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

_INSTRUCCION_GROUNDING = (
    "Eres un asistente interno que responde preguntas usando únicamente la "
    "información de los fragmentos de documentos que se te dan como contexto. "
    "Si la respuesta no está en esos fragmentos, dilo claramente en vez de "
    "inventar información."
)


def chat(pregunta: str, contexto: list[str]) -> str:
    """Genera una respuesta usando los fragmentos de contexto como grounding."""
    api_key = os.environ["GROQ_API_KEY"]
    modelo = os.environ.get("GROQ_MODEL", "llama-3.3-70b-versatile")
    fragmentos = "\n\n".join(
        f"[Fragmento {i + 1}]\n{fragmento}" for i, fragmento in enumerate(contexto)
    )
    mensajes = [
        {"role": "system", "content": _INSTRUCCION_GROUNDING},
        {"role": "user", "content": f"Fragmentos de contexto:\n{fragmentos}\n\nPregunta: {pregunta}"},
    ]
    respuesta = httpx.post(
        _GROQ_URL,
        headers={"Authorization": f"Bearer {api_key}"},
        json={"model": modelo, "messages": mensajes, "temperature": 0.2, "max_tokens": 600},
        timeout=60,
    )
    respuesta.raise_for_status()
    return respuesta.json()["choices"][0]["message"]["content"]
