
import os

from langchain.agents import create_agent
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langgraph.checkpoint.memory import InMemorySaver
from tools import consultar_disponibilidad, buscar_en_faqs, escalar_a_humano
from prompts import AGENT_SYSTEM_PROMPT

load_dotenv()

if not os.getenv("GOOGLE_API_KEY") or not os.getenv("GROQ_API_KEY"):
    raise RuntimeError("Falta GOOGLE_API_KEY o GROQ_API_KEY en tu .env")


llm = ChatGroq(model="openai/gpt-oss-120b", temperature=0.2)

tools = [buscar_en_faqs, consultar_disponibilidad, escalar_a_humano]

agent = create_agent(model=llm, tools=tools, system_prompt=AGENT_SYSTEM_PROMPT, checkpointer=InMemorySaver())


