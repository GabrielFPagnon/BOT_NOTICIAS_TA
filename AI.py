import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq

load_dotenv()

llm = ChatGroq(
    api_key=os.getenv("GROQ_API_KEY"),
    model="llama-3.1-8b-instant"
)

def resumir_noticia(texto):
    resposta = llm.invoke(f"Resuma essa notícia em até 3 frases:\n\n{texto}")
    return resposta.content