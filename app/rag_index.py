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
