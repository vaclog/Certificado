import sys
import types
import unittest
from unittest.mock import patch


dotenv_stub = types.ModuleType("dotenv")
dotenv_stub.load_dotenv = lambda: None
sys.modules.setdefault("dotenv", dotenv_stub)

import smtp


class NormalizeRecipientsTest(unittest.TestCase):
    def test_separa_destinatarios_dentro_de_una_lista(self):
        recipients = smtp.smtp._normalize_recipients([
            "Celula4@vaclog.com,asagula@vaclog.com",
            "administracion@vaclog.com",
        ])

        self.assertEqual(recipients, [
            "Celula4@vaclog.com",
            "asagula@vaclog.com",
            "administracion@vaclog.com",
        ])

    def test_envia_cada_destinatario_por_separado(self):
        server = _SmtpServer()
        client = smtp.Smtp("smtp.example.com", 465, "sender@example.com", "secret", "Robot")

        with patch.object(smtp.ssl, "create_default_context"), \
                patch.object(smtp.smtplib, "SMTP_SSL", return_value=server):
            client.SendMail(
                "Celula4@vaclog.com,asagula@vaclog.com",
                "Informe",
                "Mensaje",
                "",
            )

        self.assertEqual(
            [recipients for _, recipients, _ in server.deliveries],
            [["Celula4@vaclog.com"], ["asagula@vaclog.com"]],
        )


class _SmtpServer:
    def __init__(self):
        self.deliveries = []

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        return False

    def login(self, user, password):
        pass

    def sendmail(self, sender, recipients, message):
        self.deliveries.append((sender, recipients, message))
        return {}


if __name__ == "__main__":
    unittest.main()
