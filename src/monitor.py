import time
import re
from playwright.sync_api import sync_playwright
from src.config import (
    URL_ALVO,
    SELETOR_DATA,
    DATA_ALVO,
    INTERVALO_MINUTOS,
    SESSION_DIR
)
from src.notifier import enviar_notificacao, enviar_notificacao_pushover

def verificar_e_monitorar(headless=True):
    """Roda a verificação periódica de datas no modo Headless/Visible."""
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
                    
                    if site_indisponivel:
                        print("🎉 O site voltou a ficar disponível!")
                        enviar_notificacao_pushover(
                            titulo="✅ SITE DISPONÍVEL NOVAMENTE",
                            mensagem="A página de monitoramento de ingressos voltou a responder normalmente.",
                            priority=0,
                            sound="magic"
                        )
                        site_indisponivel = False
                    
                    SETA_NEXT = ".css-1d7lels"
                    
                    datas_encontradas = set()
                    historico_paginas = []
                    
                    while True:
                        datas_visiveis = []
                        elementos_datas = page.locator(SELETOR_DATA)
                        total_elementos = elementos_datas.count()
                        
                        for i in range(total_elementos):
                            el = elementos_datas.nth(i)
                            if el.is_visible():
                                texto = el.inner_text().strip().replace('\n', ' ')
                                if texto:
                                    datas_visiveis.append(texto)
                                    
                        if not datas_visiveis:
                            print("Nenhuma data visível encontrada neste slide.")
                            break
                            
                        print(f"Slide atual - datas visíveis: {datas_visiveis}")
                        
                        datas_encontradas.update(datas_visiveis)
                        
                        estado_atual = tuple(datas_visiveis)
                        if estado_atual in historico_paginas:
                            print("🔄 O calendário retornou ao início ou travou. Finalizando varredura das setas.")
                            break
                        historico_paginas.append(estado_atual)
                        
                        seta = page.locator(SETA_NEXT)
                        if seta.count() == 0 or not seta.is_visible():
                            print("Seta para a direita não encontrada ou invisível. Fim do calendário.")
                            break
                            
                        aria_disabled = seta.get_attribute("aria-disabled")
                        if aria_disabled == "true":
                            print("Seta para a direita está desativada (aria-disabled='true'). Fim do calendário.")
                            break
                            
                        try:
                            seta.click(force=True)
                            page.wait_for_timeout(1000)
                        except Exception as click_err:
                            print(f"Não foi possível clicar na seta: {click_err}")
                            break
                    
                    datas_encontradas_lista = sorted(list(datas_encontradas))
                    print(f"📅 Total de dias mapeados no calendário completo: {datas_encontradas_lista}")
                    
                    dia_alvo_str = DATA_ALVO.split("/")[0].strip() if "/" in DATA_ALVO else DATA_ALVO.strip()
                    dia_alvo = str(int(dia_alvo_str))
                    
                    data_disponivel = False
                    for data_detectada in datas_encontradas:
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
