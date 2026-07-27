import os
import re
import sys
import time
import argparse
import urllib.request
import urllib.parse
from playwright.sync_api import sync_playwright
import resend
from dotenv import load_dotenv

# Carrega as variáveis do arquivo .env
load_dotenv()

# Configurações do arquivo .env ou valores padrão
URL_ALVO = os.getenv("URL_ALVO", "https://www.cinepolis.com.br/filmes/1000046469-a-odisseia-imax/")
SELETOR_DATA = os.getenv("SELETOR_DATA", ".data-disponivel")
DATA_ALVO = os.getenv("DATA_ALVO", "20/07/2026")
INTERVALO_MINUTOS = int(os.getenv("INTERVALO_MINUTOS", "5"))
SESSION_DIR = os.getenv("SESSION_DIR", "./session")
RESEND_API_KEY = os.getenv("RESEND_API_KEY", "")
EMAIL_REMETENTE = os.getenv("EMAIL_REMETENTE", "onboarding@resend.dev")
EMAIL_DESTINO = os.getenv("EMAIL_DESTINO", "")

# Configurações do Pushover
PUSHOVER_API_TOKEN = os.getenv("PUSHOVER_API_TOKEN", "")
PUSHOVER_USER_KEY = os.getenv("PUSHOVER_USER_KEY", "")

# Configura o Resend API Key
if RESEND_API_KEY:
    resend.api_key = RESEND_API_KEY

def enviar_notificacao(data_desejada, datas_disponiveis):
    """Envia um e-mail de alerta utilizando o Resend."""
    if not RESEND_API_KEY or not EMAIL_DESTINO:
        print("⚠️ Configurações do Resend ou E-mail de destino ausentes. Não foi possível enviar notificação por e-mail.")
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

def enviar_notificacao_pushover(titulo, mensagem, priority=0, sound="pushover"):
    """Envia uma notificação para o celular via Pushover."""
    if not PUSHOVER_API_TOKEN or not PUSHOVER_USER_KEY:
        print("⚠️ Configurações do Pushover ausentes no arquivo .env. Não foi possível enviar a notificação.")
        return False
        
    try:
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
        # - retry=30: o celular vai apitar a cada 30 segundos
        # - expire=3600: o alarme para de apitar depois de 1 hora se não for lido pelo usuário
        if priority == 2:
            payload["retry"] = 30
            payload["expire"] = 3600
            payload["sound"] = "persistent" # Toca som de alarme persistente
            
        data = urllib.parse.urlencode(payload).encode("utf-8")
        
        req = urllib.request.Request(url, data=data)
        with urllib.request.urlopen(req) as response:
            res_body = response.read().decode("utf-8")
            print(f"🔊 Notificação do Pushover enviada! Resposta: {res_body}")
            return True
            
    except Exception as e:
        print(f"❌ Erro ao enviar notificação via Pushover: {e}")
        return False

