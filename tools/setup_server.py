import os
import sys
import subprocess
import platform

def setup_venv():
    """Configura ambiente virtual e instala dependências"""
    try:
        # Detecta o sistema operacional
        is_windows = platform.system().lower() == "windows"
        python_cmd = "python" if is_windows else "python3"
        
        print("Configurando ambiente virtual...")
        
        # Cria venv se não existir
        if not os.path.exists("venv"):
            subprocess.check_call([python_cmd, "-m", "venv", "venv"])
        
        # Ativa venv e instala dependências
        if is_windows:
            activate_cmd = os.path.join("venv", "Scripts", "activate")
            pip_cmd = os.path.join("venv", "Scripts", "pip")
        else:
            activate_cmd = os.path.join("venv", "bin", "activate")
            pip_cmd = os.path.join("venv", "bin", "pip")
            
        # Atualiza pip
        subprocess.check_call([pip_cmd, "install", "--upgrade", "pip"])
        
        # Instala dependências
        print("Instalando dependências...")
        subprocess.check_call([pip_cmd, "install", "-r", "web_app/requirements.txt"])
        
        print("""
Ambiente configurado com sucesso!

Para ativar o ambiente:
- Windows: .\\venv\\Scripts\\activate
- Linux/Mac: source venv/bin/activate

Para iniciar a aplicação:
- Ative o venv
- Execute: python tools/run_webapp.py
        """)
        
    except Exception as e:
        print(f"Erro na configuração: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    setup_venv() 