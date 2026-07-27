import os
from playwright.sync_api import sync_playwright
from src.config import URL_ALVO, SESSION_DIR

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
            context.close()
            print("\n✅ Escaneamento e Login concluídos!")
            print("O cache de sessão foi salvo em './session'.")
            print("Aguardando novas instruções de como proceder com a automação final.")
            print("--------------------------------------------------------------------------------------------------")
