"""Listado de documentos disponibles, leído directamente de documentos/."""

from app.config import DOCUMENTOS_DIR


def listar_documentos() -> dict[str, list[dict]]:
    resultado: dict[str, list[dict]] = {}
    if not DOCUMENTOS_DIR.is_dir():
        return resultado
    for area_dir in sorted(p for p in DOCUMENTOS_DIR.iterdir() if p.is_dir()):
        archivos = []
        for archivo in sorted(area_dir.iterdir()):
            if archivo.is_file() and not archivo.name.startswith("."):
                archivos.append({"archivo": archivo.name, "formato": archivo.suffix.lstrip(".")})
        if archivos:
            resultado[area_dir.name] = archivos
    return resultado
