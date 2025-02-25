import os
import sys
import subprocess
import webbrowser
import time
import platform

class StreamlitRunner:
    def __init__(self):
        self.port = 8501
        self.app_path = os.path.join('web_app', 'app.py')
        
    def check_dependencies(self):
        """Verifica e instala dependências necessárias"""
        print("🔍 Verificando dependências...")
        
        required_packages = [
            'streamlit',
            'pandas',
            'plotly',
            'requests'
        ]
        
        for package in required_packages:
            try:
                __import__(package)
                print(f"✅ {package} já instalado")
            except ImportError:
                print(f"📦 Instalando {package}...")
                subprocess.check_call([sys.executable, "-m", "pip", "install", package])
                
    def is_port_in_use(self):
        """Verifica se a porta está em uso"""
        import socket
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            return s.connect_ex(('localhost', self.port)) == 0
            
    def find_available_port(self):
        """Encontra uma porta disponível"""
        while self.is_port_in_use():
            self.port += 1
            
    def get_local_ip(self):
        """Obtém IP local da máquina"""
        import socket
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            s.connect(('10.255.255.255', 1))
            ip = s.getsockname()[0]
        except Exception:
            ip = '127.0.0.1'
        finally:
            s.close()
        return ip
        
    def run(self):
        """Executa a aplicação Streamlit"""
        try:
            # Verifica dependências
            self.check_dependencies()
            
            # Encontra porta disponível
            self.find_available_port()
            
            # Obtém IP local
            local_ip = self.get_local_ip()
            
            print("\n🚀 Iniciando JohnDeere Monitor...")
            print("=" * 50)
            print(f"📱 Interface Web: http://{local_ip}:{self.port}")
            print("=" * 50)
            
            # Abre navegador
            webbrowser.open(f"http://localhost:{self.port}")
            
            # Inicia Streamlit
            os.environ['STREAMLIT_SERVER_PORT'] = str(self.port)
            subprocess.run([
                "streamlit", 
                "run", 
                self.app_path,
                "--server.address", "0.0.0.0",
                "--browser.serverAddress", local_ip,
                "--theme.primaryColor", "#367C2B",
                "--theme.secondaryBackgroundColor", "#f0f0f0",
                "--theme.textColor", "#262730"
            ])
            
        except KeyboardInterrupt:
            print("\n⛔ Aplicação encerrada pelo usuário")
        except Exception as e:
            print(f"\n❌ Erro ao iniciar aplicação: {e}")
            
def main():
    # Verifica se está no diretório correto
    if not os.path.exists('web_app/app.py'):
        print("❌ Execute este script do diretório raiz do projeto")
        sys.exit(1)
        
    runner = StreamlitRunner()
    runner.run()

if __name__ == "__main__":
    main() 