import traceback
import inspect
import fitz  # PyMuPDF
import re
from dotenv import load_dotenv
import os
import logging

import imaplib
import email
from email.header import decode_header
import os
import util

import smtp
load_dotenv()

log_level = os.getenv('LOG_LEVEL', 'INFO')  # Valor por defecto 'INFO' si no está definido

# Configurar el nivel de logging dinámicamente
numeric_level = getattr(logging, log_level.upper(), logging.INFO)

logging.basicConfig(
    level=numeric_level,  # Nivel de registro mínimo que quieres mostrar
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

def preparar_search_criteria(subject_filter):
    filters = [f.strip() for f in subject_filter.split(',') if f.strip()]

    # Construir el criterio de búsqueda
    if len(filters) == 1:
        # Un solo filtro
        search_criteria = f'(UNSEEN SUBJECT "{filters[0]}")'
    elif len(filters) > 1:
        # Múltiples filtros, construir usando OR
        search_criteria = '(UNSEEN ' + ' '.join(f'(OR SUBJECT "{f1}" SUBJECT "{f2}")' for f1, f2 in zip(filters[:-1], filters[1:])) + ')'
    else:
        # Sin filtros
        search_criteria = '(UNSEEN)'

    return search_criteria.encode('utf-8')
def save_attachments(imap_server, email_user, email_password, folder_to_save="attachments"):
    # Connect to the server
    mail = imaplib.IMAP4_SSL(imap_server)
    mail.login(email_user, email_password)

    # Select the mailbox you want to check (e.g., inbox)
    mail.select("inbox")
    
    sender_filter = os.getenv('SENDER_FILTER', '')
    subject_filter = os.getenv('SUBJECT_FILTER', '')
    
    # Search for all emails (can modify to search only specific ones)
    #search_criteria = f'(UNSEEN FROM "{sender_filter}" SUBJECT "{subject_filter}")'
    search_criteria = f'(UNSEEN  SUBJECT "{subject_filter}")'
    for criteria in subject_filter.split(","):
        search_criteria = preparar_search_criteria(criteria)
    #search_criteria = f'(UNSEEN  SUBJECT "{subject_filter}")'
    
    
    
        status, messages = mail.search(None, search_criteria)  # Modify search criteria as needed

        # Convert messages to a list of email IDs
        email_ids = messages[0].split()

        for email_id in email_ids:
        # Fetch the email by ID
            status, msg_data = mail.fetch(email_id, '(RFC822)')

            for response_part in msg_data:
                if isinstance(response_part, tuple):
                    # Parse a byte email into a message object
                    msg = email.message_from_bytes(response_part[1])

                    # Decode email subject (if needed)
                    subject, encoding = decode_header(msg["Subject"])[0]
                    if isinstance(subject, bytes):
                        subject = subject.decode(encoding if encoding else "utf-8")
                    print(f"Subject: {subject}")

                    # If the email has attachments
                    if msg.is_multipart():
                        for part in msg.walk():
                            # Check if the part is an attachment
                            if part.get_content_disposition() == "attachment":
                                # Get the filename
                                filename = part.get_filename()
                                if filename:
                                    # Decode the filename if needed
                                    filename = decode_header(filename)[0][0]
                                    if isinstance(filename, bytes):
                                        filename = filename.decode()

                                    # Save the file
                                    filepath = os.path.join(folder_to_save, filename)
                                    with open(filepath, "wb") as f:
                                        f.write(part.get_payload(decode=True))
                                    print(f"Saved attachment: {filename}")

    # Logout from the account
    mail.logout()
def format_traceback(exc):
    raw_traceback = exc  # Obtener el traceback
    formatted_lines = []
    
    for line in raw_traceback.splitlines():
        if line.startswith("Traceback (most recent call last):"):
            formatted_lines.append("\n🌟 " + line)  # Título
        elif "File " in line and "line" in line and "in" in line:
            formatted_lines.append(f"📂 {line}")  # Archivos y líneas
        elif line.strip().startswith("raise") or line.strip().startswith("return"):
            formatted_lines.append(f"🔥 {line.strip()}")  # Excepciones importantes
        else:
            formatted_lines.append(f"    {line}")  # Detalles generales
        
    # Unir todo con saltos de línea
    return "\n".join(formatted_lines)
def main():
    try:
        
        start_time = util.show_time("Inicio")
        imap_server = os.getenv('IMAP_SERVER', '')  # Replace with your email server
        email_user = os.getenv('EMAIL_USER', '') 
        email_password = os.getenv('EMAIL_PASSWORD', '') 

        attachemets_folder = os.getenv('ATTACHMENTS_FOLDER', 'attachments')
        # Ensure the directory to save attachments exists
        os.makedirs(attachemets_folder, exist_ok=True)
        save_attachments(imap_server, email_user, email_password, attachemets_folder)
        end_time = util.show_time("Fin")
        print(f"Tiempo de ejecución: {end_time - start_time}")
    except Exception as e:
        
        description = traceback.format_exc()
        traceback.print_exc()
        print(description)
        frame = inspect.currentframe()
        function_name = inspect.getframeinfo(frame).function
        print(f"Error ocurrió en la función: {function_name}")
        print(f"Archivo: {inspect.getfile(frame)}")
        print(f"Error: {e}")

        html_msg = f"""<html>
        <body>
            <p>Error ocurrido en la función: {function_name}</p>
            <p>Archivo: {inspect.getfile(frame)}</p>
            <p>Error: {e}</p>
            <p>Descripción: {description}</p>
        </body>
        </html>"""
        smtp.smtp.SendMail(os.getenv('EMAIL_TICKETS', ''), f"Leer mails de certificados", f"{description} {frame} {function_name}",html_msg , "")

    
main(   )