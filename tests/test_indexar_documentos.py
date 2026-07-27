import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts.indexar_documentos import indexar_todos, main


class TestIndexarDocumentos(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self.tmp.name)
        (self.dir / "rh").mkdir()
        (self.dir / "rh" / "politica.md").write_text(
            "# Política\n\nContenido de ejemplo con suficiente texto para un fragmento.",
            encoding="utf-8",
        )

    def tearDown(self):
        self.tmp.cleanup()

    @patch("scripts.indexar_documentos.indexar_fragmentos")
    def test_indexa_archivo_valido(self, mock_indexar):
        total = indexar_todos(self.dir)
        self.assertEqual(total, 1)
        mock_indexar.assert_called_once()

    @patch("scripts.indexar_documentos.indexar_fragmentos")
    def test_omite_formato_no_soportado(self, mock_indexar):
        (self.dir / "rh" / "notas.txt").write_text("contenido", encoding="utf-8")
        indexar_todos(self.dir)
        mock_indexar.assert_called_once()  # solo el .md; el .txt se omite sin tumbar el resto


class TestMain(unittest.TestCase):
    @patch("scripts.indexar_documentos.indexar_fragmentos")
    @patch("scripts.indexar_documentos.hay_documentos")
    @patch("scripts.indexar_documentos.load_env")
    def test_omite_indexacion_si_ya_hay_documentos(
        self, mock_load_env, mock_hay_documentos, mock_indexar
    ):
        mock_hay_documentos.return_value = True
        main()
        mock_indexar.assert_not_called()
