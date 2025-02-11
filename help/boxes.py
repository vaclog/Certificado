import fitz  # PyMuPDF
from PIL import Image, ImageDraw
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

def extraer_texto_y_boxes_ocr(imagen):
    # Obtener resultados de OCR con datos de cajas delimitadoras
    datos = pytesseract.image_to_data(imagen, lang='spa', output_type=pytesseract.Output.DICT)
    return datos

def dibujar_recuadros_y_guardar_coordenadas(imagen, datos_ocr, textos_buscar, ruta_salida_txt):
    # Crear una copia de la imagen para dibujar
    imagen_dibujada = imagen.copy()
    draw = ImageDraw.Draw(imagen_dibujada)
    coordenadas_texto = []

    # Dibujar rectángulos para textos específicos y guardar coordenadas
    n_boxes = len(datos_ocr['text'])
    for i in range(n_boxes):
        texto_actual = datos_ocr['text'][i].strip()
        if texto_actual in textos_buscar and int(datos_ocr['conf'][i]) > 0:  # Considerar solo detecciones con cierta confianza
            (x, y, w, h) = (datos_ocr['left'][i], datos_ocr['top'][i], datos_ocr['width'][i], datos_ocr['height'][i])
            draw.rectangle([x, y, x + w, y + h], outline="red", width=2)
            draw.text((x, y - 10), texto_actual, fill="red")  # Etiqueta con el texto encontrado
            coordenadas_texto.append(f"Texto: '{texto_actual}' | Coordenadas: (x: {x}, y: {y}, w: {w}, h: {h})")
    
    # Guardar las coordenadas en un archivo de texto
    with open(ruta_salida_txt, "w", encoding="utf-8") as file:
        for linea in coordenadas_texto:
            file.write(linea + "\n")
    
    return imagen_dibujada

# Ruta al archivo PDF cargado por el usuario
archivo_pdf = "CAC01005448-ORG-RX0001-10144.pdf"
imagenes = convertir_pdf_a_imagenes(archivo_pdf)

# Aplicar OCR y dibujar los recuadros para textos específicos
datos_ocr = extraer_texto_y_boxes_ocr(imagenes[0])
textos_buscar = ["10144", "5/11/2024", "041386"]
output_txt_path = "coordenadas_textos_especificos.txt"
imagen_con_recuadros = dibujar_recuadros_y_guardar_coordenadas(imagenes[0], datos_ocr, textos_buscar, output_txt_path)

# Guardar la imagen resultante
output_image_path = "imagen_con_recuadros_especificos.png"
imagen_con_recuadros.save(output_image_path)

output_image_path, output_txt_path  # Devolver las rutas de los archivos guardados
