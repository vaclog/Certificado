import traceback
import inspect

from dotenv import load_dotenv
import os
import logging

import pandas as pd
from datetime import datetime
import db
import util
import smtp


load_dotenv()

log_level = os.getenv('LOG_LEVEL', 'INFO')  # Valor por defecto 'INFO' si no está definido

# Configurar el nivel de logging dinámicamente
numeric_level = getattr(logging, log_level.upper(), logging.INFO)

logging.basicConfig(
    level=numeric_level,  # Nivel de registro mínimo que quieres mostrar
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)


def main():
    try:
        start_time = util.show_time("Inicio")
        dbase = db.DB()
        nro_factura = ''
        facturas = dbase.listFacturasSinProcesar()

        for r in facturas:
            
            nro_factura = r['nro_factura']
            print(f"Procesando factura {nro_factura}")
            parametros =  '{"nro_factura":'+ '"' + f"{r['nro_factura']}" + '"}'
                          
            if dbase.esPlanificable(nro_factura) == 0:
                print(f"Factura {nro_factura} fue planificada en el robot")
                dbase.insertRobotTarea( parametros)
        end_time = util.show_time("Fin")
        print(f"Tiempo de ejecución: {end_time - start_time}")
    except Exception as e:
        description = traceback.format_exc()
        traceback.print_exc()
        print(description)
        frame = inspect.currentframe()
        function_name = inspect.getframeinfo(frame).function
        print(f"Error ocurrió en la función: {function_name}")
        print(f"Archivo: {inspect.getfile(frame)}")
        print(f"Error: {e}")

        html_msg = f"""<html>
        <body>
            <p>Error ocurrido en la función: {function_name}</p>
            <p>Archivo: {inspect.getfile(frame)}</p>
            <p>Error: {e}</p>
            <p>Descripción: {description}</p>
        </body>
        </html>"""
        smtp.smtp.SendMail(os.getenv('EMAIL_TICKETS', ''), f"Procesando factura numero {nro_factura}", f"{description} {frame} {function_name}",html_msg , "")


main()