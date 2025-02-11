import fitz  # PyMuPDF
from PIL import Image
import pytesseract

# Configurar la ruta de Tesseract en Windows (si aplica)
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def convertir_pdf_a_imagenes(ruta_pdf):
    imagenes = []
    documento = fitz.open(ruta_pdf)
    for pagina_num in range(len(documento)):
        pagina = documento.load_page(pagina_num)
        matriz = fitz.Matrix(2, 2)  # Escalar la página (opcional para mejor resolución)
        pix = pagina.get_pixmap(matrix=matriz)
        imagen = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        imagenes.append(imagen)
    return imagenes
def buscar_valor_por_prefijo(texto, prefijo):
    inicio = texto.find(prefijo)
    if inicio != -1:
        fin = texto.find("\n", inicio + len(prefijo))
        return texto[inicio + len(prefijo):fin].strip()
    return None

def buscar_certificados(texto):
    import re
    certificados = re.findall(r'Certificado:\s+(\d+(?:\s*al\s*\d+)?)', texto)
    return certificados
def extraer_texto_ocr(imagen):
    return pytesseract.image_to_string(imagen)

# Ruta al archivo PDF
archivo_pdf = "CAC01005448-ORG-RX0001-10211.pdf"
imagenes = convertir_pdf_a_imagenes(archivo_pdf)

# Aplicar OCR a cada imagen y buscar campos específicos
for idx, imagen in enumerate(imagenes):
    texto_extraido = extraer_texto_ocr(imagen)
    # Buscar campos específicos (puedes adaptar las búsquedas)
    numero_remito = buscar_valor_por_prefijo(texto_extraido, "RX0001")
    fecha_remito = buscar_valor_por_prefijo(texto_extraido, "\nFecha de Factura\n")
    certificados = buscar_certificados(texto_extraido)

    print(f"Página {idx + 1}")
    print(f"Número de Remito: {numero_remito}")
    print(f"Fecha del Remito: {fecha_remito}")
    print(f"Números de Certificados: {', '.join(certificados)}")
    print("-" * 40)


