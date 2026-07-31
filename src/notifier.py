import urllib.request
import urllib.parse
import resend
from src.config import (
    URL_ALVO,
    ENABLE_RESEND,
    RESEND_API_KEY,
    EMAIL_REMETENTE,
    EMAIL_DESTINO,
    PUSHOVER_API_TOKEN,
    PUSHOVER_USER_KEY
)

# Configura o Resend API Key
if RESEND_API_KEY:
    resend.api_key = RESEND_API_KEY

def enviar_notificacao(data_desejada, datas_disponiveis):
    """Envia um e-mail de alerta utilizando o Resend (desativado por padrão a menos que ENABLE_RESEND=true)."""
    if not ENABLE_RESEND or not RESEND_API_KEY or not EMAIL_DESTINO:
        return False
    
    try:
        html_content = f"""
        <h1>🎫 Ingressos Disponíveis!</h1>
        <p>A data desejada <strong>{data_desejada}</strong> que você estava monitorando foi encontrada!</p>
        <p><strong>Datas disponíveis mapeadas atualmente:</strong> {', '.join(datas_disponiveis)}</p>
        <p>Acesse o site agora para garantir seu ingresso: <a href="{URL_ALVO}">{URL_ALVO}</a></p>
        """
        
        response = resend.Emails.send({
            "from": f"Bot de Ingressos <{EMAIL_REMETENTE}>",
            "to": EMAIL_DESTINO,
            "subject": f"🚨 Ingressos Disponíveis - Data Encontrada: {data_desejada}",
            "html": html_content
        })
        print(f"📧 Notificação de e-mail enviada com sucesso! Resposta: {response}")
        return True
    except Exception as e:
        print(f"❌ Erro ao enviar e-mail via Resend: {e}")
        return False

import time

def enviar_notificacao_pushover(titulo, mensagem, priority=0, sound="pushover"):
    """Envia uma notificação para o celular via Pushover com retentativas em caso de falha de rede/DNS."""
    if not PUSHOVER_API_TOKEN or not PUSHOVER_USER_KEY:
        print("⚠️ Configurações do Pushover ausentes no arquivo .env. Não foi possível enviar a notificação.")
        return False
        
    url = "https://api.pushover.net/1/messages.json"
    
    payload = {
        "token": PUSHOVER_API_TOKEN,
        "user": PUSHOVER_USER_KEY,
        "title": titulo,
        "message": mensagem,
        "priority": priority,
        "sound": sound
    }
    
    # Parâmetros adicionais para Prioridade de Emergência (priority=2):
    if priority == 2:
        payload["retry"] = 30
        payload["expire"] = 3600
        payload["sound"] = "persistent" # Toca som de alarme persistente
        
    data = urllib.parse.urlencode(payload).encode("utf-8")
    
    # Tenta até 3 vezes em caso de oscilação temporária de DNS ou rede
    max_tentativas = 3
    for tentativa in range(1, max_tentativas + 1):
        try:
            req = urllib.request.Request(url, data=data)
            with urllib.request.urlopen(req, timeout=15) as response:
                res_body = response.read().decode("utf-8")
                print(f"🔊 Notificação do Pushover enviada! Resposta: {res_body}")
                return True
        except Exception as e:
            print(f"⚠️ [Tentativa {tentativa}/{max_tentativas}] Falha temporária no envio Pushover: {e}")
            if tentativa < max_tentativas:
                time.sleep(2)
            else:
                print(f"❌ Erro final ao enviar notificação via Pushover: {e}")
                return False