def realizar_scan_e_login():
    """Abre o navegador de forma visível, permite que o usuário faça o login,

    navegue até a tela final de ingressos, e escaneia a estrutura do DOM ao receber confirmação.
    """
    print("🔑 Iniciando modo de Login e Escaneamento da Estrutura da Página...")
    print(f"1. O navegador se abrirá em modo visível apontando para: {URL_ALVO}")
    print("2. Faça o login e navegue até a tela exata dos ingressos que deseja monitorar.")
    print("3. Quando chegar na página final, volte a este terminal e pressione [Enter] para escanear a página.")
    print("--------------------------------------------------------------------------------------------------")
    
    os.makedirs(SESSION_DIR, exist_ok=True)
    
    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            user_data_dir=SESSION_DIR,
            headless=False,
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            ignore_default_args=["--enable-automation"],
            args=[
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-blink-features=AutomationControlled"
            ]
        )
        
        page = context.new_page()
        page.goto(URL_ALVO)
        
        # Aguarda a confirmação do usuário que já está na tela certa
        input("\nPressione [Enter] AQUI no terminal quando estiver na página final para escanear a estrutura...")
        
        print("\n⏳ Escaneando a página... Por favor, aguarde.")
        
        try:
            # 1. Salva o HTML completo da página
            html_completo = page.content()
            with open("pagina_completa.html", "w", encoding="utf-8") as f:
                f.write(html_completo)
            print("💾 HTML completo salvo em 'pagina_completa.html'")
            
            # 2. Extrai estrutura simplificada com elementos interativos e textos
            estrutura_simplificada = []
            estrutura_simplificada.append("=== ESTRUTURA SIMPLIFICADA DA PÁGINA ESQUELETO ===\n")
            estrutura_simplificada.append(f"URL Escaneada: {page.url}\n")
            estrutura_simplificada.append(f"Título da Página: {page.title()}\n")
            estrutura_simplificada.append("="*50 + "\n")
            
            # Mapeia botões, links, inputs e textos relevantes
            elementos = page.locator("button, a, input, select, [class*='date'], [class*='calendar'], [id*='date'], [id*='calendar']")
            count = elementos.count()
            
            estrutura_simplificada.append(f"Elementos de interesse detectados ({count}):\n")
            for i in range(count):
                el = elementos.nth(i)
                tag_name = el.evaluate("el => el.tagName.toLowerCase()")
                classes = el.evaluate("el => el.className")
                el_id = el.evaluate("el => el.id")
                text = el.inner_text().strip().replace('\n', ' ')
                
                info = f"- [{tag_name.upper()}] "
                if el_id:
                    info += f"ID: #{el_id} | "
                if classes:
                    info += f"Classes: .{classes.replace(' ', '.')} | "
                if text:
                    # Limita exibição do texto
                    info += f"Texto: '{text[:60]}'"
                else:
                    placeholder = el.evaluate("el => el.placeholder")
                    if placeholder:
                        info += f"Placeholder: '{placeholder}'"
                
                estrutura_simplificada.append(info + "\n")
            
            # Escreve a estrutura em arquivo
            with open("estrutura_pagina.txt", "w", encoding="utf-8") as f:
                f.writelines(estrutura_simplificada)
            print("💾 Estrutura da página simplificada salva em 'estrutura_pagina.txt'")
            
        except Exception as e:
            print(f"❌ Erro ao escanear a página: {e}")
            
        finally:
            # Fecha o browser salvando a sessão/cookies no persistent context
            context.close()
            print("\n✅ Escaneamento e Login concluídos!")
            print("O cache de sessão foi salvo em './session'.")
            print("Aguardando novas instruções de como proceder com a automação final.")
            print("--------------------------------------------------------------------------------------------------")

