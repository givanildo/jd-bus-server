import socket
import _thread

class DNSServer:
    def __init__(self):
        self.socket = None
        self.running = True
        
    def start(self):
        """Inicia servidor DNS em thread separada"""
        _thread.start_new_thread(self._run_server, ())
        
    def _run_server(self):
        """Loop principal do servidor DNS"""
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind(('', 53))
        
        while self.running:
            try:
                # Recebe pacote DNS
                data, addr = self.socket.recvfrom(4096)
                
                # Responde com IP do ESP32
                response = self.build_response(data)
                self.socket.sendto(response, addr)
            except Exception as e:
                print(f"Erro DNS: {e}")
                
    def stop(self):
        """Para o servidor DNS"""
        self.running = False
        if self.socket:
            self.socket.close()
            
    def build_response(self, data):
        """Constrói resposta DNS redirecionando para 192.168.4.1"""
        # Cabeçalho DNS padrão
        header = data[:12]
        # Modifica flags para resposta
        header = header[:2] + b'\x81\x80' + header[4:]
        
        # Questão original
        question = data[12:]
        
        # Resposta apontando para 192.168.4.1
        answer = (
            b'\xc0\x0c'  # Pointer para nome
            b'\x00\x01'  # Type A
            b'\x00\x01'  # Class IN
            b'\x00\x00\x00\x3c'  # TTL (60 segundos)
            b'\x00\x04'  # Data length
            b'\xc0\xa8\x04\x01'  # IP (192.168.4.1)
        )
        
        return header + question + answer 