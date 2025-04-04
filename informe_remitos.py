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
        nro_remito = ''
        remitos = dbase.remitosSinOperacion()

        
            
            
            
        if len(remitos) > 0:
            html_msg = f"""<html>
                <body>
                    <p>Los siguientes Remitos no tienen operaciones asociadas:</p>
                    <table border="1" style="border-collapse: collapse; width: 70%;">
                        <thead>
                            <tr>
                                <th style="padding: 8px; background-color: #00008B; color:white;">Nro Remito</th>
                                <th style="padding: 8px; background-color: #00008B; color:white;">Fecha Remito</th>
                                <th style="padding: 8px; background-color: #00008B; color:white;">Nro Factura</th>
                                <th style="padding: 8px; background-color: #00008B; color:white;">Fecha Factura</th>
                            </tr>
                        </thead>
                        <tbody>
                        """
            for r in remitos:
                nro_remito = r['nro_remito']
                print(f"Procesando remito {nro_remito}")

                fecha_factura = r['fecha_factura'].strftime('%d/%m/%Y') if r.get('fecha_factura') else ''
                html_msg += f"""<tr>
                                    <td style="padding: 8px;text-align: center;">{nro_remito}</td>
                                    <td style="padding: 8px;text-align: center;">{r['fecha_remito'].strftime('%d/%m/%Y')}</td>
                                    <td style="padding: 8px;text-align: center;">{r['nro_factura']}</td>
                                    <td style="padding: 8px;text-align: center;">{fecha_factura}</td>
                                </tr>"""

            html_msg += """
                        </tbody>
                    </table>
                </body>
            </html>"""
                        

            # destinatarios=os.getenv('EMAIL_INFORME_REMITO', '') + " , " + os.getenv('EMAIL_ADMINISTRACION', '')
            destinatarios = []
            destinatarios.append(os.getenv('EMAIL_INFORME_REMITO', ''))
            destinatarios.append(os.getenv('EMAIL_ADMINISTRACION', ''))
            #destinatarios=os.getenv('EMAIL_ADMINISTRACION', '')
            smtp.smtp.SendMail(destinatarios, f"Remitos sin operaciones asociadas","",html_msg , "")
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
        smtp.smtp.SendMail(os.getenv('EMAIL_TICKETS', ''), f"Error en informe de remitos sin operación", f"{description} {frame} {function_name}",html_msg , "")


main()