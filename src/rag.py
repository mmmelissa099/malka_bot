import os
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma
from faqs_data import faqs

embeddings = GoogleGenerativeAIEmbeddings(model="gemini-embedding-001") 

vectorstore = Chroma.from_documents(faqs, embeddings)

retriever = vectorstore.as_retriever(search_kwargs={"k": 6})


def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)
