"""
Datos de disponibilidad - PLANTILLA PUBLICA
=============================================
Version de ejemplo de stock_data.py, el archivo que usa la tool
consultar_disponibilidad. El archivo real NO se versiona: las fechas de
apertura de cada temporada son informacion comercial.

Para correr el proyecto:
    cp src/stock_data_example.py src/stock_data.py

Las fechas de abajo son INVENTADAS y corresponden al criadero ficticio
del archivo faqs_data_example.py. Estan elegidas para que la demo
muestre los dos comportamientos de la tool: celdas ya disponibles, y
reinas con fecha de apertura futura.

Los valores se actualizan A MANO a medida que se llenan los cupos de
cada temporada - no se calculan solos. Formato: YYYY-MM-DD.

Las claves del diccionario son los unicos valores validos para el
parametro 'producto' de consultar_disponibilidad: si se agrega o se
renombra una, hay que actualizar tambien el docstring de la tool en
src/tools.py.
"""

disponibilidad = {
    "celdas": {
        "proxima_fecha_disponible": "2020-10-01",
    },
    "reinas_nacional": {
        "proxima_fecha_disponible": "2099-12-01",
    },
    "reinas_exportacion": {
        "proxima_fecha_disponible": "2099-03-15",
    },
}