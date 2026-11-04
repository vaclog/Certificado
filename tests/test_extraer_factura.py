import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from openpyxl import Workbook

import extraer_factura


class MainExcelFormatErrorTest(unittest.TestCase):
    def test_moves_each_invalid_excel_to_error_folder_and_continues(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            attachments = Path(temp_dir) / 'attached'
            error_folder = Path(temp_dir) / 'error'
            attachments.mkdir()

            for filename in ('factura_1.xlsx', 'factura_2.xlsx'):
                workbook = Workbook()
                worksheet = workbook.active
                worksheet.append(['encabezado inesperado'])
                worksheet.append(['dato'])
                workbook.save(attachments / filename)

            environment = {
                'ATTACHMENTS_FOLDER': str(attachments),
                'ERROR_FOLDER': str(error_folder),
                'EMAIL_ADMINISTRACION': 'administracion@example.com',
            }
            with patch.dict(os.environ, environment, clear=False), \
                    patch.object(extraer_factura.db, 'DB'), \
                    patch.object(extraer_factura, 'safe_send_mail'):
                extraer_factura.main()

            self.assertEqual(
                sorted(path.name for path in error_folder.iterdir()),
                ['factura_1.xlsx', 'factura_2.xlsx'],
            )
            self.assertEqual(list(attachments.iterdir()), [])


if __name__ == '__main__':
    unittest.main()
