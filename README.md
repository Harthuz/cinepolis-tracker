# Bot de Monitoramento de Ingressos (Cinépolis Tracker)

Este projeto é um bot automatizado que monitora sites de venda de ingressos (como a Cinépolis) em busca da disponibilidade de sessões para uma data e cinema específicos. Ele utiliza o **Playwright** para navegar de forma reativa no site, aceitar cookies, selecionar a localidade do cinema e verificar os horários das sessões, notificando você via **Resend** (e-mail) ou **Pushover** (notificação de emergência no celular) assim que os ingressos forem liberados.

---

## 🚀 Funcionalidades e Processo de Verificação por URL e Data

- **Parametrização por Data Alvo na URL**: O bot monta automaticamente a URL da página do filme contendo o parâmetro `?date=YYYY-MM-DD` (ex: `https://www.cinepolis.com.br/filmes/1000046469-a-odisseia-imax/?date=2026-08-12`).
- **Seleção Automática do Cinema Alvo**: Ao carregar a página, o bot detecta se a localidade precisa ser definida e seleciona automaticamente o complexo configurado (ex: `Cinépolis JK Iguatemi (SP)`).
- **Reload Periódico do Navegador**: A cada ciclo de monitoramento (`INTERVALO_MINUTOS`), o bot executa um `page.reload()` no navegador mantendo os cookies e a sessão para verificar a abertura dos horários (ex: `14:30`, `18:15`, `22:00`).
- **Tratamento Automático de Cookies/LGPD**: Fecha automaticamente o modal de consentimento de privacidade.
- **Alertas Imediatos**: Envia notificações instantâneas com a lista dos horários encontrados assim que a sessão fica disponível.

---

## ⚙️ Configuração

1. Clone o repositório e acesse a pasta do projeto.
2. Crie o arquivo `.env` baseado no exemplo `.env.example`:
   ```bash
   cp .env.example .env
   ```
3. Configure suas variáveis no `.env`:
   - `URL_ALVO`: Link direto do filme (ex: `https://www.cinepolis.com.br/filmes/1000046469-a-odisseia-imax/`).
   - `DATA_ALVO`: Data alvo a ser monitorada no formato `YYYY-MM-DD` ou `DD/MM/YYYY` (ex: `2026-08-12`).
   - `CINEMA_ALVO`: Nome da localidade/cinema alvo (padrão: `Cinépolis JK Iguatemi (SP)`).
   - `INTERVALO_MINUTOS`: Tempo de espera entre cada reload (padrão: `5` minutos).
   - `RESEND_API_KEY`, `EMAIL_DESTINO`: Para notificações por e-mail via Resend.
   - `PUSHOVER_API_TOKEN`, `PUSHOVER_USER_KEY`: Para alertas persistentes no celular via Pushover.

---

## 🧪 Processo de Teste de URLs e Validação

Você pode validar a verificação das URLs e sessões para datas específicas diretamente com os comandos abaixo:

### Testar a verificação de data e seleção de cinema:
O bot acessará a URL formatada com `?date=YYYY-MM-DD`, fechará o banner de cookies e garantirá a seleção do **Cinépolis JK Iguatemi (SP)**.

```bash
# Executa o monitoramento uma vez ou periodicamente
python bot.py --visible
```

Se a data monitorada (ex: `2026-08-12`) tiver sessões abertas, o terminal exibirá:
```text
🎯 SUCESSO: Foram encontradas sessões disponíveis no Cinépolis JK Iguatemi (SP) para 2026-08-12!
🕒 Horários disponíveis encontrados: 14:30, 18:15, 22:00
```

---

## 💻 Como Rodar Localmente (Python)

### 1. Instalar as Dependências

```bash
# Criando ambiente virtual (opcional)
python -m venv venv
venv\Scripts\activate

# Instalando as dependências
pip install -r requirements.txt

# Instalando os navegadores do Playwright
playwright install chromium
```

### 2. Escaneamento Inicial e Login (Modo --scan)

A primeira execução pode ser feita com `--scan` para visualizar o navegador e gerar os cookies de sessão:

```bash
python bot.py --scan
```

### 3. Executar o Monitoramento

Para rodar em segundo plano (Headless):
```bash
python bot.py
```

Para visualizar a janela do navegador em cada reload:
```bash
python bot.py --visible
```

---

## 🐳 Como Rodar Utilizando o Docker

### 1. Construir a Imagem do Docker

```bash
docker build -t harthuz/cinepolis-tracker .
```

### 2. Executar o Container

```bash
docker run -d --name cinepolis-tracker -v "%cd%\session:/app/session" --env-file .env harthuz/cinepolis-tracker
```
*(No Linux/Mac utilize `$(pwd)` no lugar de `%cd%`).*

### Comandos Úteis do Docker:

* **Visualizar logs em tempo real:**
  ```bash
  docker logs -f cinepolis-tracker
  ```
* **Parar o container:**
  ```bash
  docker stop cinepolis-tracker
  ```
* **Reiniciar o container:**
  ```bash
  docker start cinepolis-tracker
  ```
