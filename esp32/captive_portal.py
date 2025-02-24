import socket
import _thread

class CaptivePortal:
    def __init__(self):
        self.socket = None
        self.running = True
        
    def handle_request(self, client):
        """Redireciona todas requisições para página de configuração"""
        try:
            request = client.recv(1024).decode()
            
            # Envia redirecionamento
            response = """HTTP/1.1 302 Found
Location: http://192.168.4.1
Connection: close

"""
            client.send(response)
            
        except Exception as e:
            print(f"Erro no captive portal: {str(e)}")
        finally:
            client.close()
            
    def start(self):
        """Inicia portal em thread separada"""
        _thread.start_new_thread(self._run_server, ())
        
    def _run_server(self):
        """Loop principal do portal"""
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind(('', 80))
        self.socket.listen(5)
        
        while self.running:
            try:
                client, addr = self.socket.accept()
                _thread.start_new_thread(self.handle_request, (client,))
            except Exception as e:
                print(f"Erro portal: {e}")
                
    def stop(self):
        """Para o servidor"""
        if self.socket:
            self.socket.close() 