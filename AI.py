import os
import requests
from requests.exceptions import RequestException
from dotenv import load_dotenv
from flask import Flask, jsonify, request
from langchain_groq import ChatGroq

load_dotenv()

# Validação das variaveis de ambiente
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
NEWS_API_KEY = os.getenv("NEWS_API_KEY")

if not GROQ_API_KEY or not NEWS_API_KEY:
    raise ValueError("ERRO: Chaves de API não encontradas. Verifique o código do .env")

app = Flask(__name__)
app.json.ensure_ascii = False

try: # Tratamento inicialização da LLM. 
    llm = ChatGroq(
        api_key=GROQ_API_KEY,
        model="openai/gpt-oss-20b" 
    )
except Exception as e:
    raise RuntimeError(f"Erro ao inicializar o ChatGroq: {str(e)}")

def resumir_noticia(texto):
    """Retorna o resumo ou um dicionário de erro em caso de falha."""
    try:
        # Adição de timeout implícito dependendo da lib, mas o try/except garante a captura
        resposta = llm.invoke(f"Resuma essa notícia em até 3 frases de forma clara:\n\n{texto}")
        return resposta.content
    except Exception as e:
        print(f"[ERRO GROQ] Falha na requisição de resumo {e}")
        return None 

def buscar_noticias(tema):
    url = "https://newsapi.org/v2/everything"
    
    parametros = {
        "q": tema,
        "sortBy": "publishedAt",
        "language": "pt",
        "apiKey": NEWS_API_KEY
    }
    
    try:
        response = requests.get(url, params=parametros, timeout=10)
        response.raise_for_status()
        dados = response.json()
        
        if dados.get("status") != "ok":
            print(f"[ERRO API] Status não ok: {dados}")
            return None
            
        return dados.get("articles", [])
        
    except RequestException as e:
        print(f"Falha ao acessar News API: {e}")
        return None
    except ValueError as e:
        print(f"Falha no JSON: {e}")
        return None

@app.route('/api/noticias/resumo', methods=['POST'])
def get_noticias_resumidas():
    print(f"\n>>> REQUISIÇÃO RECEBIDA! Iniciando processamento... <<<") 
    dados_req = request.get_json()
    tema_buscado = dados_req.get("assunto", "Geral") if dados_req else "Geral"

    # Passa o tema para a função
    artigos = buscar_noticias(tema_buscado)
    
    # Validação da NEWS API. 
    if artigos is None:
        return jsonify({"erro": "Falha na comunicação com o provedor de notícias."}), 502
    # Validação do conteúdo retornado pela NEWS API.    python
    if not artigos:
        return jsonify({"mensagem": "Nenhuma notícia encontrada no período."}), 404

    resultados = []
    
    for artigo in artigos[:3]:
        titulo = artigo.get("title") or "Sem título"
        conteudo = artigo.get("content") or artigo.get("description")
        
        if conteudo:
            resumo = resumir_noticia(conteudo)
            if not resumo:
                resumo = "Erro interno: Falha ao gerar resumo com Inteligência Artificial."
        else:
            resumo = "Conteúdo original indisponível para gerar resumo."
            
        resultados.append({
            "titulo": titulo,
            "autor": artigo.get("author") or "Desconhecido",
            "link_original": artigo.get("url"),
            "resumo_ia": resumo
        })
        
    return jsonify({
        "status": "sucesso",
        "quantidade": len(resultados),
        "noticias": resultados
    }), 200

if __name__ == '__main__':
    app.run(debug=True,use_reloader=False, port=5050)
    