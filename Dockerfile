FROM mcr.microsoft.com/playwright/python:v1.61.0-jammy

# Define o diretório de trabalho dentro do container
WORKDIR /app

ENV DEBIAN_FRONTEND=noninteractive

# Instala o tzdata para suportar a variável de ambiente TZ corretamente
RUN apt-get update && apt-get install -y tzdata && rm -rf /var/lib/apt/lists/*

# Copia os arquivos de dependência
COPY requirements.txt .

# Instala as dependências Python (a imagem base alinhada com a versão do Playwright)
RUN pip install --no-cache-dir -r requirements.txt

# Copia o código do bot e os módulos para dentro do container
COPY bot.py .
COPY src/ ./src/

# Cria a pasta de sessão caso não exista
RUN mkdir -p /app/session

# Define as variáveis de ambiente necessárias
ENV PYTHONUNBUFFERED=1

# Executa o script por padrão (ele rodará em modo headless de monitoramento)
CMD ["python", "bot.py"]