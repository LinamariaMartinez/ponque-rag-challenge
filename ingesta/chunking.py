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
