"""Interfaz en Streamlit del asistente interno Ponqué Ponqué Calarcá.

Versión pensada para desplegar gratis en Streamlit Community Cloud: sin
Ollama (no corre ahí) y sin ChromaDB persistido (el índice se recalcula en
memoria al arrancar, ver app/streamlit_rag.py).
"""

import html

import streamlit as st

from app.config import load_env
from app.documentos import listar_documentos
from app.llm_groq import chat as generar_respuesta
from app.streamlit_rag import buscar, construir_indice, hay_documentos
from app.vista_previa import generar_vista_previa

load_env()

LOGO = "app/static/logo.png"

st.set_page_config(page_title="Asistente Ponqué Ponqué Calarcá", page_icon=LOGO, layout="wide")

MENSAJE_SIN_INDICE = "Todavía no hay documentos indexados."


def _burbuja(rol: str, texto: str, fuentes: list[str] | None = None) -> None:
    es_usuario = rol == "user"
    alineacion = "flex-end" if es_usuario else "flex-start"
    fondo = "#d98e4a" if es_usuario else "#faf6f0"
    color_texto = "#fff" if es_usuario else "#3d2417"
    texto_html = html.escape(texto).replace("\n", "<br>")
    st.markdown(
        f"""
        <div style="display:flex; justify-content:{alineacion}; margin:6px 0;">
          <div style="max-width:70%; background:{fondo}; color:{color_texto};
                      padding:10px 14px; border-radius:16px; font-size:0.95rem;
                      line-height:1.4;">
            {texto_html}
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if fuentes:
        st.caption(" · ".join(fuentes))


@st.cache_resource(show_spinner="Indexando documentos...")
def _indice():
    return construir_indice()


def _mostrar_vista_previa(area: str, archivo: str) -> None:
    @st.dialog(archivo)
    def _modal():
        try:
            vista = generar_vista_previa(area, archivo)
        except (FileNotFoundError, ValueError) as error:
            st.error(str(error))
            return

        if vista["tipo"] == "html":
            st.markdown(vista["contenido"], unsafe_allow_html=True)
        elif vista["tipo"] == "tabla":
            for hoja in vista["contenido"]:
                if hoja["hoja"]:
                    st.caption(hoja["hoja"])
                st.table([hoja["encabezados"], *hoja["filas"]] if hoja["encabezados"] else hoja["filas"])
        else:
            for bloque in vista["contenido"]:
                st.text(bloque)

        if st.button("Preguntar sobre este documento"):
            st.session_state["pregunta_prellenada"] = f"Sobre {archivo}: "
            st.rerun()

    _modal()


with st.sidebar:
    st.header("Documentos")
    for area, archivos in listar_documentos().items():
        with st.expander(area):
            for doc in archivos:
                if st.button(doc["archivo"], key=f"doc_{area}_{doc['archivo']}"):
                    _mostrar_vista_previa(area, doc["archivo"])

col_logo, col_titulo = st.columns([1, 10], vertical_alignment="center")
with col_logo:
    st.image(LOGO, width=56)
with col_titulo:
    st.title("Asistente interno Ponqué Ponqué Calarcá")

indice = _indice()
st.session_state.setdefault("mensajes", [])

for mensaje in st.session_state["mensajes"]:
    _burbuja(mensaje["role"], mensaje["content"], mensaje.get("fuentes"))

pregunta = st.chat_input("Escribe tu pregunta...")
if pregunta_prellenada := st.session_state.pop("pregunta_prellenada", None):
    pregunta = pregunta or pregunta_prellenada

if pregunta:
    st.session_state["mensajes"].append({"role": "user", "content": pregunta})
    _burbuja("user", pregunta)

    with st.spinner("Pensando..."):
        if not hay_documentos(indice):
            respuesta, fuentes = MENSAJE_SIN_INDICE, []
        else:
            fragmentos = buscar(pregunta, indice)
            if not fragmentos:
                respuesta, fuentes = MENSAJE_SIN_INDICE, []
            else:
                try:
                    respuesta = generar_respuesta(pregunta, [f["texto"] for f in fragmentos])
                except Exception:  # noqa: BLE001 — cualquier falla del LLM debe dar un mensaje amable
                    respuesta = "No pude conectar con el servicio de IA. Intenta de nuevo en un momento."
                fuentes = sorted({f'{f["archivo"]} — {f["area"]}' for f in fragmentos})
    _burbuja("assistant", respuesta, fuentes)

    st.session_state["mensajes"].append({"role": "assistant", "content": respuesta, "fuentes": fuentes})