def verificar_e_monitorar(headless=True):
    """Roda a verificação periódica de datas no modo Headless/Visible."""
    # Como o usuário quer instruções adicionais primeiro, mantemos a função estruturada,
    # mas o fluxo principal de escaneamento orientará a parar e aguardar novas diretrizes.
    print(f"🚀 Iniciando monitoramento periódico a cada {INTERVALO_MINUTOS} minutos...")
    print(f"URL Alvo: {URL_ALVO}")
    print(f"Data Alvo procurada: {DATA_ALVO}")
    print(f"Modo de Execução: {'Visível' if not headless else 'Oculto (Headless)'}")
    
    alerta_enviado = False
    site_indisponivel = False
    
    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            user_data_dir=SESSION_DIR,
            headless=headless,
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            ignore_default_args=["--enable-automation"],
            args=[
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-blink-features=AutomationControlled"
            ]
        )
        
        try:
            while True:
                print(f"\n[{time.strftime('%Y-%m-%d %H:%M:%S')}] Checando página de ingressos...")
                page = context.new_page()
                
                try:
                    response = page.goto(URL_ALVO, timeout=60000)
                    if response is None or not response.ok:
                        status = response.status if response else "Sem Resposta/Timeout"
                        raise Exception(f"O site retornou código de erro HTTP {status}")
                        
                    page.wait_for_load_state("domcontentloaded")
                    page.wait_for_timeout(3000)
                    
                    # Se o site estava indisponível e agora carregou com sucesso
                    if site_indisponivel:
                        print("🎉 O site voltou a ficar disponível!")
                        enviar_notificacao_pushover(
                            titulo="✅ SITE DISPONÍVEL NOVAMENTE",
                            mensagem="A página de monitoramento de ingressos voltou a responder normalmente.",
                            priority=0,
                            sound="magic"
                        )
                        site_indisponivel = False
                    
                    # Configurações dos seletores do calendário
                    SETA_NEXT = ".css-1d7lels"
                    
                    datas_encontradas = set()
                    historico_paginas = []
                    
                    while True:
                        # 1. Coleta as datas que estão visíveis na tela no momento
                        datas_visiveis = []
                        elementos_datas = page.locator(SELETOR_DATA)
                        total_elementos = elementos_datas.count()
                        
                        for i in range(total_elementos):
                            el = elementos_datas.nth(i)
                            if el.is_visible():
                                texto = el.inner_text().strip().replace('\n', ' ')
                                if texto:
                                    datas_visiveis.append(texto)
                                    
                        # Se não encontrar nenhuma data visível, aborta
                        if not datas_visiveis:
                            print("Nenhuma data visível encontrada neste slide.")
                            break
                            
                        print(f"Slide atual - datas visíveis: {datas_visiveis}")
                        
                        # Adiciona ao conjunto acumulado
                        datas_encontradas.update(datas_visiveis)
                        
                        # Estado atual da tela para detecção de fim/looping circular
                        estado_atual = tuple(datas_visiveis)
                        if estado_atual in historico_paginas:
                            print("🔄 O calendário retornou ao início ou travou. Finalizando varredura das setas.")
                            break
                        historico_paginas.append(estado_atual)
                        
                        # 2. Localiza a seta para a direita
                        seta = page.locator(SETA_NEXT)
                        if seta.count() == 0 or not seta.is_visible():
                            print("Seta para a direita não encontrada ou invisível. Fim do calendário.")
                            break
                            
                        # Verifica se a seta está inativa
                        aria_disabled = seta.get_attribute("aria-disabled")
                        if aria_disabled == "true":
                            print("Seta para a direita está desativada (aria-disabled='true'). Fim do calendário.")
                            break
                            
                        # 3. Clica na seta e aguarda a transição
                        try:
                            seta.click(force=True)
                            page.wait_for_timeout(1000) # Aguarda 1 segundo pela transição do slide
                        except Exception as click_err:
                            print(f"Não foi possível clicar na seta: {click_err}")
                            break
                    
                    datas_encontradas_lista = sorted(list(datas_encontradas))
                    print(f"📅 Total de dias mapeados no calendário completo: {datas_encontradas_lista}")
                    
                    # Validação da data alvo no acumulado de todas as abas
                    # Se for fornecida uma data no formato DD/MM/AAAA, extraímos apenas o dia para bater com o site
                    dia_alvo_str = DATA_ALVO.split("/")[0].strip() if "/" in DATA_ALVO else DATA_ALVO.strip()
                    dia_alvo = str(int(dia_alvo_str))  # Remove zeros à esquerda e converte para número limpo
                    
                    data_disponivel = False
                    for data_detectada in datas_encontradas:
                        # Extrai o primeiro grupo de números encontrado no texto (ex: "SEG. 20" -> "20", "TER. 4/08" -> "4")
                        match = re.search(r'\d+', data_detectada)
                        numeros_data = match.group() if match else ""
                        if dia_alvo == numeros_data:
                            data_disponivel = True
                            break
                    
                    if data_disponivel:
                        print(f"🎯 SUCESSO: A data desejada ({DATA_ALVO}) está disponível!")
                        if not alerta_enviado:
                            resend_ok = enviar_notificacao(DATA_ALVO, datas_encontradas_lista)
                            pushover_ok = enviar_notificacao_pushover(
                                titulo="🚨 INGRESSOS DISPONÍVEIS!",
                                mensagem=f"A data desejada {DATA_ALVO} está aberta para compras no site!",
                                priority=2
                            )
                            alerta_enviado = resend_ok or pushover_ok
                    else:
                        print(f"ℹ️ A data desejada ({DATA_ALVO}) ainda não está disponível.")
                        
                except Exception as e:
                    erro_msg = str(e)
                    print(f"❌ Erro durante a varredura da página: {erro_msg}")
                    
                    # Notifica apenas uma vez quando o site cai
                    if not site_indisponivel:
                        enviar_notificacao_pushover(
                            titulo="⚠️ SITE INDISPONÍVEL",
                            mensagem=f"Ocorreu um erro de conexão com o site: {erro_msg}",
                            priority=0,
                            sound="falling"
                        )
                        site_indisponivel = True
                finally:
                    page.close()
                
                print(f"Aguardando {INTERVALO_MINUTOS} minutos para a próxima verificação...")
                time.sleep(INTERVALO_MINUTOS * 60)
                
        except KeyboardInterrupt:
            print("\n👋 Monitoramento interrompido pelo usuário.")
        finally:
            context.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Bot de Monitoramento de Ingressos")
    parser.add_argument("--scan", action="store_true", help="Executa o modo de login, navegação e escaneamento inicial do DOM")
    parser.add_argument("--visible", action="store_true", help="Abre o navegador de forma visível ao rodar o monitoramento")
    args = parser.parse_args()
    
    if args.scan:
        realizar_scan_e_login()
    else:
        # Se a pasta de sessão não existir ou estiver vazia, avisa o usuário sobre o login
        if not os.path.exists(SESSION_DIR) or not os.listdir(SESSION_DIR):
            print("⚠️ Atenção: A pasta de cache de sessão parece vazia ou não existe.")
            print("Para garantir que a sessão e os cookies estejam corretos, execute primeiro:")
            print("python bot.py --scan")
            print("----------------------------------------------------------------------")
        
        # Por padrão headless=True. Se --visible for passado, headless torna-se False
        verificar_e_monitorar(headless=not args.visible)
