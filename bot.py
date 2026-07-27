import os
import argparse
import sys

# Garante que o diretório atual esteja no path do Python
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from src.scanner import realizar_scan_e_login
from src.monitor import verificar_e_monitorar
from src.config import SESSION_DIR

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
