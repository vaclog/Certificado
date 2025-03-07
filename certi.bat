
set LOG_FILE=C:\Users\desarrollo\Certificado\remitos.log

echo "Starting" > %LOG_FILE% 2>&1
call C:\Users\desarrollo\miniconda3\Scripts\activate.bat Certificado

python C:\Users\desarrollo\Certificado\leer_mail.py >> %LOG_FILE% 2>&1

python C:\Users\desarrollo\Certificado\extraer_simple.py >> %LOG_FILE% 2>&1