"""
Semana 3 - Tool de disponibilidad
====================================

Objetivo: entender que es un tool en LangChain (una funcion que el
LLM decide si llamar o no - no se ejecuta siempre, a diferencia del
retriever del RAG), y armar uno real que compare la fecha de hoy
contra la disponibilidad vigente de cada producto.

Todavia NO se conecta a ningun agente/LLM - eso es la Semana 4. Por
ahora se prueba como pieza aislada, con .invoke() directo.

Completa los TODO vos misma.
"""

import datetime

from langchain_core.tools import tool

from stock_data import disponibilidad


@tool
def consultar_disponibilidad(producto: str) -> str:
        
    """
    Consulta si Malka esta tomando pedidos ahora mismo para un
    producto, o informa cuando se abre el proximo cupo si todavia
    no esta disponible.

    Args:
        producto: uno de "celdas", "reinas_nacional" o
            "reinas_exportacion".
    """

    if producto not in disponibilidad:
        return "No reconozco ese producto. Por favor, revisa la lista de productos disponibles: celdas, reinas_nacional, reinas_exportacion."
    elif datetime.date.today() >= datetime.date.fromisoformat(disponibilidad[producto]["proxima_fecha_disponible"]):
        return "El producto {} ya esta disponible para pedidos.".format(producto)
    else:
        proxima_fecha = disponibilidad[producto]["proxima_fecha_disponible"]
        return "El producto {} estará disponible a partir del {}.".format(producto, proxima_fecha)



if __name__ == "__main__":
    # Los tools de LangChain se prueban con .invoke() y un dict con
    # los argumentos - no se llaman como una funcion comun de Python
    # (consultar_disponibilidad("celdas") NO va a funcionar igual).
    print(consultar_disponibilidad.invoke({"producto": "celdas"}))
    print(consultar_disponibilidad.invoke({"producto": "reinas_nacional"}))
    print(consultar_disponibilidad.invoke({"producto": "reinas_exportacion"}))
    print(consultar_disponibilidad.invoke({"producto": "producto_que_no_existe"}))