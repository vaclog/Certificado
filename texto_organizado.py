import fitz  # PyMuPDF



def resaltar_bloques_en_verde(ruta_pdf, salida_pdf):
    documento = fitz.open(ruta_pdf)
    for pagina_num in range(len(documento)):
        pagina = documento.load_page(pagina_num)
        texto_por_areas = pagina.get_text("dict")  # Extraer texto como un diccionario organizado

        # Dibujar un rectángulo verde alrededor de cada bloque
        for bloque in texto_por_areas["blocks"]:
            x0, y0, x1, y1 = bloque["bbox"]  # Coordenadas del bloque
            rect = fitz.Rect(x0, y0, x1, y1)
            # Dibujar el rectángulo en la página
            pagina.draw_rect(rect, color=(0, 1, 0), width=1)  # Color verde (RGB: 0, 1, 0)

    # Guardar el documento modificado
    rect = fitz.Rect(314, 45, 510, 80)
    pagina.draw_rect(rect, color=(1, 0, 0), width=2)
    documento.save(salida_pdf)
def obtener_texto_organizado(ruta_pdf):
    documento = fitz.open(ruta_pdf)
    for pagina_num in range(len(documento)):
        pagina = documento.load_page(pagina_num)
        texto_por_areas = pagina.get_text("dict")  # Extraer texto como un diccionario organizado

        # Mostrar el contenido del texto organizado por bloques
        for bloque in texto_por_areas["blocks"]:
            print(f"Bloque en coordenadas {bloque['bbox']}:")
            if 'lines' in bloque:  # Verificar si la clave 'lines' existe antes de acceder a ella
                for linea in bloque["lines"]:
                    for span in linea["spans"]:
                        print(f"  Texto: {span['text']} (Coordenadas: {span['bbox']})")
        print("-" * 40)

# Ruta al archivo PDF (ajusta según sea necesario)
ruta_pdf = "CAC01005448-ORG-RX0001-10144.pdf"
salida_pdf ="salida.pdf"
obtener_texto_organizado(ruta_pdf)
resaltar_bloques_en_verde(ruta_pdf, salida_pdf)

