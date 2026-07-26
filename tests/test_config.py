# tests/test_config.py
import os
import unittest
import tempfile
from pathlib import Path
from unittest.mock import patch

from app import config


class TestLoadEnv(unittest.TestCase):
    def test_carga_variables_del_archivo(self):
        with tempfile.TemporaryDirectory() as tmp:
            ruta_env = Path(tmp) / ".env"
            ruta_env.write_text(
                "OCI_COMPARTMENT_ID=ocid1.test\n# comentario\n\nOCI_CHAT_MODEL_ID=modelo-x\n",
                encoding="utf-8",
            )
            with patch.object(config, "ENV_PATH", ruta_env):
                os.environ.pop("OCI_COMPARTMENT_ID", None)
                os.environ.pop("OCI_CHAT_MODEL_ID", None)
                config.load_env()
            self.assertEqual(os.environ["OCI_COMPARTMENT_ID"], "ocid1.test")
            self.assertEqual(os.environ["OCI_CHAT_MODEL_ID"], "modelo-x")
            del os.environ["OCI_COMPARTMENT_ID"]
            del os.environ["OCI_CHAT_MODEL_ID"]

    def test_no_sobreescribe_variables_existentes(self):
        with tempfile.TemporaryDirectory() as tmp:
            ruta_env = Path(tmp) / ".env"
            ruta_env.write_text("OCI_COMPARTMENT_ID=del_archivo\n", encoding="utf-8")
            os.environ["OCI_COMPARTMENT_ID"] = "ya_definida"
            with patch.object(config, "ENV_PATH", ruta_env):
                config.load_env()
            self.assertEqual(os.environ["OCI_COMPARTMENT_ID"], "ya_definida")
            del os.environ["OCI_COMPARTMENT_ID"]
