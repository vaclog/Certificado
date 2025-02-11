
from datetime import datetime
from tqdm import tqdm


class PDFInconsistente(Exception):
    def __init__(self, *args) -> None:
        super().__init__(*args)

        
# Función para mostrar la hora actual
def show_time(label):
    now = datetime.now()
    print(f"{label}: {now.strftime('%Y-%m-%d %H:%M:%S')}")
    return now


def replace_pipe_with_hash(text):
    
    return text.replace('|', '#')


def convert_decimal_to_spanish_format(number):
    # Convertir el número a string y reemplazar el punto por una coma
    if isinstance(number, (int, float)):
        return str(number).replace('.', ',')
    return number  # Devuelve el valor original si no es un número

def convert_decimal_from_spanish_to_english_format(number):
    # Convertir el número a string y reemplazar el punto por una coma
    if number.rfind(',') > number.rfind('.'):
            formato = "europeo"
    else:
        formato = "anglosajón"
    if isinstance(number, (str)) and formato == "europeo":
        parte_entera, parte_decimal = number.split(',')
        str_number = parte_entera.replace('.', '')
        
        return float(f"{str_number}.{parte_decimal}")
    elif isinstance(number, (str)) and formato == "anglosajón":
        parte_entera, parte_decimal = number.split('.')
        str_number = parte_entera.replace(',', '')
        
        return float(f"{str_number}.{parte_decimal}")
    return number  # Devuelve el valor original si no es un número
