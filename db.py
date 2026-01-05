import mariadb
import config as setting
import traceback
import util
import json
cnf = setting.Config()
class DB:
    def __init__(self):
        self.server = cnf.db_host
        self.db = cnf.db_database
        self.user = cnf.db_user
        self.password  = cnf.db_password
        try:
            self.conn = mariadb.connect(host=self.server,
                                        port=3306, 
                                   user=self.user, 
                                   password=self.password, 
                                   database=self.db)		
            
            self.cursor = self.conn.cursor()
            
        
        except Exception as e:
            print(traceback.format_exc())
            print(e)

    def CertificadoInsert(self, data):
        
        sentence=f"""
                    INSERT INTO cert_origen_facturacion (
                                nro_remito, fecha_remito, certificado, 
                                fecha_alta, user_id_last_update, 
                                facturar_flag
                                ) VALUES (%s, %s, %s, %s, %s, 'S')
                    """

        check_query = """
            SELECT COUNT(*) FROM cert_origen_facturacion
            WHERE nro_remito = %s 
             AND anulado = 'N'
            """
       

        
        with self.conn.cursor(dictionary=True) as cursor:
            if ( len(data[2]) == 0 ):
                check_query += " AND certificado = ''"
                cursor.execute(check_query, (data[0], ))
            else:
                check_query += " AND certificado = %s"
                cursor.execute(check_query, (data[0], data[2]))
            
            exists = cursor.fetchone()['COUNT(*)']
            if exists== 0:
                cursor.execute(sentence, data)
            
            self.conn.commit()
    def agregarRemitoNoEncontrado(self, lista, valor):
        """
        Agrega un valor a la lista si no existe ya en ella.

        Args:
            lista (list): La lista donde se va a agregar el valor.
            valor (str): El valor que se quiere agregar.

        Returns:
            bool: True si el valor se agregó, False si ya existía.
        """
        if valor not in lista:
            lista.append(valor)
            return True
        return False
    #([nro_remito, ce, fecha_factura, nro_factura, precio_unitario, fecha_update,'proceso de alta'])
    #  0,          1,   2,            3,           4,               5            6
    def CertificadoFactura(self, values, total):
        total_calculado = 0
        remitos_no_encontrados=[]
        try:
            with self.conn.cursor(dictionary=True) as cursor:
                for data in values:
                    try:
                        nro_factura = data[3]
                        fecha_factura = data[2]
                        user_id_last_update = data[6]
                        fecha_update = data[5]
                        precio_unitario = data[4]
                        tipo = data[7]
                        nro_remito = data[0]
                        sentence=f"""
                                    UPDATE cert_origen_facturacion SET 
                                            nro_factura = '{nro_factura}',
                                            fecha_factura = '{fecha_factura}',
                                            user_id_last_update = '{user_id_last_update}',
                                            fecha_update = '{fecha_update}',
                                            precio_unitario = {precio_unitario},
                                            tipo = '{tipo}'
                                            
                                    WHERE nro_remito = {nro_remito} 
                                    AND anulado = 'N'
                                
                                """
                        
                        if ( len(data[1]) == 0 ):
                            sentence += " " # en los casos de BLOCK y VISADO no indica el numero de certificado en la factura pero si en el remito
                        #    raise util.PDFInconsistente(f"ERROR: NO SE UBICO EN LA TABLA el certificado {data[1]} del remito {data[0]}")
                            
                            

                        else:
                            certificado = data[1]
                            sentence += f""" AND certificado = '{certificado}' """
                            
                        #print(sentence) 
                        resp_db= cursor.execute(sentence)

                        
                        self.conn.commit()
                        if cursor.rowcount == 1 or cursor.affected_rows == 1:
                            total_calculado += data[4]
                            
                            #print("Encontrados ", data[0], data[1], data[2], data[3], data[4], data[5], data[6])
                        else:
                            
                            raise util.PDFInconsistente(f"ERROR: NO SE UBICO EN LA TABLA el certificado {data[1]} del remito {data[0]}")
                        
                    except util.PDFInconsistente as e:  
                        self.agregarRemitoNoEncontrado(remitos_no_encontrados, data[0])  
                        print(e)
                
                return total_calculado, remitos_no_encontrados
                    #self.conn.rollback()
                    
        except util.PDFInconsistente as e:
            print(e)
    def CertificadoDocumentoInsertOrUpdate(self, data):
        
        

        sentence_insert=f"""
                    INSERT INTO cert_origen_documentos(
                                archivo, nro_factura, total_factura, total_calculado
                                ) VALUES (%s, %s, %s, %s)
                    """

        sentence_update=f"""
                    UPDATE cert_origen_documentos SET
                                 
                                nro_factura = %s, 
                                total_factura=%s,
                                total_calculado = %s
                    WHERE archivo = %s
                      AND anulado = 'N'
                    """
        check_query = f"""
            SELECT COUNT(*) as cantidad FROM cert_origen_documentos
            WHERE archivo = %s 
              AND anulado = 'N'
            """
        

        
        with self.conn.cursor(dictionary=True) as cursor:
            cursor.execute(check_query, (data[0],))
            exists = cursor.fetchone()['cantidad']
            if exists== 0:
                cursor.execute(sentence_insert, data)
            else:
                cursor.execute(sentence_update, (data[1], data[2], data[3], data[0]))
            
            self.conn.commit()

    def insertRobotTarea(self, parametros):
        param = json.loads(parametros)
        try:
            sentence_tarea = f"""INSERT INTO robot_tarea ( proceso, estado, parametros, fecha_alta, user_id )
                            VALUES ( 'certificado_origen', 0, ?, CURDATE(), 'certificado')

                            """
            sentence_documento = f"""UPDATE cert_origen_documentos SET
                                     planificado_robot = 'S'
                                     WHERE nro_factura = %s
                                       AND anulado = 'N'
                                     """
            with self.conn.cursor(dictionary=True) as cursor:
                cursor.execute(sentence_tarea, [f"{parametros}"])
                cursor.execute(sentence_documento, (param['nro_factura'],))
                self.conn.commit()
        except Exception as e:
            self.conn.rollback()
            print(traceback.format_exc())
            print(e) 
    
    def listFacturasSinProcesar(self):
        sentence_facturas = f"""SELECT nro_factura
                                  FROM cert_origen_documentos
                                WHERE subido_a_dux = 'N'
                                  AND planificado_robot = 'N'
                                  AND total_factura = total_calculado
                                  AND anulado = 'N'
                            """
        with self.conn.cursor(dictionary=True) as cursor:
            cursor.execute(sentence_facturas)

            facturas = cursor.fetchall()

            return facturas
    def existeFactura(self, nro_factura):
        sentence_facturas = f"""SELECT nro_factura
                                  FROM cert_origen_documentos
                                WHERE nro_factura = '{nro_factura}'
                                  AND anulado = 'N'
                            """
        with self.conn.cursor(dictionary=True) as cursor:
            cursor.execute(sentence_facturas)

            facturas = cursor.fetchall()

            return  len(facturas) > 0

    def esPlanificable(self, nro_factura):
        sentence = f""" SELECT count(*) as cantidad_sin_operacion 
                          FROM cert_origen_facturacion
                         WHERE numop = 0
                           AND nro_factura = ?
                           AND facturar_flag = 'S'
                           AND anulado = 'N'
                    """
        with self.conn.cursor(dictionary=True) as cursor:
            cursor.execute(sentence, [nro_factura])

            resp = cursor.fetchone()

            return resp['cantidad_sin_operacion']
    
    def remitosSinOperacion(self):
        sentence = f""" SELECT distinct nro_remito, fecha_remito, nro_factura, fecha_factura
                          FROM cert_origen_facturacion
                         WHERE numop = 0
                           and fecha_remito >= CURDATE() - INTERVAL 60 DAY AND fecha_remito < CURDATE()
                           and fecha_remito >= '2025-04-01'
                           and facturar_flag = 'S'
                           AND anulado = 'N'
                    """
        with self.conn.cursor(dictionary=True) as cursor:
            cursor.execute(sentence)

            resp = cursor.fetchall()

            return resp