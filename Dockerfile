FROM mcr.microsoft.com/playwright/python:v1.48.0-jammy

# Define o diretório de trabalho dentro do container
WORKDIR /app

# Copia os arquivos de dependência
COPY requirements.txt .

# Instala as dependências Python
RUN pip install --no-cache-dir -r requirements.txt

# Garante que a versão correta do Chromium seja baixada para o container
RUN python -m playwright install chromium

# Copia o código do bot para dentro do container
COPY bot.py .

# Cria a pasta de sessão caso não exista
RUN mkdir -p /app/session

# Define as variáveis de ambiente necessárias
ENV PYTHONUNBUFFERED=1

# Executa o script por padrão (ele rodará em modo headless de monitoramento)
CMD ["python", "bot.py"]