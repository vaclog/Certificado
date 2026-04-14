from datetime import datetime
from tqdm import tqdm
import re


class PDFInconsistente(Exception):
    def __init__(self, *args) -> None:
        super().__init__(*args)


# FunciÃ³n para mostrar la hora actual
def show_time(label):
    now = datetime.now()
    print(f"{label}: {now.strftime('%Y-%m-%d %H:%M:%S')}")
    return now


def replace_pipe_with_hash(text):
    return text.replace('|', '#')


def convert_decimal_to_spanish_format(number):
    # Convertir el nÃºmero a string y reemplazar el punto por una coma
    if isinstance(number, (int, float)):
        return str(number).replace('.', ',')
    return number  # Devuelve el valor original si no es un nÃºmero


def convert_decimal_from_spanish_to_english_format(number):
    # Convertir el nÃºmero a string y reemplazar el punto por una coma
    if number.rfind(',') > number.rfind('.'):
        formato = "europeo"
    else:
        formato = "anglosajÃ³n"
    if isinstance(number, (str)) and formato == "europeo":
        parte_entera, parte_decimal = number.split(',')
        str_number = parte_entera.replace('.', '')

        return float(f"{str_number}.{parte_decimal}")
    elif isinstance(number, (str)) and formato == "anglosajÃ³n":
        parte_entera, parte_decimal = number.split('.')
        str_number = parte_entera.replace(',', '')

        return float(f"{str_number}.{parte_decimal}")
    return number  # Devuelve el valor original si no es un nÃºmero


def normalizar_numero_certificado(valor):
    if valor is None:
        return ''

    certificado = str(valor).strip()
    if not certificado:
        return ''

    partes = certificado.rsplit('-', 1)
    if len(partes) == 2:
        izquierda = partes[0].strip()
        derecha = partes[1].strip()
        if izquierda.isdigit() and derecha.isdigit():
            return derecha

    return certificado


def expandir_rango(rango_str):
    retornar = []
    rango_str = normalizar_numero_certificado(rango_str)
    if "al" in rango_str:
        partes = rango_str.split("al")
        inicio = int(partes[0].strip())
        fin = int(partes[1].strip())
        return [str(num).zfill(len(partes[0].strip())) for num in range(inicio, fin + 1)]
    elif "y" in rango_str:
        partes = rango_str.split("y")
        return [partes[0].strip(), partes[1].strip()]
    elif "/" in rango_str:
        partes = rango_str.split("/")
        for parte in partes:
            retornar.append(normalizar_numero_certificado(parte))
        return retornar
    elif "-" in rango_str:
        return [rango_str]
    else:
        resultado = re.findall(r'\d+', rango_str.strip())
        return resultado
