import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import app.rag_index as rag_index


class TestRagIndex(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        rag_index._cliente = None
        rag_index._coleccion = None
        self.parche_dir = patch("app.rag_index.CHROMA_DIR", Path(self.tmp.name))
        self.parche_dir.start()

    def tearDown(self):
        self.parche_dir.stop()
        rag_index._cliente = None
        rag_index._coleccion = None
        self.tmp.cleanup()

    def test_hay_documentos_falso_si_vacio(self):
        self.assertFalse(rag_index.hay_documentos())

    @patch("app.rag_index.embed_texts")
    def test_indexar_y_buscar(self, mock_embed):
        mock_embed.side_effect = [
            [[1.0, 0.0], [0.0, 1.0]],  # embeddings de los dos fragmentos indexados
            [[1.0, 0.0]],               # embedding de la pregunta
        ]
        rag_index.indexar_fragmentos(
            fragmentos=["Fragmento sobre vacaciones", "Fragmento sobre presupuesto"],
            metadatas=[
                {"area": "rh", "archivo": "a.docx"},
                {"area": "finanzas", "archivo": "b.xlsx"},
            ],
            ids=["rh:a:0", "finanzas:b:0"],
        )
        self.assertTrue(rag_index.hay_documentos())

        resultados = rag_index.buscar("¿Cuántos días de vacaciones tengo?", n=1)

        self.assertEqual(resultados[0]["archivo"], "a.docx")
        self.assertEqual(resultados[0]["area"], "rh")
