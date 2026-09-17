"""
Semana 1 - Primer chain con LangChain + Gemini
================================================

Objetivo de la semana: entender los tres bloques basicos de LangChain
(prompt template, modelo, output parser) encadenados con LCEL
(LangChain Expression Language, el operador "|").

Antes de correr este script:
1. Consegui tu API key gratis en https://aistudio.google.com/apikey
2. Copia .env.example a .env (en la raiz del proyecto) y pega tu key ahi
3. Desde la raiz del proyecto: 
4. Corre: python src/week1_simple_chain.py
"""

import os

from dotenv import load_dotenv
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

if not os.getenv("GOOGLE_API_KEY"):
    raise RuntimeError(
        "Falta GOOGLE_API_KEY. Crea un archivo .env con tu key "
        "(mira .env.example) o exportala como variable de entorno."
    )


llm = ChatGoogleGenerativeAI(model="gemini-3.6-flash", temperature=0.3)

prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "Sos el asistente virtual de Cabana Apicola Malka, un negocio "
            "familiar de productos apicolas (miel, propoleo, cera). "
            "Responde de forma breve, cordial y en espanol rioplatense. "
            "Si no sabes algo con certeza, decilo en vez de inventar.",
        ),
        ("human", "{mensaje}"),
    ]
)

parser = StrOutputParser()

chain = prompt | llm | parser


def responder(mensaje: str) -> str:
    """Punto de entrada reutilizable: dado un mensaje de un cliente, devuelve la respuesta del bot. Semana 4 lo va a envolver en un agente con RAG y tools; por ahora es un chain directo."""
    return chain.invoke({"mensaje": mensaje})


if __name__ == "__main__":
    mensajes_de_prueba = [
        "Hola! Que tipos de miel tienen?",
        "Hacen envios a Cordoba?",
        "Cual es la capital de Francia?"
    ]

    for mensaje in mensajes_de_prueba:
        respuesta = responder(mensaje)
        print(f"Cliente: {mensaje}")
        print(f"Bot:     {respuesta}\n")