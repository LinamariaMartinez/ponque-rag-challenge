"""Índice RAG en memoria para el despliegue en Streamlit Cloud.

Sin ChromaDB ni disco persistido: con el puñado de documentos ficticios del
challenge, basta con recalcular los embeddings al arrancar y comparar por
similitud coseno en memoria. Los embeddings salen de un modelo local
(fastembed), no de una API externa.
"""

import os

import numpy as np
from fastembed import TextEmbedding

from app.config import DOCUMENTOS_DIR
from ingesta.cargadores import cargar_documento
from ingesta.chunking import dividir_en_fragmentos

_MODELO_EMBED = os.environ.get(
    "FASTEMBED_MODEL", "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
)

_modelo = None


def _obtener_modelo() -> TextEmbedding:
    global _modelo
    if _modelo is None:
        _modelo = TextEmbedding(model_name=_MODELO_EMBED)
    return _modelo


def _embed(textos: list[str]) -> np.ndarray:
    vectores = list(_obtener_modelo().embed(textos))
    return np.array(vectores)


def construir_indice(directorio=DOCUMENTOS_DIR) -> dict:
    """Carga, trocea y embebe todos los documentos. Devuelve el índice en memoria."""
    fragmentos, metadatas = [], []
    for area_dir in sorted(p for p in directorio.iterdir() if p.is_dir()):
        area = area_dir.name
        for archivo in sorted(area_dir.iterdir()):
            if archivo.name.startswith("."):
                continue
            try:
                texto = cargar_documento(archivo)
            except ValueError:
                continue
            for fragmento in dividir_en_fragmentos(texto):
                fragmentos.append(fragmento)
                metadatas.append({"area": area, "archivo": archivo.name})

    if not fragmentos:
        return {"fragmentos": [], "metadatas": [], "embeddings": np.empty((0, 0))}

    embeddings = _embed(fragmentos)
    return {"fragmentos": fragmentos, "metadatas": metadatas, "embeddings": embeddings}


def hay_documentos(indice: dict) -> bool:
    return len(indice["fragmentos"]) > 0


def buscar(pregunta: str, indice: dict, n: int = 4) -> list[dict]:
    if not hay_documentos(indice):
        return []
    vector_pregunta = _embed([pregunta])[0]
    matriz = indice["embeddings"]
    similitudes = matriz @ vector_pregunta / (
        np.linalg.norm(matriz, axis=1) * np.linalg.norm(vector_pregunta) + 1e-10
    )
    top_n = np.argsort(-similitudes)[:n]
    return [
        {
            "texto": indice["fragmentos"][i],
            "archivo": indice["metadatas"][i]["archivo"],
            "area": indice["metadatas"][i]["area"],
        }
        for i in top_n
    ]
