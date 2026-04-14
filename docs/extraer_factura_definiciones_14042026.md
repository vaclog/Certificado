# Definiciones extraer_factura

Fecha: 14/04/2026

## Objetivo
Migrar `extraer_factura.py` para que procese archivos `xlsx` del directorio de adjuntos en lugar de PDFs.

## Reglas definidas
- La factura puede venir en distintos formatos, pero debe guardarse normalizada como `0009-99999999`.
- El valor de `Numero de Serie` representa el certificado.
- El certificado se busca en base de datos sin transformación.
- Si el certificado viene vacío, se debe buscar por `nro_remito` y `certificado = ''`.
- Cuando el certificado viene vacío, el cálculo del valor unitario divide por `1`.
- Cuando una celda de certificado contiene varios valores separados por `,`, cada uno genera un registro.
- Cuando una parte contiene un rango con `/`, por ejemplo `45/47`, se expande a `45`, `46`, `47`.
- El valor unitario se calcula como `Total Pedido / cantidad de certificados resultantes para ese remito`.
- Un workbook normalmente trae una sola factura, pero si trae más de una se deben agrupar y procesar por `nro_factura`.
- Los encabezados del Excel pueden cambiar de posición, por lo que deben detectarse por nombre.

## Persistencia
- `cert_origen_facturacion` sigue recibiendo la misma estructura de datos usada por `db.CertificadoFactura(...)`.
- En `cert_origen_documentos.archivo` ya no se guarda el nombre físico del archivo; se guarda el número de factura normalizado.

## Validaciones
- Cada factura agrupada valida total calculado versus total acumulado desde `Total Pedido`.
- Si faltan columnas obligatorias o una fila no permite calcular certificados o remito, se debe informar inconsistencia.
