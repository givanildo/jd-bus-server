import os
import sys
import time
import serial
import serial.tools.list_ports

def find_esp32_port():
    """Encontra a porta serial do ESP32"""
    ports = list(serial.tools.list_ports.comports())
    for port in ports:
        if "CP210x" in port.description or "CH340" in port.description:
            return port.device
    return None

def upload_file(port, file_path):
    """Faz upload de um arquivo para o ESP32"""
    try:
        # Abre conexão serial
        ser = serial.Serial(port, 115200, timeout=1)
        print(f"Conectado à porta {port}")
        
        # Lê o arquivo
        with open(file_path, 'rb') as f:
            content = f.read()
            
        # Nome do arquivo de destino no ESP32
        dest_file = os.path.basename(file_path)
        
        # Envia comando para criar arquivo
        print(f"Enviando {dest_file}...")
        ser.write(f"f = open('{dest_file}', 'wb')\r\n".encode())
        time.sleep(0.5)
        
        # Envia conteúdo em chunks
        chunk_size = 512
        for i in range(0, len(content), chunk_size):
            chunk = content[i:i+chunk_size]
            ser.write(f"f.write({chunk})\r\n".encode())
            time.sleep(0.1)
            print(f"Progresso: {min((i+chunk_size)*100/len(content), 100):.1f}%")
            
        # Fecha arquivo
        ser.write(b"f.close()\r\n")
        print(f"Arquivo {dest_file} enviado com sucesso!")
        
    except Exception as e:
        print(f"Erro ao enviar arquivo: {str(e)}")
    finally:
        if 'ser' in locals():
            ser.close()

def main():
    # Encontra porta do ESP32
    port = find_esp32_port()
    if not port:
        print("ESP32 não encontrado! Verifique a conexão.")
        return
        
    # Arquivos para upload
    esp32_files = [
        'main.py',
        'web_server.py',
        'wifi_manager.py',
        'can_handler.py',
        'dns_server.py',
        'captive_portal.py'
    ]
    
    # Faz upload de cada arquivo
    for file in esp32_files:
        file_path = os.path.join('esp32', file)
        if os.path.exists(file_path):
            upload_file(port, file_path)
        else:
            print(f"Arquivo {file} não encontrado!")
            
    print("\nUpload concluído! Reinicie o ESP32.")

if __name__ == "__main__":
    main() 