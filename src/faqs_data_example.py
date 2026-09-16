"""
Datos de ejemplo (ficticios) - Cabana Apicola Malka
=====================================================

"""

from langchain_core.documents import Document

faqs = [
    Document(page_content=(
        "Un producto de ejemplo A es una version inicial de un "
        "producto, todavia en preparacion. A diferencia del producto "
        "de ejemplo B, no pasa por un control de calidad previo, por "
        "lo que existe mayor riesgo de fallas. Por este proceso de "
        "control de calidad, el producto B cuesta mas que el A."
    )),
    Document(page_content=(
        "Enviamos el producto de ejemplo B a todo el pais durante la "
        "temporada de diciembre a febrero."
    )),
    Document(page_content=(
        "El producto de ejemplo A se envia a partir de noviembre, "
        "unicamente dentro de una zona geografica limitada. El envio "
        "se realiza a traves de un servicio expreso, con una "
        "restriccion de tiempo de viaje para asegurar la calidad del "
        "producto."
    )),
    Document(page_content=(
        "Exportamos el producto de ejemplo B al exterior a partir de "
        "mediados de marzo, a paises de una region especifica."
    )),
    Document(page_content=(
        "El precio del producto de ejemplo A es de $XXX. El pedido "
        "minimo es de N unidades para envio; si el cliente retira el "
        "pedido directamente en el establecimiento, no hay minimo de "
        "compra."
    )),
    Document(page_content=(
        "El pedido minimo del producto de ejemplo B para venta local "
        "es de N unidades para envio; si se retira en el "
        "establecimiento, no hay minimo de compra. Los precios varian "
        "segun la variedad."
    )),
    Document(page_content=(
        "Contacto de ejemplo: escribinos a ejemplo@empresa.com o "
        "comunicate al +54-9XXX-XXX-XXXX."
    )),
]