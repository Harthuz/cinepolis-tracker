import os
from dotenv import load_dotenv

# Carrega as variáveis do arquivo .env
load_dotenv()

# Configurações gerais
URL_ALVO = os.getenv("URL_ALVO", "https://www.cinepolis.com.br/filmes/1000046469-a-odisseia-imax/")
SELETOR_DATA = os.getenv("SELETOR_DATA", ".data-disponivel")
DATA_ALVO = os.getenv("DATA_ALVO", "2026-08-12")
CINEMA_ALVO = os.getenv("CINEMA_ALVO", "Cinépolis JK Iguatemi (SP)")
INTERVALO_MINUTOS = int(os.getenv("INTERVALO_MINUTOS", "5"))
SESSION_DIR = os.getenv("SESSION_DIR", "./session")

# Configurações do Resend
RESEND_API_KEY = os.getenv("RESEND_API_KEY", "")
EMAIL_REMETENTE = os.getenv("EMAIL_REMETENTE", "onboarding@resend.dev")
EMAIL_DESTINO = os.getenv("EMAIL_DESTINO", "")

# Configurações do Pushover
PUSHOVER_API_TOKEN = os.getenv("PUSHOVER_API_TOKEN", "")
PUSHOVER_USER_KEY = os.getenv("PUSHOVER_USER_KEY", "")

def formatar_data_yyyy_mm_dd(data_str: str) -> str:
    """Converte datas nos formatos DD/MM/YYYY para YYYY-MM-DD se necessário."""
    data_str = data_str.strip()
    if "/" in data_str:
        partes = data_str.split("/")
        if len(partes) == 3:
            # Assume DD/MM/YYYY -> YYYY-MM-DD
            dia, mes, ano = partes[0].zfill(2), partes[1].zfill(2), partes[2]
            return f"{ano}-{mes}-{dia}"
    return data_str

def obter_url_com_data(url_base: str, data_alvo: str) -> str:
    """Retorna a URL base formatada incluindo o parâmetro ?date=YYYY-MM-DD."""
    data_fmt = formatar_data_yyyy_mm_dd(data_alvo)
    url_limpa = url_base.split("?")[0]
    return f"{url_limpa}?date={data_fmt}"

