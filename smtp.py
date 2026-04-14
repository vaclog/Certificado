import smtplib, ssl
import config
import re

from email.mime.text import MIMEText
from email import encoders
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.utils import formataddr

class Smtp:

    def __init__ (self, host, port, user, password, sender_mail):
        
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.sender_mail = sender_mail
              
    
    
        print(host)
        
            
    def _normalize_recipients(self, to):
        if isinstance(to, list):
            recipients = to
        else:
            recipients = re.split(r'[;,]', str(to or ''))

        return [recipient.strip() for recipient in recipients if recipient and recipient.strip()]

    def SendMail(self, to, subject, plain_message="", html_message="<html></html>", imagename=""):
        context = ssl.create_default_context()
        recipients = self._normalize_recipients(to)
        if not recipients:
            raise ValueError('No hay destinatarios configurados para el correo.')
        
        message = MIMEMultipart("alternative")
        message["Subject"] = subject
        message["From"] = formataddr((self.sender_mail, self.user))
        message["To"] = ", ".join(recipients)
        
        if plain_message:
            part1 = MIMEText(plain_message, "plain", "utf-8")
            message.attach(part1)

        if html_message:
            part2 = MIMEText(html_message, "html", "utf-8")
            message.attach(part2)   
        
        # part1=MIMEText(text, 'plain')
             
        # message.attach(part1)
        if (len(imagename)> 0):
            try:
                with open(imagename, 'rb') as attachment:
                    part3 = MIMEBase("application", "octet-stream")
                    part3.set_payload(attachment.read())

                encoders.encode_base64(part3)
                part3.add_header(
                    "Content-Disposition",
                    f"attachment; filename={imagename}",
                )
                message.attach(part3)
            except FileNotFoundError:
                print(f"Error: Archivo '{imagename}' no encontrado.")
        
        with smtplib.SMTP_SSL(self.host, self.port, context=context) as self.server:
        #with smtplib.SMTP(self.host, 587) as self.server:
            self.server.login(self.user, self.password)
            
            self.server.sendmail(self.user, recipients, message.as_string())
config = config.Config()   
smtp = Smtp( config.smtp_host , config.smtp_port ,
            config.smtp_user , config.smtp_password, config.sender_mail )

