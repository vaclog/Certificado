import unittest
import sys
from contextlib import redirect_stdout
from io import StringIO
from unittest.mock import MagicMock, patch

sys.modules.setdefault('mariadb', MagicMock())
import db


class DBConnectionTest(unittest.TestCase):
    def test_constructor_propagates_connection_error(self):
        connection_error = RuntimeError('No se pudo conectar a MariaDB')

        with patch.object(db.mariadb, 'connect', side_effect=connection_error):
            with redirect_stdout(StringIO()):
                with self.assertRaises(RuntimeError) as raised:
                    db.DB()

        self.assertIs(raised.exception, connection_error)


if __name__ == '__main__':
    unittest.main()
