import time
import os
import re
from playwright.sync_api import sync_playwright
from src.config import (
    URL_ALVO,
    DATA_ALVO,
    CINEMA_ALVO,
    INTERVALO_MINUTOS,
    SESSION_DIR,
    obter_url_com_data,
    formatar_data_yyyy_mm_dd
)
from src.notifier import enviar_notificacao, enviar_notificacao_pushover

def tentar_fechar_cookies(page):
    """Tenta clicar no botão de aceitar cookies se estiver presente na tela."""
    try:
        btn_cookie = page.locator("button:has-text('Concordar e fechar'), button:has-text('Aceitar')")
        if btn_cookie.count() > 0 and btn_cookie.first.is_visible():
            btn_cookie.first.click(force=True)
            page.wait_for_timeout(1000)
            print("🍪 [DEBUG] Modal de cookies fechado com sucesso.")
    except Exception:
        pass

def garantir_selecao_cinema(page):
    """Verifica se há solicitação para selecionar localidade e seleciona o CINEMA_ALVO."""
    try:
        # Checa se o cinema já está selecionado
        body_text = page.inner_text("body")
        if CINEMA_ALVO.lower() in body_text.lower():
            print(f"📍 [DEBUG] Cinema '{CINEMA_ALVO}' já está ativo na página.")
            return

        sel_local = page.locator("text=POR FAVOR, SELECIONE UMA LOCALIDADE").first
        if sel_local.count() > 0 and sel_local.is_visible():
            print(f"📍 [DEBUG] Selecionando cinema alvo '{CINEMA_ALVO}'...")
            sel_local.click(force=True)
            page.wait_for_timeout(1500)
            
            # Clica na opção do cinema (ex: Cinépolis JK Iguatemi (SP))
            op_cinema = page.locator(f"text={CINEMA_ALVO}").first
            if op_cinema.count() > 0 and op_cinema.is_visible():
                op_cinema.click(force=True)
                page.wait_for_timeout(3000)
                print(f"✅ [DEBUG] Cinema '{CINEMA_ALVO}' selecionado com sucesso!")
            else:
                op_alt = page.locator("text=JK Iguatemi").first
                if op_alt.count() > 0 and op_alt.is_visible():
                    op_alt.click(force=True)
                    page.wait_for_timeout(3000)
                    print("✅ [DEBUG] Cinema 'JK Iguatemi' selecionado!")
    except Exception as e:
        print(f"⚠️ [DEBUG] Erro ao tentar selecionar o cinema: {e}")

def garantir_selecao_data(page, data_str):
    """Tenta localizar e clicar no dia correspondente no carrossel de datas para expandir as sessões."""
    try:
        # Extrai o dia (ex: "12" de "2026-08-12" ou "12/08/2026")
        match = re.search(r'\b(\d{1,2})\b', data_str)
        dia_alvo = str(int(match.group(1))) if match else ""
        
        if not dia_alvo:
            return

        # Procura botões/elementos do carrossel que contenham o dia alvo
        dias_el = page.locator(f"text={dia_alvo}")
        for i in range(dias_el.count()):
            el = dias_el.nth(i)
            if el.is_visible():
                txt = el.inner_text().strip()
                if txt == dia_alvo:
                    print(f"📅 [DEBUG] Clicando no dia {dia_alvo} no carrossel de datas...")
                    el.click(force=True)
                    page.wait_for_timeout(2000)
                    break
    except Exception as e:
        print(f"⚠️ [DEBUG] Erro ao selecionar o dia no carrossel: {e}")

