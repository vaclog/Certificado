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




def extraer_cabecera(pagina, texto_completo):
    coordenadas_area_fecha = (310, 42, 510, 80) # Ajusta las coordenadas de acuerdo a tus necesidades
    x1, y1, x2, y2 = coordenadas_area_fecha
    area_fecha = fitz.Rect(x1, y1, x2, y2)  
    texto_area = pagina.get_textbox(area_fecha)

    rx_valor = re.search(r'\b\s*(\d{4}-\d+)', texto_area)
    rx_encontrado = rx_valor.group(1) if rx_valor else "No encontrado"
    fecha = re.search(r'\d{1,2}/\d{1,2}/\d{4}', texto_area)
    fechas = re.findall(r'\d{1,2}/\d{1,2}/\d{4}', texto_completo)
    fecha_encontrada = fecha.group() if fecha else "No encontrado"

    return rx_encontrado, fecha_encontrada

def extraer_clave(clave, texto_area):
    patron = r'(' + '|'.join([clave]) + r')'
    patrones = re.split(patron, texto_area)
    items = []
    for i  in range(1, len(patrones), 2):
        clave = patrones[i]
        contenido = patrones[i + 1] if i + 1 < len(patrones) else ""
        if clave == 'Certificado':
            if "MERCOSUR COD" in contenido:
                aux = contenido.strip().split('\n')
                if len(aux) == 7:
                    lineas = [f"{aux[0]}", aux[1], aux[2], aux[3], aux[4], aux[5].strip(), aux[6].strip()]
                elif (len(aux) == 8):
                    lineas = [f"{aux[0]}{aux[1]}", aux[2], aux[3], aux[4], aux[5], aux[6].strip(), aux[7]]

                elif (len(aux)  >= 9):
                    lineas = [f"{aux[0]}", aux[1], aux[2], aux[3], aux[4], aux[5].strip(), aux[6].strip()]
            else:
                lineas = contenido.strip().split('\n')[:7]
        else:
            if clave == 'Block':
                aux = contenido.strip().split('\n')[:10]
                lineas = [f"{clave} {aux[0]}", aux[1], aux[2], aux[3], aux[4],  '',  aux[5]]
            else:
                lineas = contenido.strip().split('\n')[:5]
                lineas.insert(0, clave)
                lineas.insert(5, '')
        
        items.append(lineas) 
    return items
