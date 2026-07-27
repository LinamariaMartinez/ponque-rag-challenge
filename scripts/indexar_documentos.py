"""Indexa todos los documentos de documentos/<area>/ hacia ChromaDB."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.config import DOCUMENTOS_DIR, load_env
from app.rag_index import hay_documentos, indexar_fragmentos
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
            formato = archivo.suffix.lstrip(".")
            metadatas = [
                {"area": area, "archivo": archivo.name, "formato": formato} for _ in fragmentos
            ]
            indexar_fragmentos(fragmentos, metadatas, ids)
            total_fragmentos += len(fragmentos)
            print(f"  [ok] {archivo.name}: {len(fragmentos)} fragmentos")
    return total_fragmentos


def main() -> None:
    load_env()
    if hay_documentos():
        print("Ya hay documentos indexados; se omite la indexación.")
        return
    print(f"Indexando documentos de {DOCUMENTOS_DIR}...")
    total = indexar_todos()
    print(f"\nTotal indexado: {total} fragmentos")


if __name__ == "__main__":
    main()
