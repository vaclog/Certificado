import traceback
import inspect
import fitz  # PyMuPDF
import re
from dotenv import load_dotenv
import os
import logging
import fnmatch
import shutil
import pandas as pd
from datetime import datetime
import db
import util
load_dotenv()
import smtp 

log_level = os.getenv('LOG_LEVEL', 'INFO')  # Valor por defecto 'INFO' si no está definido

# Configurar el nivel de logging dinámicamente
numeric_level = getattr(logging, log_level.upper(), logging.INFO)

logging.basicConfig(
    level=numeric_level,  # Nivel de registro mínimo que quieres mostrar
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)


def extraer_informacion_pdf(ruta_pdf):
    # Abrir el archivo PDF
    documento = fitz.open(ruta_pdf)
    texto_completo = ""
    for pagina in documento:
        texto_completo += pagina.get_text()

    # Expresiones regulares para buscar la información
    

    coordenadas_area_fecha = (310, 42, 510, 80) # Ajusta las coordenadas de acuerdo a tus necesidades
    x1, y1, x2, y2 = coordenadas_area_fecha
    area_fecha = fitz.Rect(x1, y1, x2, y2)  
    texto_area = pagina.get_textbox(area_fecha)

    rx_valor = re.search(r'RX0001\s*(\d+)', texto_area)
    rx_encontrado = rx_valor.group(1) if rx_valor else "No encontrado"
    fecha = re.search(r'\d{1,2}/\d{1,2}/\d{4}', texto_area)
    fechas = re.findall(r'\d{1,2}/\d{1,2}/\d{4}', texto_completo)
    fecha_encontrada = fecha.group() if fecha else "No encontrado"

    patron_certificado = r'Certificado\s+([A-Z0-9\s]+)\s*Certificado:\s*(\d+)'
    coincidencias = re.findall(patron_certificado, texto_completo)
    certificados = re.findall(r'(Certificado|Block):\s*([\d\s\w\/]+)', texto_completo)
    certificados_encontrados = []
    if len(certificados) >= 1:
        for certificado in certificados:
            valor = certificado[1].split('\n')[0]
            if valor:  # Esto verifica que no sea nulo o vacío
                certificados_encontrados.append(valor)
    
        
    documento.close()
    return rx_encontrado, fecha_encontrada, certificados_encontrados


def buscar_pdfs_con_nombre_similar(directorio, patron="CAC01005448-ORG-RX0001-*.pdf"):
    """
    Busca archivos PDF en un directorio cuyo nombre coincida con un patrón dado.

    Parámetros:
    - directorio (str): Ruta del directorio donde buscar los archivos.
    - patron (str): Patrón de búsqueda para coincidir con los nombres de archivo (por defecto busca nombres similares a "CAC01005448-ORG-RX0001-*.pdf").

    Retorna:
    - List[str]: Una lista de rutas completas a los archivos que coinciden con el patrón.
    """
    archivos_pdf = []
    # Recorre los archivos en el directorio especificado
    for archivo in os.listdir(directorio):
        if fnmatch.fnmatch(archivo, patron):
            # Agrega la ruta completa del archivo a la lista
            archivos_pdf.append(os.path.join(directorio, archivo))
    return archivos_pdf


def mover_archivo(nombre_archivo, directorio_destino):
    """
    Mueve un archivo a un directorio específico.

    Parámetros:
    - nombre_archivo (str): Ruta completa del archivo que deseas mover.
    - directorio_destino (str): Ruta del directorio destino.

    Retorna:
    - str: Ruta completa del archivo movido en el nuevo directorio.
    """
    # Verifica si el archivo existe
    if not os.path.isfile(nombre_archivo):
        raise FileNotFoundError(f"El archivo '{nombre_archivo}' no existe.")
    
    # Verifica si el directorio destino existe, si no, lo crea
    if not os.path.exists(directorio_destino):
        os.makedirs(directorio_destino)

    # Construye la ruta del nuevo archivo
    nombre_archivo_nuevo = os.path.join(directorio_destino, os.path.basename(nombre_archivo))

    # Mueve el archivo
    shutil.move(nombre_archivo, nombre_archivo_nuevo)

    return nombre_archivo_nuevo


def convertir_fecha(fecha_str):
    try:
        # Separar la fecha en partes
        dia, mes, anio = fecha_str.split('/')
        # Formatear la fecha en 'yyyy-mm-dd'
        return f"{anio}-{mes}-{dia}"
    except ValueError:
        return "Formato de fecha inválido"

def main():
    
    try:
        start_time = util.show_time("Inicio")
        attachments_folder = os.getenv('ATTACHMENTS_FOLDER', '') 
        # Rutas a los archivos PDF (ajusta según sea necesario)
        archivos_pdf = buscar_pdfs_con_nombre_similar(attachments_folder, patron="*RX*.pdf")
        filas = []
        dbase = db.DB()
        
        for archivo in archivos_pdf:
            rx, fecha, certificados = extraer_informacion_pdf(archivo)
            print(f"Archivo: {archivo}")
            print(f"RX0001: {rx}")
            print(f"Primera Fecha: {fecha}")
            fecha_remito = convertir_fecha(fecha)  # Convertir la fecha
            nro_remito = rx

            if len(certificados) > 0:
                for certificado in certificados:
                    print(f"Certificados: {util.expandir_rango(certificado)}")  # Expandir el rango de certificados y mostrarlos separados por comascertificados}")
                    print("-" * 40)
                
                    for cert in util.expandir_rango(certificado):
                        fecha_alta = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        
                        
                        dbase.CertificadoInsert((nro_remito, fecha_remito, cert, fecha_alta, 'proceso de alta'))
            else:
                print("No se encontraron certificados en el PDF.")
                fecha_alta = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                dbase.CertificadoInsert((nro_remito, fecha_remito, '', fecha_alta, 'proceso de alta'))

            
            # Mover el archivo a la carpeta "procesados"
            mover_archivo(archivo, os.getenv('PROCESSED_FOLDER', ''))
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
        smtp.smtp.SendMail(os.getenv('EMAIL_TICKETS', ''), f"Lectura de Remito {archivo}", f"{description} {frame} {function_name}",html_msg , "")

main()