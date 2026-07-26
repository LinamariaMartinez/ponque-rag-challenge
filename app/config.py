"""Rutas del proyecto y carga de variables de entorno (.env)."""

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DOCUMENTOS_DIR = BASE_DIR / "documentos"
CHROMA_DIR = BASE_DIR / "data" / "chroma"

ENV_PATH = BASE_DIR / ".env"


def load_env() -> None:
    """Carga las variables de .env al entorno, sin dependencias externas.

    Las líneas vacías o que empiezan con '#' se ignoran. Los valores ya
    presentes en el entorno no se sobreescriben.
    """
    if not ENV_PATH.exists():
        return
    for line in ENV_PATH.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        os.environ.setdefault(key.strip(), value.strip().strip("'\""))
