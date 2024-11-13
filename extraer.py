import traceback
import fitz  # PyMuPDF
from PIL import Image
import pytesseract
from dotenv import load_dotenv
import os
import logging
load_dotenv()

log_level = os.getenv('LOG_LEVEL', 'INFO')  # Valor por defecto 'INFO' si no está definido

# Configurar el nivel de logging dinámicamente
numeric_level = getattr(logging, log_level.upper(), logging.INFO)

logging.basicConfig(
    level=numeric_level,  # Nivel de registro mínimo que quieres mostrar
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
def expandir_rango(rango_str):
    if "al" in rango_str:
        partes = rango_str.split("al")
        inicio = int(partes[0].strip())
        fin = int(partes[1].strip())
        return [str(num).zfill(len(partes[0].strip())) for num in range(inicio, fin + 1)]
    return [rango_str.strip()]

def convertir_pdf_a_imagenes(ruta_pdf):
    imagenes = []
    documento = fitz.open(ruta_pdf)
    for pagina_num in range(len(documento)):
        pagina = documento.load_page(pagina_num)
        matriz = fitz.Matrix(2, 2)  # Escalar la página para mejor resolución
        pix = pagina.get_pixmap(matrix=matriz)
        imagen = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        imagenes.append(imagen)
    return imagenes

def extraer_texto_por_area(imagen, area, key):
    # Recorta la imagen según las coordenadas especificadas en el área
    x, y, w, h = area["x"], area["y"], area["w"], area["h"]
    recorte = imagen.crop((x , y, x + w, y + h ))
    # Aplicar OCR solo al área recortada
    
    if key in ["remito", "certificado"]: 
        texto = pytesseract.image_to_string(recorte, lang='spa', config='--psm 10 --oem 3 -c tessedit_char_whitelist=abcdefghijklmnopqrstuvwxyz0123456789')
    else: 
        
        texto = pytesseract.image_to_string(recorte, lang='spa', config='--psm 6 -c tessedit_char_whitelist=0123456789/')
    
    return texto.strip()

# Definir las áreas de interés
areas_interes = {
    "remito": {"x": 953, "y": 103, "w": 54, "h": 15},
    "fecha": {"x": 795, "y": 130, "w": 130, "h": 30},
    "certificado": {"x": 193, "y": 558, "w": 150, "h": 12}
}


def main():
    try:
        
        # Rutas a los archivos PDF (ajusta según sea necesario)
        archivos_pdf = [
            "CAC01005448-ORG-RX0001-10144.pdf",  # Ajusta según tus rutas
            "CAC01005448-ORG-RX0001-10211.pdf",
            "CAC01005448-ORG-RX0001-10171.pdf"
        ]

        # Procesar cada archivo PDF y extraer texto de las áreas de interés
        for archivo_pdf in archivos_pdf:
            imagenes = convertir_pdf_a_imagenes(archivo_pdf)
            for i, imagen in enumerate(imagenes):
                print(f"\nArchivo: {archivo_pdf}, Página: {i + 1}")
                for key, area in areas_interes.items():
                    texto = extraer_texto_por_area(imagen, area, key)
                    if key in ["remito", "fecha"]: 
                        print(f"{key.capitalize()}: {texto}")
                    else:  
                        print(f"{key.capitalize()}: {', '.join(expandir_rango(texto))}")

    except Exception as e:
        traceback.print_exc()
        print(f"Error: {e}")

main()