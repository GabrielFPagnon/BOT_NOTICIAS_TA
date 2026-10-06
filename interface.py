import streamlit as st
import requests

# Configuração da página
st.set_page_config(page_title="Simulador - WhatsApp Bot",)
st.title("Bot de Notícias")
st.caption("Digite um assunto para ver a curadoria e resumos da IA.")

# Histórico da conversa
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Olá! Sobre qual assunto você quer ler as notícias hoje?"}
    ]

# Mostra as mensagens antigas
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Caixa de texto para o usuário digitar
if prompt := st.chat_input("Ex: Inteligência artificial, Economia, Esporte..."):
    
    # Salva e mostra a mensagem do usuário
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Processamento do Assistente
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        message_placeholder.markdown("Buscando e resumindo as notícias...")

        try:
            # 1. Faz a requisição POST para o seu back-end Flask
            url_backend = "http://localhost:5050/api/noticias/resumo"
            payload = {"assunto": prompt}
            
            resposta = requests.post(url_backend, json=payload)
            
            # 2. Verifica se a resposta foi bem sucedida
            if resposta.status_code == 200:
                dados = resposta.json()
                noticias = dados.get("noticias", [])
                
                if noticias:
                    # Formata a resposta para parecer uma mensagem de WhatsApp
                    texto_final = f"Aqui estão as notícias fresquinhas sobre *{prompt}*:\n\n"
                    
                    for i, noti in enumerate(noticias, 1):
                        texto_final += f"*{i}. {noti['titulo']}*\n"
                        texto_final += f" {noti['resumo_ia']}\n"
                        texto_final += f" [Ler matéria completa]({noti['link_original']})\n\n"
                else:
                    texto_final = "Não encontrei nenhuma notícia sobre esse assunto hoje. "
            else:
                texto_final = "Ops, parece que você inseriu um assunto inválido. Tente de novo."
                
        except Exception as e:
            texto_final = f" Erro de conexão. Servidores não respondem. Detalhes: {e}"

        # Exibe a resposta final e salva no histórico
        message_placeholder.markdown(texto_final)
        st.session_state.messages.append({"role": "assistant", "content": texto_final})