def extraer_informacion_pdf(ruta_pdf):
    # Abrir el archivo PDF
    documento = fitz.open(ruta_pdf)
    texto_completo = ""
    items = []
    texto_documento = ""
    for pagina in documento:

        texto_completo = pagina.get_text()
        texto_documento += texto_completo
        rx_encontrado, fecha_encontrada = extraer_cabecera(pagina, texto_completo)
        items_pattern = r"CANT.(.*?)TOTAL:"
        coordenadas_area_items = (10, 300, 800, 1200)
        x1, y1, x2, y2 = coordenadas_area_items
        area_items = fitz.Rect(x1, y1, x2, y2)  
        texto_area = pagina.get_textbox(area_items)

        claves = ['Block', 'Certificado', 'VISADOS', ]

        for clave in claves:
            items.extend(extraer_clave( clave, texto_area))
    patron = r'TOTAL:\s*([\s\S]*?)(\d{1,3}(?:[.,]\d{3})*[.,]\d{2})'
    total = re.search(patron, texto_documento)
    total_value = None
    if total is None:
        raise util.PDFInconsistente("No se pudo encontrar el TOTAL: en el PDF.")
    else:
        total_value = util.convert_decimal_from_spanish_to_english_format(total.group(2))
    
    documento.close()   

    return rx_encontrado, fecha_encontrada, total_value, items


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
        archivos_pdf = buscar_pdfs_con_nombre_similar(attachments_folder, patron="*FC*-*.pdf")
        filas = []
        dbase = db.DB()
        
        for archivo in archivos_pdf:
            try:
                rx, fecha, total, certificados = extraer_informacion_pdf(archivo)
                print(f"Archivo: {archivo}")
                print(f"FACTURA: {rx}")
                print(f"Fecha: {fecha}")
                fecha_factura = convertir_fecha(fecha)  # Convertir la fecha
                nro_factura = rx
                total_calculado = 0
                values = []
                print("-" * 40)
                ##if dbase.existeFactura(nro_factura):
                ##    print(f"La factura {nro_factura} ya existe en la base de datos.")
                ##else:
                for certificado in certificados:
                    #print(f"Certificados: {expandir_rango(certificado[5])}")  # Expandir el rango de certificados y mostrarlos separados por comascertificados}")
                    print(certificado)
                    tipo = certificado[0]
                    cant = int(certificado[1])
                    total_calculado += util.convert_decimal_from_spanish_to_english_format  (certificado[2])
                    
                    subtotal = util.convert_decimal_from_spanish_to_english_format(certificado[2])
                    precio_unitario = util.convert_decimal_from_spanish_to_english_format(certificado[3])
                    cert=certificado[5].strip()
                    nro_remito = int(certificado[6].split('-')[1].strip()) if isinstance(certificado[6], str) and '-' in certificado[6].split('-')[0].strip() else   certificado[6].split('-')[1].strip()
                    if tipo == 'VISADOS' or 'Block' in tipo:
                        precio_unitario = precio_unitario * cant
                    
                    if cert == '':
                        fecha_update = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        
                        values.append([nro_remito, cert, fecha_factura, nro_factura, precio_unitario, fecha_update,'proceso de facturación', tipo])
                    for ce in util.expandir_rango(cert):
                        fecha_update = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        
                        values.append([nro_remito, ce, fecha_factura, nro_factura, precio_unitario, fecha_update,'proceso de facturación', tipo])

                    
                
                
                total_calculado, remitos_no_encontrados = dbase.CertificadoFactura(values, total)
                print(f"Total: {total}")
                print(f"Remitos no encontrados: {remitos_no_encontrados}")
                dbase.CertificadoDocumentoInsertOrUpdate([os.path.basename(archivo), nro_factura,  total, total_calculado])
                
                if len(remitos_no_encontrados) > 0:
                    html_msg_admin = f"""<html>
                    <body>
                        <p>Para la factura: <strong>{nro_factura}</strong></p
                        <p>del archivo: {os.path.basename(archivo)}</p>
                        <p>Los siguientes Remitos no fueron encontrados en la base de datos de certificados de orgien:</p>
                        <ul>
                            {''.join([f'<li>{remito}</li>' for remito in remitos_no_encontrados])}
                        </ul>
                        <p>Por favor reenviar los mails con los remitos a la casilla <strong>{os.getenv('EMAIL_USER', '')}</strong> para su procesamiento</p>

                    </body>
                    </html>"""
                    raise util.PDFInconsistente(f"Los remitos no fueron encontrados para la factura {nro_factura}.")
                # Mover el archivo a la carpeta "procesados"
                
                if total != total_calculado:
                    html_msg_admin = f"""<html>
                    <body>
                        <p>Para la factura: <strong>{nro_factura}</strong></p
                        <p>del archivo: {os.path.basename(archivo)}</p>
                        <p>El total en el PDF no coincide con el total calculado:</p>
                        <ul>
                            <li>Total PDF: {total}</li>
                            <li>Total Calculado: {total_calculado}</li>
                        </ul>
                        <p>Por favor reenviar los mails con los remitos a la casilla <strong>{os.getenv('EMAIL_USER', '')}</strong> para su procesamiento</p>

                    </body>
                    </html>"""
                    
                    raise util.PDFInconsistente("El total en el PDF no coincide con el total calculado.")
                else:
                    mover_archivo(archivo, os.getenv('PROCESSED_FOLDER', ''))
                    
            except util.PDFInconsistente as e:
                
                print(f"Error: {e}")
                smtp.smtp.SendMail(os.getenv('EMAIL_ADMINISTRACION', ''), f"Inconsistencia en procesar Factura CAC ce Cert Origen {nro_factura}", f"{e}", html_msg_admin, "")
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