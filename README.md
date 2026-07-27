# Bot de Monitoramento de Ingressos

Este projeto é um bot automatizado que monitora sites de venda de ingressos em busca de disponibilidade de uma data específica. Ele utiliza Playwright para navegar no site e extrair informações, notificando você via Resend (e-mail) ou Pushover (notificação celular) quando o ingresso estiver disponível.

## 📋 Pré-requisitos

* Python 3.9+ ou Docker instalado.

## ⚙️ Configuração

1. Clone o repositório e acesse a pasta do projeto.
2. Crie um arquivo `.env` na raiz do projeto copiando o arquivo de exemplo fornecido:
   ```bash
   cp .env.example .env
   ```
3. Edite o arquivo `.env` e configure suas variáveis de ambiente, como por exemplo:
   - `URL_ALVO`: Link direto da página de ingressos.
   - `DATA_ALVO`: A data que você quer monitorar (ex: 20/07/2026).
   - `INTERVALO_MINUTOS`: O tempo de espera entre cada checagem.
   - Notificações: Configure as chaves de API do Resend e/ou Pushover.

---

## 💻 Como Rodar Localmente (Python)

### 1. Instalar as Dependências

Primeiro, crie um ambiente virtual (recomendado) e instale as bibliotecas necessárias:

```bash
python -m venv venv

# Ativando o ambiente virtual:
# No Windows:
venv\Scripts\activate
# No Linux/Mac:
source venv/bin/activate

# Instalando as bibliotecas
pip install -r requirements.txt

# Instalando o navegador do Playwright
playwright install chromium
```

### 2. Escaneamento Inicial e Login (Importante na 1ª vez)

A primeira execução deve ser feita no modo `--scan` para gerar a sessão (se o site exigir login) e escanear a página:

```bash
python bot.py --scan
```

Siga as instruções exibidas no terminal. O navegador abrirá a página alvo para que você faça o login e a navegação inicial. Após chegar à página correta, pressione `Enter` no terminal. O bot salvará a sessão (cookies) localmente na pasta `session`.

### 3. Executar o Monitoramento

Após realizar o escaneamento inicial, você já pode iniciar o bot para ficar monitorando periodicamente em segundo plano (Headless):

```bash
python bot.py
```

*Nota: Se preferir ver a tela do navegador executando a cada checagem, utilize a flag `--visible`:*
```bash
python bot.py --visible
```

---

## 🐳 Como Rodar Utilizando o Docker

### 1. Construir a Imagem do Docker

Após ajustar seu `.env` e ter feito o seu primeiro login e escaneamento gerando a pasta `session` na sua máquina local (passo 2 acima), construa a imagem do Docker com o comando:

```bash
docker build -t bot-ingressos .
```

### 2. Executar o Container

Para rodar o bot isoladamente dentro do Docker, utilize o comando abaixo. Ele passará o seu arquivo `.env` e fará um link da sua pasta `session` local para dentro do container, mantendo o seu acesso ao site:

```bash
docker run -d --name bot-ingressos -v "%cd%\session:/app/session" --env-file .env bot-ingressos
```
*(Nota: No Windows, utilizamos `%cd%` ou `${PWD}` no PowerShell. No Linux/Mac utilize `$(pwd)` no lugar).*

### Comandos Úteis do Docker:

* **Visualizar os logs de execução do bot em tempo real:**
  ```bash
  docker logs -f bot-ingressos
  ```
* **Parar o monitoramento:**
  ```bash
  docker stop bot-ingressos
  ```
* **Reiniciar o monitoramento:**
  ```bash
  docker start bot-ingressos
  ```