def verificar_e_monitorar(headless=True):
    """Roda a verificação periódica acessando a URL com o parâmetro date=?YYYY-MM-DD,
    garantindo a seleção do cinema e executando reload no navegador a cada ciclo.
    """
    data_formatada = formatar_data_yyyy_mm_dd(DATA_ALVO)
    url_com_data = obter_url_com_data(URL_ALVO, DATA_ALVO)
    
    print(f"🚀 Iniciando monitoramento periódico a cada {INTERVALO_MINUTOS} minutos...")
    print(f"URL Alvo com parâmetro: {url_com_data}")
    print(f"Cinema Alvo: {CINEMA_ALVO}")
    print(f"Data Alvo procurada: {data_formatada}")
    print(f"Modo de Execução: {'Visível' if not headless else 'Oculto (Headless)'}")
    
    alerta_enviado = False
    site_indisponivel = False
    
    os.makedirs(SESSION_DIR, exist_ok=True)
    
    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            user_data_dir=SESSION_DIR,
            headless=headless,
            viewport={'width': 1280, 'height': 800},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            ignore_default_args=["--enable-automation"],
            args=[
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-blink-features=AutomationControlled"
            ]
        )
        
        page = None
        
        try:
            while True:
                timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
                print(f"\n[{timestamp}] Checando sessões para {CINEMA_ALVO} na data {data_formatada}...")
                
                try:
                    if page is None or page.is_closed():
                        print(f"🌐 Navegando para: {url_com_data}")
                        page = context.new_page()
                        response = page.goto(url_com_data, timeout=60000, wait_until="domcontentloaded")
                    else:
                        print("🔄 Recarregando a página no navegador (Reload)...")
                        response = page.reload(timeout=60000, wait_until="domcontentloaded")
                        
                    if response is None or not response.ok:
                        status = response.status if response else "Sem Resposta/Timeout"
                        raise Exception(f"O site retornou código de erro HTTP {status}")
                        
                    page.wait_for_timeout(3000)
                    tentar_fechar_cookies(page)
                    garantir_selecao_cinema(page)
                    garantir_selecao_data(page, data_formatada)
                    
                    if site_indisponivel:
                        print("🎉 O site voltou a ficar disponível!")
                        enviar_notificacao_pushover(
                            titulo="✅ SITE DISPONÍVEL NOVAMENTE",
                            mensagem="A página de monitoramento de ingressos voltou a responder normalmente.",
                            priority=0,
                            sound="magic"
                        )
                        site_indisponivel = False
                    
                    # Salva screenshot para debug visual no container/máquina
                    screenshot_path = os.path.join(SESSION_DIR, "debug_last.png")
                    try:
                        page.screenshot(path=screenshot_path)
                        print(f"📸 [DEBUG] Screenshot salvo em: {screenshot_path}")
                    except Exception:
                        pass

                    # Análise do conteúdo da página
                    body_text = page.inner_text("body")
                    lines = [line.strip() for line in body_text.split('\n') if line.strip()]
                    
                    print("\n--- [DEBUG LOG] AMATRA DE CONTEÚDO CAPTURADO DA PÁGINA ---")
                    for l in lines:
                        if any(k in l.lower() for k in ['cinema', 'legendado', 'dublado', 'sess', 'quarta', '12', '14:', '18:', '22:', 'horário']):
                            print("  [PAGE LOG] >", l[:120])
                    print("--- [DEBUG LOG] FIM DA AMOSTRA ---\n")
                    
                    # Busca por horários de exibição (ex: 14:30, 18:15, 22:00)
                    horarios_encontrados = re.findall(r'\b(?:[01]?\d|2[0-3]):[0-5]\d\b', body_text)
                    horarios_validos = sorted(list(set([h for h in horarios_encontrados if h != "00:00"])))
                    
                    print(f"🔎 [DEBUG] Horários potenciais detectados: {horarios_validos}")
                    
                    tem_aviso_sem_sessao = ("não há sessões" in body_text.lower() or 
                                           "nao ha sessoes" in body_text.lower() or 
                                           "nenhuma sessão" in body_text.lower() or
                                           "selecione um cinema para ver as sessões" in body_text.lower())
                    
                    tem_sessao_disponivel = len(horarios_validos) > 0 and not tem_aviso_sem_sessao
                    
                    if tem_sessao_disponivel:
                        print(f"🎯 SUCESSO: Foram encontradas sessões disponíveis no {CINEMA_ALVO} para {data_formatada}!")
                        print(f"🕒 Horários disponíveis encontrados: {', '.join(horarios_validos)}")
                            
                        if not alerta_enviado:
                            resend_ok = enviar_notificacao(data_formatada, horarios_validos)
                            pushover_ok = enviar_notificacao_pushover(
                                titulo=f"🚨 SESSÃO DISPONÍVEL NO {CINEMA_ALVO}!",
                                mensagem=f"Sessões encontradas ({', '.join(horarios_validos)}) para {data_formatada}! Acesse: {url_com_data}",
                                priority=2
                            )
                            alerta_enviado = resend_ok or pushover_ok
                    else:
                        print(f"ℹ️ Data ({data_formatada}) no {CINEMA_ALVO} verificada, porém ainda NÃO há sessões disponíveis no momento.")
                            
                except Exception as e:
                    erro_msg = str(e)
                    print(f"❌ Erro durante a verificação da página: {erro_msg}")
                    
                    if not site_indisponivel:
                        enviar_notificacao_pushover(
                            titulo="⚠️ SITE INDISPONÍVEL",
                            mensagem=f"Ocorreu um erro de conexão com o site: {erro_msg}",
                            priority=0,
                            sound="falling"
                        )
                        site_indisponivel = True
                
                print(f"Aguardando {INTERVALO_MINUTOS} minutos para o próximo reload...")
                time.sleep(INTERVALO_MINUTOS * 60)
                
        except KeyboardInterrupt:
            print("\n👋 Monitoramento interrompido pelo usuário.")
        finally:
            if page and not page.is_closed():
                page.close()
            context.close()
