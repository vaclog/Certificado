from PIL import Image
import pytesseract
# Función para recortar y guardar las áreas específicas
def recortar_y_guardar_areas(imagen, coordenadas, output_folder="recortes"):
    import os
    os.makedirs(output_folder, exist_ok=True)
    for i, coords in enumerate(coordenadas):
        x, y, w, h = coords['x'], coords['y'], coords['w'], coords['h']
        recorte = imagen.crop((x, y, x + w, y + h))

        
        
        recorte_path = os.path.join(output_folder, f"recorte_{i}.png")
        recorte.save(recorte_path)
        imagen2 = Image.open(recorte_path)
        texto = pytesseract.image_to_string(imagen2, lang='spa', config='--psm 6')
        print(texto)
        print(f"Guardado: {recorte_path}")

# Definir coordenadas de las áreas a recortar
coordenadas = [
    {"texto": "10144", "x": 953, "y": 103, "w": 54, "h": 15},
    {"texto": "5/11/2024", "x": 813, "y": 137, "w": 106, "h": 18},
    {"texto": "5/11/2024", "x": 196, "y": 405, "w": 71, "h": 12},
    {"texto": "5/11/2024", "x": 346, "y": 405, "w": 71, "h": 12},
    {"texto": "041386", "x": 196, "y": 558, "w": 52, "h": 12}
]

# Cargar la imagen (reemplaza con la ruta de tu imagen generada)
ruta_imagen = "imagen_con_recuadros_especificos.png"
imagen = Image.open(ruta_imagen)

# Recortar y guardar las áreas
recortar_y_guardar_areas(imagen, coordenadas)

