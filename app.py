import os
from dotenv import load_dotenv
from twilio.rest import Client

load_dotenv()

account_sid = os.getenv('TWILIO_ACCOUNT_SID')
auth_token = os.getenv('TWILIO_AUTH_TOKEN')
twilio_number = os.getenv('TWILIO_PHONE_NUMBER')
meu_numero = os.getenv('MY_PHONE_NUMBER')

client = Client(account_sid, auth_token)

def enviar_sms():
    try:
        message = client.messages.create(
            body="Olá! Esta é uma mensagem de teste da API do Twilio.",
            from_=twilio_number,
            to=meu_numero
        )
        print(f"Mensagem enviada com sucesso! SID: {message.sid}")
    except Exception as e:
        print(f"Erro ao enviar mensagem: {e}")

if __name__ == "__main__":
    enviar_sms()