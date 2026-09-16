
import os

from dotenv import load_dotenv
from langchain_core.chat_history import BaseChatMessageHistory, InMemoryChatMessageHistory
from langchain_core.messages import BaseMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnableLambda, RunnablePassthrough
from langchain_core.runnables.history import RunnableWithMessageHistory
from pydantic import BaseModel, Field
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_groq import ChatGroq
from langchain_chroma import Chroma

from faqs_data import faqs

load_dotenv()

if not os.getenv("GOOGLE_API_KEY"):
    raise RuntimeError("Falta GOOGLE_API_KEY en tu .env")

embeddings = GoogleGenerativeAIEmbeddings(model="gemini-embedding-001")
vectorstore = Chroma.from_documents(faqs, embeddings)
retriever = vectorstore.as_retriever(search_kwargs={"k": 4})


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
            "no diga explicitamente. Para preguntas sobre a que paises "
            "o zonas se hacen envios: si el destino que pregunta el "
            "cliente NO esta mencionado explicitamente en el contexto "
            "como un lugar cubierto, respondé que no hacen envios ahi. "
            "Si el contexto no alcanza para responder, decilo en vez "
            "de inventar.\n\n"
            "Se breve y directa: maximo 2 a 4 oraciones cortas, como "
            "en una conversacion real de chat, no un informe."
            "\n\nContexto:\n{context}",
        ),
        MessagesPlaceholder(variable_name="history"),
        ("human", "{question}"),
    ]
)

llm = ChatGroq(model="openai/gpt-oss-120b", temperature=0.2)
parser = StrOutputParser()


rag_chain = (
    {
        "context": (lambda x: x["question"]) | retriever | format_docs,
        "question": lambda x: x["question"],
        "history": lambda x: x["history"],
    }
    | prompt
    | llm
    | parser
)

class InMemoryHistory(BaseChatMessageHistory, BaseModel):
    """In memory implementation of chat message history."""

    messages: list[BaseMessage] = Field(default_factory=list)

    def add_messages(self, messages: list[BaseMessage]) -> None:
        """Add a list of messages to the store"""
        self.messages.extend(messages)

    def clear(self) -> None:
        self.messages = []

store = {}


def get_session_history(session_id: str) -> InMemoryChatMessageHistory:
    if session_id not in store:
        store[session_id] = InMemoryHistory()
    return store[session_id]




chain_with_memory = RunnableWithMessageHistory(
    rag_chain,
    get_session_history,
    input_messages_key="question",
    history_messages_key="history",
)


if __name__ == "__main__":
    session = "cliente_demo_1"

    preguntas = [
        "Vendan paquetes de abejas?"
    ]

    for p in preguntas:
        respuesta = chain_with_memory.invoke(
            {"question": p},
            config={"configurable": {"session_id": session}},
        )
        print(f"Cliente: {p}")
        print(f"Bot:     {respuesta}\n")