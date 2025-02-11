import fitz  # PyMuPDF
from PIL import Image
import pytesseract

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

def buscar_palabra_y_coordenadas(imagen, palabra_buscar):
    # Usar pytesseract para obtener datos de cada palabra detectada
    datos = pytesseract.image_to_data(imagen, lang='spa', output_type=pytesseract.Output.DICT)
    
    # Buscar la palabra y obtener sus coordenadas
    coordenadas = []
    for i, palabra in enumerate(datos['text']):
        if palabra.strip() == palabra_buscar:
            x, y, w, h = datos['left'][i], datos['top'][i], datos['width'][i], datos['height'][i]
            coordenadas.append({"palabra": palabra, "x": x, "y": y, "w": w, "h": h})
    
    return coordenadas

# Ruta al archivo PDF cargado por el usuario
archivo_pdf = "CAC01005448-ORG-RX0001-10144.pdf"
imagenes = convertir_pdf_a_imagenes(archivo_pdf)

# Buscar la palabra "RX0001" en la primera imagen del PDF convertido
coordenadas_rx0001 = buscar_palabra_y_coordenadas(imagenes[0], "10144")

# Mostrar las coordenadas encontradas
print(coordenadas_rx0001)
