



import pymupdf as fitz
import os

pdf_path = "CAC01005448-ORG-RX0001-10144.pdf"
images_path = 'images'

pdf_document = fitz.open(pdf_path)

# Ajustes de DPI y zoom
dpi = 300
zoom_factor = dpi / 72  # El PDF está normalmente en 72 DPI, así que esto lo ajusta
file_name = f"{images_path}/{os.path.splitext(os.path.basename(pdf_path))[0]}"
# Iterar a través de cada página
for page_number in range(pdf_document.page_count):
    page = pdf_document[page_number]

    # Ajuste de escala para simular el DPI
    matrix = fitz.Matrix(zoom_factor, zoom_factor)
    image = page.get_pixmap(matrix=matrix)

    # Guardar la imagen
    image_path = f"{file_name}_{page_number + 1}.png"
    image.save(image_path)
    print(f"Guardado {image_path} con DPI aproximado de {dpi}")