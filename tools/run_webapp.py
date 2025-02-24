import os
import sys
import subprocess
import webbrowser
from time import sleep

def check_venv():
    """Verifica se está rodando em um venv"""
    if not hasattr(sys, 'real_prefix') and not hasattr(sys, 'base_prefix'):
        print("""
Erro: Ambiente virtual não ativado!

Ative o ambiente primeiro:
- Windows: .\\venv\\Scripts\\activate
- Linux/Mac: source venv/bin/activate
        """)
        sys.exit(1)

def check_dependencies():
    """Verifica e instala dependências necessárias"""
    try:
        import streamlit
        import requests
        import pandas
        import plotly
    except ImportError:
        print("Instalando dependências...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "web_app/requirements.txt"])

def start_webapp():
    """Inicia a aplicação Streamlit"""
    try:
        # Verifica ambiente
        check_venv()
        
        # Verifica se o Streamlit está rodando
        try:
            requests.get("http://localhost:8501")
            print("Aplicação já está rodando!")
            return
        except:
            pass
            
        # Inicia a aplicação
        print("Iniciando aplicação web...")
        os.chdir("web_app")
        
        # Configura variáveis de ambiente
        os.environ["STREAMLIT_SERVER_PORT"] = "8501"
        os.environ["STREAMLIT_SERVER_ADDRESS"] = "0.0.0.0"
        
        # Inicia o Streamlit
        process = subprocess.Popen(
            [sys.executable, "-m", "streamlit", "run", "app.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # Aguarda inicialização
        print("Aguardando inicialização...")
        sleep(5)
        
        # Abre navegador
        webbrowser.open("http://localhost:8501")
        
        print("""
Aplicação iniciada!
- Local: http://localhost:8501
- Rede: http://<seu-ip>:8501
        """)
        
        # Mantém processo rodando
        process.wait()
        
    except Exception as e:
        print(f"Erro ao iniciar aplicação: {str(e)}")
        sys.exit(1)

def main():
    # Verifica dependências
    check_dependencies()
    
    # Inicia aplicação
    start_webapp()

if __name__ == "__main__":
    main() 