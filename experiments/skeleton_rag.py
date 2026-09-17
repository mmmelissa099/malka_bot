import os

from dotenv import load_dotenv
from langchain_core.documents import Document
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_groq import ChatGroq
from langchain_chroma import Chroma

from faqs_data import faqs


load_dotenv()

if not os.getenv("GROQ_API_KEY"):
    raise RuntimeError("Falta GROQ_API_KEY en tu .env")

 
embeddings = GoogleGenerativeAIEmbeddings(model="gemini-embedding-001") 


vectorstore = Chroma.from_documents(faqs, embeddings)

retriever = vectorstore.as_retriever(search_kwargs={"k": 6})


def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "Sos el asistente de Cabana Apicola Malka. Tus respuestas se "
            "envian directamente como mensajes de Instagram, asi que "
            "responde SIEMPRE en texto plano: sin tablas, sin negrita "
            "con asteriscos, sin listas con formato markdown ni ningun "
            "otro tipo de formato especial.\n\n"
            "Responde la pregunta del cliente usando SOLO la "
            "informacion del contexto de abajo. No agregues "
            "comparaciones, garantias ni conclusiones que el contexto "
            "no diga explicitamente. Si el contexto no alcanza para "
            "responder, decilo en vez de inventar.\n\n"
            "Se breve y directa: maximo 2 a 4 oraciones cortas, como "
            "en una conversacion real de chat, no un informe."
            "Para preguntas sobre a qué paises o zonas se hacen envios: si el "
            "destino que pregunta el cliente NO esta mencionado explicitamente "
            "en el contexto como un lugar cubierto, respondé que no hacen envios "
            "ahi. No asumas cobertura a partir de menciones generales como "
            "'exportacion internacional' sin una lista explicita de paises."
            "\n\nContexto:\n{context}",
        ),
        ("human", "{question}"),
    ]
)
llm = ChatGroq(
    model="openai/gpt-oss-120b", 
    temperature=0.2) 

parser = StrOutputParser()


rag_chain = (
    {"context": retriever | format_docs, "question": RunnablePassthrough()}
    | prompt
    | llm
    | parser   
)


if __name__ == "__main__":
    preguntas = [
        "Que dia es hoy?",
        "Porque conviene una reina antes que una celda real?",
        "Que variedad me conviene?",
        "Hacen envios a Chile?"
    ]
    for p in preguntas:
        print(f"Cliente: {p}")
        print(f"Bot:     {rag_chain.invoke(p)}\n")