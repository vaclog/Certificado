import os
import sys
import tempfile
import types
import unittest
from pathlib import Path
from unittest.mock import patch

fitz_stub = types.ModuleType("fitz")
fitz_stub.open = None
fitz_stub.Rect = None
dotenv_stub = types.ModuleType("dotenv")
dotenv_stub.load_dotenv = lambda: None
util_stub = types.ModuleType("util")
util_stub.show_time = lambda _: __import__("datetime").datetime.now()
db_stub = types.ModuleType("db")
db_stub.DB = object
smtp_stub = types.ModuleType("smtp")

_import_temp_dir = tempfile.TemporaryDirectory()
os.environ["ATTACHMENTS_FOLDER"] = _import_temp_dir.name

sys.modules.setdefault("fitz", fitz_stub)
sys.modules.setdefault("dotenv", dotenv_stub)
sys.modules.setdefault("pandas", types.ModuleType("pandas"))
sys.modules.setdefault("db", db_stub)
sys.modules.setdefault("util", util_stub)
sys.modules.setdefault("smtp", smtp_stub)

import extraer_simple_v2

for module_name, module_stub in (
        ("fitz", fitz_stub),
        ("dotenv", dotenv_stub),
        ("pandas", sys.modules["pandas"]),
        ("db", db_stub),
        ("util", util_stub),
        ("smtp", smtp_stub)):
    if sys.modules.get(module_name) is module_stub:
        del sys.modules[module_name]


class _Pagina:
    def get_text(self):
        return "REMITO\nOTRA RAZON SOCIAL\nCUIT 00000000000"


class _Documento:
    def __init__(self):
        self.closed = False

    def __iter__(self):
        return iter([_Pagina()])

    def close(self):
        self.closed = True


class ExtraerInformacionPdfTest(unittest.TestCase):
    def test_mueve_a_error_si_no_coinciden_razon_social_o_cuit(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            origen = Path(temp_dir) / "remito.pdf"
            destino = Path(temp_dir) / "error"
            origen.touch()
            documento = _Documento()

            with patch.dict(os.environ, {"ERROR_FOLDER": str(destino)}), \
                    patch.object(extraer_simple_v2.fitz, "open", return_value=documento):
                resultado = extraer_simple_v2.extraer_informacion_pdf(str(origen))

            self.assertEqual(resultado, (None, None, []))
            self.assertTrue(documento.closed)
            self.assertFalse(origen.exists())
            self.assertTrue((destino / origen.name).exists())


if __name__ == "__main__":
    unittest.main()
