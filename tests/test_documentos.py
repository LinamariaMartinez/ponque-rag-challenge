import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from app.documentos import listar_documentos


class TestListarDocumentos(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self.tmp.name)
        (self.dir / "rh").mkdir()
        (self.dir / "rh" / "politica.docx").write_text("contenido", encoding="utf-8")
        (self.dir / "finanzas").mkdir()
        (self.dir / "finanzas" / "presupuesto.xlsx").write_text("contenido", encoding="utf-8")
        (self.dir / "finanzas" / ".DS_Store").write_text("", encoding="utf-8")
        self.parche = patch("app.documentos.DOCUMENTOS_DIR", self.dir)
        self.parche.start()

    def tearDown(self):
        self.parche.stop()
        self.tmp.cleanup()

    def test_agrupa_por_area_con_formato(self):
        resultado = listar_documentos()
        self.assertEqual(resultado["rh"], [{"archivo": "politica.docx", "formato": "docx"}])
        self.assertEqual(resultado["finanzas"], [{"archivo": "presupuesto.xlsx", "formato": "xlsx"}])

    def test_omite_archivos_ocultos(self):
        resultado = listar_documentos()
        nombres = [a["archivo"] for a in resultado["finanzas"]]
        self.assertNotIn(".DS_Store", nombres)

    def test_directorio_vacio_devuelve_vacio(self):
        with tempfile.TemporaryDirectory() as vacio:
            with patch("app.documentos.DOCUMENTOS_DIR", Path(vacio)):
                self.assertEqual(listar_documentos(), {})
