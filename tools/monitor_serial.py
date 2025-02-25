import serial
import serial.tools.list_ports
import time
import argparse
from datetime import datetime
import os

class SerialMonitor:
    # Configurações padrão
    DEFAULT_BAUDRATE = 115200
    DEFAULT_TIMEOUT = 1
    
    def __init__(self, port=None, baudrate=DEFAULT_BAUDRATE):
        self.port = port
        self.baudrate = baudrate
        self.serial = None
        print(f"\n🔧 Configuração:")
        print(f"   Baudrate: {self.baudrate} bps")
        print(f"   Timeout: {self.DEFAULT_TIMEOUT}s")
        
    def find_esp32(self):
        """Procura porta do ESP32"""
        print("\n🔍 Procurando ESP32...")
        ports = list(serial.tools.list_ports.comports())
        
        if not ports:
            print("❌ Nenhuma porta serial encontrada!")
            return None
            
        print("\n📝 Portas disponíveis:")
        for i, port in enumerate(ports):
            print(f"{i+1}. {port.device} - {port.description}")
            
        if len(ports) == 1:
            print(f"\n✅ ESP32 encontrado em {ports[0].device}")
            return ports[0].device
            
        try:
            choice = input("\n🔍 Escolha a porta (número): ")
            idx = int(choice) - 1
            if 0 <= idx < len(ports):
                return ports[idx].device
        except:
            pass
            
        return None
        
    def connect(self):
        """Conecta na porta serial"""
        try:
            if not self.port:
                self.port = self.find_esp32()
                if not self.port:
                    print("❌ ESP32 não encontrado!")
                    return False
                    
            print(f"\n🔌 Conectando em {self.port} @ {self.baudrate} bps...")
            
            self.serial = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                timeout=self.DEFAULT_TIMEOUT,
                write_timeout=self.DEFAULT_TIMEOUT
            )
            
            # Limpa buffers
            self.serial.reset_input_buffer()
            self.serial.reset_output_buffer()
            
            print("✅ Conectado com sucesso!")
            return True
            
        except Exception as e:
            print(f"❌ Erro ao conectar: {e}")
            return False
            
    def save_log(self, message):
        """Salva mensagem no arquivo de log"""
        try:
            if not os.path.exists('logs'):
                os.makedirs('logs')
                
            filename = f"logs/esp32_{datetime.now().strftime('%Y%m%d')}.log"
            
            with open(filename, 'a', encoding='utf-8') as f:
                timestamp = datetime.now().strftime('%H:%M:%S')
                f.write(f"[{timestamp}] {message}\n")
                
        except Exception as e:
            print(f"❌ Erro ao salvar log: {e}")
            
    def monitor(self):
        """Monitora porta serial"""
        if not self.serial:
            return
            
        print("\n📡 Monitorando ESP32... (Ctrl+C para parar)\n")
        
        try:
            while True:
                try:
                    # Tenta ler uma linha
                    if self.serial.in_waiting:
                        line = self.serial.readline()
                        
                        # Tenta diferentes codificações
                        for encoding in ['utf-8', 'ascii', 'latin1']:
                            try:
                                message = line.decode(encoding).strip()
                                if message:  # Ignora linhas vazias
                                    timestamp = datetime.now().strftime('%H:%M:%S')
                                    
                                    # Formata mensagem baseado no tipo
                                    if 'error' in message.lower():
                                        print(f"🔴 [{timestamp}] {message}")
                                    elif 'warning' in message.lower():
                                        print(f"🟡 [{timestamp}] {message}")
                                    elif 'info' in message.lower():
                                        print(f"🟢 [{timestamp}] {message}")
                                    else:
                                        print(f"⚪ [{timestamp}] {message}")
                                        
                                    self.save_log(message)
                                    break
                            except:
                                continue
                                
                    time.sleep(0.1)  # Pequena pausa para não sobrecarregar
                    
                except serial.SerialException as e:
                    print(f"\n❌ Erro na serial: {e}")
                    break
                    
        except KeyboardInterrupt:
            print("\n⛔ Monitoramento interrompido pelo usuário")
        except Exception as e:
            print(f"\n❌ Erro inesperado: {e}")
        finally:
            if self.serial and self.serial.is_open:
                self.serial.close()
                print("📍 Porta serial fechada")

def main():
    parser = argparse.ArgumentParser(
        description='Monitor Serial ESP32',
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument(
        '-p', '--port',
        help='Porta serial (ex: COM3, /dev/ttyUSB0)'
    )
    parser.add_argument(
        '-b', '--baud',
        type=int,
        default=SerialMonitor.DEFAULT_BAUDRATE,
        help=f'Baudrate (padrão: {SerialMonitor.DEFAULT_BAUDRATE})'
    )
    
    args = parser.parse_args()
    
    print("\n🚀 Monitor Serial ESP32")
    print("=" * 50)
    
    monitor = SerialMonitor(args.port, args.baud)
    if monitor.connect():
        monitor.monitor()

if __name__ == "__main__":
    main() 