import socket
import select
import os

class DNSServer:
    """Servidor DNS simples para captive portal"""
    
    def __init__(self):
        self.sock = None
        self.running = False
        
    def start(self):
        """Inicia o servidor DNS"""
        try:
            # Cria socket UDP
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            
            # Força bind na porta 53
            try:
                self.sock.bind(('0.0.0.0', 53))
            except:
                os.umount('/dns_port')  # Libera porta 53 se necessário
                self.sock.bind(('0.0.0.0', 53))
                
            self.running = True
            
            # Loop principal com timeout curto
            while self.running:
                try:
                    data, addr = self.sock.recvfrom(1024)
                    response = self._build_response(data)
                    if response:
                        self.sock.sendto(response, addr)
                except:
                    pass
                    
        except Exception as e:
            print(f'Erro no servidor DNS: {e}')
            self.stop()
            
    def stop(self):
        """Para o servidor DNS"""
        self.running = False
        if self.sock:
            self.sock.close()
            self.sock = None
            
    def _handle_request(self):
        """Processa uma requisição DNS"""
        try:
            # Recebe dados
            data, addr = self.sock.recvfrom(1024)
            
            # Monta resposta redirecionando para IP local
            response = self._build_response(data)
            
            # Envia resposta
            if response:
                self.sock.sendto(response, addr)
                
        except Exception as e:
            print(f'Erro ao processar requisição DNS: {e}')
            
    def _build_response(self, data):
        """Monta pacote de resposta DNS"""
        try:
            # Cabeçalho DNS
            header = data[:12]
            
            # Modifica flags
            flags = bytearray(header[2:4])
            flags[0] |= 0x80  # QR=1 (resposta)
            flags[0] &= 0x7f  # RCODE=0 (sem erro)
            flags[1] &= 0x7f  # RA=0
            
            # Monta resposta
            response = bytearray(header[:2] + flags + header[4:])
            response[7] = 1  # ANCOUNT=1
            
            # Adiciona query original
            response.extend(data[12:])
            
            # Adiciona resposta apontando para 192.168.4.1
            response.extend(b'\xc0\x0c')  # Ponteiro para nome
            response.extend(b'\x00\x01')  # TYPE=A
            response.extend(b'\x00\x01')  # CLASS=IN
            response.extend(b'\x00\x00\x00\x3c')  # TTL=60s
            response.extend(b'\x00\x04')  # RDLENGTH=4
            
            # IP 192.168.4.1 em bytes
            response.extend(bytes([192, 168, 4, 1]))
            
            return response
            
        except Exception as e:
            print(f'Erro ao montar resposta DNS: {e}')
            return None 