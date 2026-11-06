import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from openpyxl import Workbook

import extraer_factura


class MainExcelFormatErrorTest(unittest.TestCase):
    def test_sends_notification_when_database_connection_fails(self):
        connection_error = RuntimeError('No se pudo conectar a MariaDB')
        environment = {
            'ATTACHMENTS_FOLDER': 'attached',
            'EMAIL_TICKETS': 'tickets@example.com',
        }

        with patch.dict(os.environ, environment, clear=False), \
                patch.object(extraer_factura.db, 'DB', side_effect=connection_error), \
                patch.object(extraer_factura, 'safe_send_mail') as send_mail:
            extraer_factura.main()

        send_mail.assert_called_once()
        recipients, subject, plain_message, html_message = send_mail.call_args.args
        self.assertEqual(recipients, 'tickets@example.com')
        self.assertIn('Lectura de Factura', subject)
        self.assertIn('No se pudo conectar a MariaDB', plain_message)
        self.assertIn('No se pudo conectar a MariaDB', html_message)

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
