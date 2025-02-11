from PIL import Image, ImageDraw
import pytesseract
areas_interes = {
    "remito": {"x": 963, "y": 103, "w": 54, "h": 15},
    "fecha": {"x": 150, "y": 50, "w": 100, "h": 30},
    "certificado": {"x": 200, "y": 100, "w": 150, "h": 50}
}

def dibujar_cuadros(imagen, areas_interes):
    imagen_dibujada = imagen.copy()
    draw = ImageDraw.Draw(imagen_dibujada)
    for key, area in areas_interes.items():
        x, y, w, h = area["x"], area["y"], area["w"], area["h"]
        draw.rectangle([x, y, x + w, y + h], outline="red", width=2)
        draw.text((x, y - 10), key, fill="blue")  # Etiqueta con el nombre del área
    return imagen_dibujada

# Cargar la imagen
ruta_imagen = "imagen_con_recuadros.png"
imagen = Image.open(ruta_imagen)

# Dibujar los cuadros según el JSON proporcionado
imagen_dibujada = dibujar_cuadros(imagen, areas_interes)

# Mostrar la imagen con cuadros dibujados
imagen_dibujada.show() 