from langchain_core.tools import tool
from stock_data import disponibilidad
from rag import retriever, format_docs
import datetime



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
    

@tool
def buscar_en_faqs(pregunta: str) -> str:
    """
    Busca en las FAQs de Malka la respuesta a la pregunta del cliente.
    Este tool es útil para preguntas sobre productos, precios, envíos,
    diferencias entre celda real y reina fecundada, razas, etc.
    """
    return format_docs(retriever.invoke(pregunta))


@tool
def escalar_a_humano(motivo: str) -> str:
    """
    Usa este tool cuando el cliente pida explicitamente hablar con
    una persona, cuando no puedas resolver su consulta con
    buscar_en_faqs ni consultar_disponibilidad, o cuando pida una
    recomendacion de que producto o raza le conviene (eso requiere
    criterio que no esta disponible en las FAQs).
    """
    print(f"[ESCALADO] motivo: {motivo}")
    return (
        "No tengo informacion suficiente para responder eso. "
        "En breve te va a contestar una persona del equipo."
    )
