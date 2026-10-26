"""
Datos del negocio - PLANTILLA PUBLICA
=======================================
Version de ejemplo de faqs_data.py, el archivo que alimenta el RAG. El
archivo real NO se versiona porque contiene informacion comercial de
Cabana Apicola Malka (precios, minimos, condiciones de venta).

Para correr el proyecto:
    cp src/faqs_data_example.py src/faqs_data.py

Los datos de abajo son INVENTADOS: corresponden a un criadero ficticio
llamado "Apiario del Valle". Estan escritos de forma coherente para que
la demo se entienda sin tener los datos reales, pero ninguna cifra,
fecha ni condicion se corresponde con las de Malka.

Al reemplazarlos, conviene conservar dos cosas que no son adorno:
- El documento resumen del final, que existe para que las preguntas
  amplias ("que venden?") recuperen algo util en vez de fragmentos
  sueltos.
- La aclaracion explicita cuando un producto se parece a otro por el
  nombre (abajo, el hibrido Valcit frente a la raza Carnica pura).
Ambas resuelven problemas reales de recuperacion documentados en
docs/observaciones/semana2.md.
"""

from langchain_core.documents import Document

faqs = [
    Document(page_content=(
        "Una celda real es una reina en desarrollo, todavia sin nacer, "
        "que se instala directamente en la colmena. A diferencia de la "
        "reina fecundada, la celda real no pasa por un control de "
        "calidad previo, por lo que existe el riesgo de que nazca "
        "deformada o no nazca. Ese control de calidad es lo que explica "
        "que una reina fecundada sea bastante mas cara que una celda "
        "real."
    )),
    Document(page_content=(
        "Enviamos reinas fecundadas a todo el pais durante la temporada "
        "de diciembre a febrero."
    )),
    Document(page_content=(
        "Actualmente tenemos celdas reales disponibles. Para concretar "
        "un pedido de celdas, una persona del equipo coordina la "
        "cantidad, la fecha y la forma de entrega."
    )),
    Document(page_content=(
        "Las celdas reales se envian unicamente dentro de la provincia "
        "de Cordoba. El envio se realiza por servicio expreso. Las "
        "celdas se despachan 24 horas antes de la eclosion, por lo que "
        "el viaje debe durar menos de 24 horas para asegurar que la "
        "reina nazca correctamente."
    )),
    Document(page_content=(
        "Las consultas sobre exportacion, envios al exterior y destinos "
        "fuera de la Argentina las responde una persona del equipo, "
        "porque los destinos, los plazos, las cantidades y las "
        "condiciones dependen de cada pais y de la normativa vigente en "
        "cada temporada."
    )),
    Document(page_content=(
        "El precio de cada celda real es de $1.000. El pedido minimo es "
        "de 20 unidades para envio; si el cliente retira el pedido "
        "directamente en el apiario, no hay minimo de compra."
    )),
    Document(page_content=(
        "El pedido minimo de reinas fecundadas para venta local (dentro "
        "de la Argentina) es de 5 unidades para envio; si se retira en "
        "el apiario, no hay minimo de compra. Los precios varian segun "
        "la raza: las reinas Italianas cuestan $4.000 por unidad, y las "
        "reinas Valcit y Buckfast cuestan $5.000 por unidad."
    )),
    Document(page_content=(
        "Las reinas Italianas (Ligustica) del Apiario del Valle "
        "provienen de una linea seleccionada desde 1995. Se caracterizan "
        "por alta prolificidad, baja tendencia a enjambrar y "
        "temperamento docil."
    )),
    Document(page_content=(
        "Las reinas Valcit son un hibrido propio del Apiario del Valle: "
        "resultado de un cruzamiento entre la raza Carnica y zanganos "
        "Italianos. IMPORTANTE: el apiario NO vende reinas Carnicas "
        "puras como producto - unicamente se ofrece el hibrido Valcit. "
        "Las Valcit se adaptan bien a climas calidos con flujos de "
        "nectar breves y se destacan por su longevidad."
    )),
    Document(page_content=(
        "Las reinas Buckfast son multihibridas, originadas en la "
        "seleccion desarrollada por el Hermano Adam en la Abadia de "
        "Buckfast. Presentan gran variabilidad de color y son "
        "especialmente rusticas."
    )),
    Document(page_content=(
        "El apiario realiza controles sanitarios periodicos sobre sus "
        "colonias y las exportaciones cuentan con certificacion "
        "sanitaria oficial."
    )),
    Document(page_content=(
        "Las reinas se exportan por via aerea desde el aeropuerto "
        "internacional, con asistencia de un agente de cargas "
        "especializado en transporte de animales vivos y embalajes que "
        "cumplen las normas internacionales correspondientes."
    )),
    Document(page_content=(
        "Ademas de reinas y celdas reales, ofrecemos nucleos de 5 "
        "cuadros (con cria, abejas adheridas, miel y una reina marcada) "
        "y paquetes de abejas de 1,2 kg (aproximadamente 9.000 obreras y "
        "una reina fecundada). Ambos productos se entregan unicamente en "
        "el establecimiento, no se envian."
    )),
    Document(page_content=(
        "Dado que no se puede garantizar completamente el transporte de "
        "animales vivos, se envia una reina adicional sin cargo cada 20 "
        "reinas compradas."
    )),
    Document(page_content=(
        "Para una buena aceptacion de las reinas, cualquier tratamiento "
        "sanitario contra varroa debe haber terminado al menos 10 dias "
        "antes de introducir las reinas, y no debe reiniciarse hasta al "
        "menos 21 dias despues, porque esos productos enmascaran las "
        "feromonas de la reina."
    )),
    Document(page_content=(
        "Para consultas, pueden escribir a contacto@apiariodelvalle.test "
        "o comunicarse al +54-9351-000-0000."
    )),
    Document(page_content=(
        "El Apiario del Valle fue fundado en 1995 como emprendimiento "
        "familiar dedicado a la cria de reinas. Dicta cursos de cria y "
        "participa de exposiciones apicolas."
    )),
    Document(page_content=(
        "El apiario exporta reinas desde 2005, cuando comenzo a enviar a "
        "paises de la region."
    )),
    Document(page_content=(
        "Como caracteristica general de las razas: las Italianas tienen "
        "coloracion rubia y rinden mejor en climas frescos. Las Valcit "
        "son oscuras y convienen en climas calidos. Las Buckfast tienen "
        "color variable y se adaptan a condiciones diversas."
    )),
    Document(page_content=(
        "La temporada de produccion comienza aproximadamente a mediados "
        "de septiembre, aunque la fecha exacta varia cada anio segun las "
        "condiciones climaticas."
    )),
    Document(page_content=(
        "La jalea real es el alimento que producen las abejas obreras "
        "para alimentar a las larvas y transformarlas en reinas. Es un "
        "insumo central en la cria."
    )),
    Document(page_content=(
        "El proceso de cria de una reina dura aproximadamente un mes: "
        "comienza cuando la reina madre pone huevos en un cuadro "
        "especial, sigue con el desarrollo de las larvas alimentadas con "
        "jalea real hasta formar la celda real, y culmina cuando la "
        "nueva reina nace y es fecundada."
    )),
    Document(page_content=(
        "Que productos tiene el Apiario del Valle: vendemos cuatro tipos "
        "de productos - celdas reales, reinas fecundadas (en tres razas: "
        "Italiana, Buckfast y Valcit), nucleos de 5 cuadros y paquetes "
        "de abejas de 1,2 kg. Las razas de reinas que manejamos son "
        "Italiana, Buckfast y Valcit (nuestro hibrido propio) - no "
        "vendemos otras razas. Cada producto tiene su propia zona de "
        "envio, precio y minimo de compra."
    )),
]