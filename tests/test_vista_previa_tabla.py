import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from openpyxl import Workbook

from app.vista_previa import generar_vista_previa


class TestVistaPreviaTabla(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self.tmp.name)
        (self.dir / "operaciones").mkdir()
        self.parche = patch("app.vista_previa.DOCUMENTOS_DIR", self.dir)
        self.parche.start()

    def tearDown(self):
        self.parche.stop()
        self.tmp.cleanup()

    def test_vista_previa_csv(self):
        ruta = self.dir / "operaciones" / "rutas.csv"
        ruta.write_text("zona,dia\nNorte,Lunes\n", encoding="utf-8")
        resultado = generar_vista_previa("operaciones", "rutas.csv")
        self.assertEqual(resultado["tipo"], "tabla")
        hoja = resultado["contenido"][0]
        self.assertIsNone(hoja["hoja"])
        self.assertEqual(hoja["encabezados"], ["zona", "dia"])
        self.assertEqual(hoja["filas"], [["Norte", "Lunes"]])

    def test_vista_previa_xlsx(self):
        ruta = self.dir / "operaciones" / "datos.xlsx"
        libro = Workbook()
        hoja = libro.active
        hoja.title = "Hoja1"
        hoja.append(["Categoría", "Valor"])
        hoja.append(["Prueba", 100])
        libro.save(str(ruta))
        resultado = generar_vista_previa("operaciones", "datos.xlsx")
        self.assertEqual(resultado["tipo"], "tabla")
        hoja_resultado = resultado["contenido"][0]
        self.assertEqual(hoja_resultado["hoja"], "Hoja1")
        self.assertEqual(hoja_resultado["encabezados"], ["Categoría", "Valor"])
        self.assertEqual(hoja_resultado["filas"], [["Prueba", "100"]])

    def test_archivo_inexistente_lanza_filenotfound(self):
        with self.assertRaises(FileNotFoundError):
            generar_vista_previa("operaciones", "no-existe.csv")

    def test_path_traversal_en_area_lanza_filenotfound(self):
        with self.assertRaises(FileNotFoundError):
            generar_vista_previa("..", "README.md")

    def test_formato_no_soportado_lanza_valueerror(self):
        ruta = self.dir / "operaciones" / "nota.txt"
        ruta.write_text("contenido", encoding="utf-8")
        with self.assertRaises(ValueError):
            generar_vista_previa("operaciones", "nota.txt")
