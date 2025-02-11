import traceback



from dotenv import load_dotenv
import os
import logging
load_dotenv()

log_level = os.getenv('LOG_LEVEL', 'INFO')
# Configurar el nivel de logging dinámicamente
numeric_level = getattr(logging, log_level.upper(), logging.INFO)

logging.basicConfig(
    level=numeric_level,  # Nivel de registro mínimo que quieres mostrar
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
class Config:
    def __init__(self) -> None:
        self.db_host=os.getenv('DB_HOST')
        self.db_database=os.getenv('DB_NAME')
        self.db_user=os.getenv('DB_USER')
        self.db_password=os.getenv('DB_PASSWORD')
        self.smtp_host=os.getenv('SMTP_HOST')
        self.smtp_port=os.getenv('SMTP_PORT')
        self.smtp_user=os.getenv('SMTP_USER')
        self.smtp_password=os.getenv('SMTP_PASSWORD')
        self.sender_mail=os.getenv('SENDER_MAIL')