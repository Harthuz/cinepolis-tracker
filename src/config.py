import os
from dotenv import load_dotenv

# Carrega as variáveis do arquivo .env
load_dotenv()

# Configurações gerais
URL_ALVO = os.getenv("URL_ALVO", "https://www.cinepolis.com.br/filmes/1000046469-a-odisseia-imax/")
SELETOR_DATA = os.getenv("SELETOR_DATA", ".data-disponivel")
DATA_ALVO = os.getenv("DATA_ALVO", "20/07/2026")
INTERVALO_MINUTOS = int(os.getenv("INTERVALO_MINUTOS", "5"))
SESSION_DIR = os.getenv("SESSION_DIR", "./session")

# Configurações do Resend
RESEND_API_KEY = os.getenv("RESEND_API_KEY", "")
EMAIL_REMETENTE = os.getenv("EMAIL_REMETENTE", "onboarding@resend.dev")
EMAIL_DESTINO = os.getenv("EMAIL_DESTINO", "")

# Configurações do Pushover
PUSHOVER_API_TOKEN = os.getenv("PUSHOVER_API_TOKEN", "")
PUSHOVER_USER_KEY = os.getenv("PUSHOVER_USER_KEY", "")
