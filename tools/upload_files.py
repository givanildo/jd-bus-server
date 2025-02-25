import sys
import time
import subprocess
import os
from serial.tools import list_ports
import serial

def install_dependencies():
    """Instala dependências necessárias"""
    print("\nInstalando dependências...")
    dependencies = [
        "esptool",
        "mpremote",
        "pyserial",
        "streamlit",
        "plotly",
        "pandas",
        "requests"
    ]
    
    for dep in dependencies:
        try:
            print(f"Instalando {dep}...")
            subprocess.run([
                sys.executable, "-m", "pip", "install", "--upgrade", dep
            ], check=True)
        except Exception as e:
            print(f"Erro ao instalar {dep}: {e}")
            return False
    return True

def find_esp32_port():
    """Encontra a porta COM do ESP32"""
    ports = list(list_ports.comports())
    for port in ports:
        if any(id in port.description for id in ["CP210", "CH340", "USB Serial"]):
            return port.device
    return None

def flash_micropython(port):
    """Instala o MicroPython no ESP32"""
    firmware_path = "esp32/firmware/ESP32_GENERIC-20241129-v1.24.1.bin"
    
    if not os.path.exists(firmware_path):
        print(f"Erro: Firmware não encontrado em {firmware_path}")
        print("Verifique se o arquivo está na pasta correta.")
        return False
        
    try:
        print("\nApagando flash do ESP32...")
        subprocess.run([
            sys.executable, "-m", "esptool", 
            "--port", port, 
            "--baud", "460800",
            "erase_flash"
        ], check=True)
        time.sleep(2)
        
        print("\nInstalando MicroPython...")
        subprocess.run([
            sys.executable, "-m", "esptool",
            "--port", port,
            "--baud", "460800",
            "write_flash",
            "--flash_size=detect", "0x1000",
            firmware_path
        ], check=True)
        
        print("\nMicroPython instalado com sucesso!")
        time.sleep(3)
        return True
        
    except Exception as e:
        print(f"\nErro durante instalação: {e}")
        return False

def transfer_files(port):
    """Transfere os arquivos Python para o ESP32"""
    try:
        # Lista de arquivos para transferir
        files = [
            ("esp32/main.py", ":main.py"),
            ("esp32/can_handler.py", ":can_handler.py"),
            ("esp32/wifi_manager.py", ":wifi_manager.py"),
            ("esp32/web_server.py", ":web_server.py"),
            ("esp32/j1939_decoder.py", ":j1939_decoder.py"),
            ("esp32/logger.py", ":logger.py"),
            ("esp32/lib/dns.py", ":dns.py"),
            ("esp32/lib/captive_portal.py", ":captive_portal.py"),
            ("esp32/lib/microdot.py", ":microdot.py"),
            ("esp32/lib/mcp2515.py", ":mcp2515.py")
        ]
        
        # Verifica arquivos
        missing = [f for f, _ in files if not os.path.exists(f)]
        if missing:
            print("\nArquivos não encontrados:")
            for f in missing:
                print(f"- {f}")
            return False
        
        # Transfere arquivos
        print("\nTransferindo arquivos...")
        for local, remote in files:
            print(f"Enviando {os.path.basename(local)}...")
            try:
                subprocess.run([
                    sys.executable, "-m", "mpremote",
                    "connect", port,
                    "cp", local, remote
                ], check=True)
                time.sleep(1)
            except Exception as e:
                print(f"Erro ao enviar {local}: {e}")
                return False
            
        print("\nTodos os arquivos transferidos com sucesso!")
        return True
        
    except Exception as e:
        print(f"\nErro durante transferência: {e}")
        return False

def monitor_serial(port):
    """Monitora a saída serial do ESP32"""
    try:
        print("\nMonitorando saída serial (Ctrl+C para sair)...")
        
        with serial.Serial(port, 115200, timeout=1) as ser:
            while True:
                if ser.in_waiting:
                    try:
                        line = ser.readline().decode('utf-8').strip()
                        if line:
                            print(line)
                    except UnicodeDecodeError:
                        pass
                time.sleep(0.1)
                
    except KeyboardInterrupt:
        print("\nMonitoramento interrompido")
    except Exception as e:
        print(f"\nErro no monitoramento: {e}")

def main():
    try:
        # 0. Instalar dependências
        print("Verificando dependências...")
        if not install_dependencies():
            print("Erro ao instalar dependências")
            return
            
        # 1. Encontrar ESP32
        print("\nProcurando ESP32...")
        port = find_esp32_port()
        if not port:
            print("ESP32 não encontrado!")
            print("Verifique conexão e drivers")
            return
        print(f"ESP32 encontrado na porta: {port}")
        
        # 2. Instalar MicroPython
        if not flash_micropython(port):
            return
            
        # 3. Transferir arquivos
        if not transfer_files(port):
            return
        
        print("\nInstalação concluída!")
        print("Aguarde o ESP32 reiniciar...")
        print("Procure pela rede 'JohnDeere_Monitor'")
        
        # 4. Monitorar serial
        monitor_serial(port)
        
    except Exception as e:
        print(f"\nErro: {e}")

if __name__ == "__main__":
    main() 