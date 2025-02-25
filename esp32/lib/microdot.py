# Baixar de: https://github.com/miguelgrinberg/microdot 

class Response:
    """Classe para respostas HTTP"""
    def __init__(self, body='', status_code=200, headers=None):
        self.status_code = status_code
        self.headers = headers or {}
        self.body = body
        
        # Define content-type padrão
        if 'Content-Type' not in self.headers:
            self.headers['Content-Type'] = 'text/plain'
            
        # Adiciona CORS headers
        self.headers.update({
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
            'Access-Control-Allow-Headers': '*'
        })

class Microdot:
    """Servidor web minimalista"""
    def __init__(self):
        self.routes = {}
        
    def route(self, path, methods=None):
        """Decorador para registrar rotas"""
        if methods is None:
            methods = ['GET']
            
        def decorator(handler):
            self.routes[path] = {
                'handler': handler,
                'methods': methods
            }
            return handler
        return decorator
        
    def run(self, host='0.0.0.0', port=80, debug=False):
        """Inicia o servidor"""
        import socket
        
        s = socket.socket()
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((host, port))
        s.listen(1)
        
        while True:
            try:
                conn, addr = s.accept()
                request = conn.recv(1024).decode()
                
                # Processa requisição
                try:
                    # Extrai método e path
                    method = request.split()[0]
                    path = request.split()[1]
                    
                    # Busca rota
                    if path in self.routes:
                        route = self.routes[path]
                        if method in route['methods']:
                            response = route['handler'](request)
                        else:
                            response = Response('Method not allowed', 405)
                    else:
                        response = Response('Not found', 404)
                        
                except Exception as e:
                    if debug:
                        response = Response(str(e), 500)
                    else:
                        response = Response('Internal error', 500)
                
                # Envia resposta
                status_line = f'HTTP/1.0 {response.status_code}\r\n'
                headers = '\r\n'.join([f'{k}: {v}' for k, v in response.headers.items()])
                conn.send(f'{status_line}{headers}\r\n\r\n{response.body}'.encode())
                
            except Exception as e:
                if debug:
                    print(f'Server error: {e}')
                    
            finally:
                conn.close() 