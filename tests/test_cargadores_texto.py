import tempfile
import unittest
from pathlib import Path

from ingesta.cargadores import cargar_documento


class TestCargadoresTexto(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def test_carga_markdown(self):
        ruta = self.dir / "doc.md"
        ruta.write_text("# Título\n\nContenido de prueba.", encoding="utf-8")
        self.assertIn("Contenido de prueba", cargar_documento(ruta))

    def test_carga_csv(self):
        ruta = self.dir / "doc.csv"
        ruta.write_text("zona,dia\nNorte,Lunes\n", encoding="utf-8")
        texto = cargar_documento(ruta)
        self.assertIn("Norte", texto)
        self.assertIn("Lunes", texto)

    def test_carga_json(self):
        ruta = self.dir / "doc.json"
        ruta.write_text('{"tema": "prueba"}', encoding="utf-8")
        self.assertIn("prueba", cargar_documento(ruta))

    def test_carga_html(self):
        ruta = self.dir / "doc.html"
        ruta.write_text(
            "<html><body><h1>Aviso</h1><p>Texto de prueba</p></body></html>",
            encoding="utf-8",
        )
        texto = cargar_documento(ruta)
        self.assertIn("Aviso", texto)
        self.assertIn("Texto de prueba", texto)

    def test_formato_no_soportado_lanza_error(self):
        ruta = self.dir / "doc.txt"
        ruta.write_text("contenido", encoding="utf-8")
        with self.assertRaises(ValueError):
            cargar_documento(ruta)
