import os
import requests
from dotenv import load_dotenv
from flask import Flask, jsonify
from langchain_groq import ChatGroq

load_dotenv()

app = Flask(__name__)

app.json.ensure_ascii = False # conserta a resposta json para UTF-8

llm = ChatGroq(
    api_key=os.getenv("GROQ_API_KEY"),
    model="openai/gpt-oss-20b"
)

def resumir_noticia(texto):
    # Função para chamar a API do Groq e retornar o resumo.
    try:
        resposta = llm.invoke(f"Resuma essa notícia em até 3 frases de forma clara:\n\n{texto}")
        return resposta.content
    except Exception as e:
        return f"Erro ao gerar resumo: {str(e)}"

def buscar_noticias():
    # Busca as notícias de esportes na News API.
    api_key = os.getenv("NEWS_API_KEY")
    url = f"https://newsapi.org/v2/everything?q=Palmeiras&from=2026-08-24&to=2026-08-25&language=pt&apiKey={api_key}"
    
    response = requests.get(url)
    if response.status_code == 200:
        dados = response.json()
        return dados.get("articles", [])
    return []

@app.route('/api/noticias/resumo', methods=['GET'])
def get_noticias_resumidas():
    artigos = buscar_noticias()
    
    if not artigos:
        return jsonify({"erro": "Não foi possível buscar as notícias"}), 500

    resultados = []
    
    for artigo in artigos[:3]:
        titulo = artigo.get("title", "Sem título")
        conteudo = artigo.get("content") or artigo.get("description")
        
        if conteudo:
            resumo = resumir_noticia(conteudo)
        else:
            resumo = "Conteúdo original indisponível para gerar resumo."
            
        resultados.append({
            "titulo": titulo,
            "autor": artigo.get("author", "Desconhecido"),
            "link_original": artigo.get("url"),
            "resumo_ia": resumo
        })
        
    return jsonify({"status": "sucesso", "quantidade": len(resultados), "noticias": resultados})


if __name__ == '__main__':
    app.run(debug=True, port=5000)
    