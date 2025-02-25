from microdot import Response
import json
import os
from logger import Logger
import time
import socket
import _thread
import ubinascii
import urandom
from dns import DNSServer
from captive_portal import CaptivePortal

class WebServer:
    # Portas configuráveis
    WEB_PORT = 80        # Volta para 80 em modo AP
    DATA_PORT = 8502     # Porta de dados
    DNS_PORT = 53        # DNS
    
    def __init__(self, wifi_manager, can_handler):
        self.wifi_manager = wifi_manager
        self.can_handler = can_handler
        self.logger = Logger()
        self.auth_token = None
        self.load_or_create_token()
        self.running = True
        self.dns_server = None
        self.captive_portal = None
        
    def load_or_create_token(self):
        """Carrega ou cria token de autenticação"""
        try:
            if 'auth_token.txt' in os.listdir():
                with open('auth_token.txt', 'r') as f:
                    self.auth_token = f.read().strip()
            else:
                # Gera token aleatório simples
                token = bytes([urandom.getrandbits(8) for _ in range(16)])
                self.auth_token = ubinascii.hexlify(token).decode()
                with open('auth_token.txt', 'w') as f:
                    f.write(self.auth_token)
        except Exception as e:
            self.logger.error('web_server', f'Erro ao carregar token: {e}')
            
    def check_auth(self, request):
        """Verifica autenticação da requisição"""
        if self.wifi_manager.get_status()['ap_active']:
            return True  # Não requer auth em modo AP
            
        token = request.headers.get('X-Auth-Token')
        if not token:
            return False
        return token == self.auth_token
        
    def handle_request(self, client):
        """Processa requisição HTTP"""
        try:
            request = client.recv(1024).decode()
            self.logger.debug('web_server', f'Nova requisição: {request.splitlines()[0]}')
            
            # Verifica CORS
            if "OPTIONS" in request:
                return self.send_cors_headers(client)
                
            # Rotas principais
            if "GET / " in request:
                if self.wifi_manager.get_status()['ap_active']:
                    # Em modo AP: mostra página de configuração WiFi
                    return self.send_html_response(client, self.captive_portal.get_config_page())
                else:
                    # Em modo cliente: mostra página de dados CAN
                    return self.send_html_response(client, self.get_status_page())
                    
            elif "GET /scan" in request:
                networks = self.wifi_manager.scan_networks()
                return self.send_json_response(client, {'networks': networks})
                
            elif "GET /data" in request:
                data = self.can_handler.read_message()
                return self.send_json_response(client, {
                    'data': data,
                    'timestamp': time.time()
                })
                
            elif "POST /connect" in request:
                body = request.split('\r\n\r\n')[1]
                config = json.loads(body)
                success = self.wifi_manager.connect(config['ssid'], config['password'])
                
                if success:
                    # Desativa modo AP
                    self.wifi_manager.stop_ap()
                    if self.dns_server:
                        self.dns_server.stop()
                    self.running = False
                    
                return self.send_json_response(client, {
                    'status': 'success' if success else 'error',
                    'ip': self.wifi_manager.get_status()['sta_ip']
                })
                
        except Exception as e:
            self.logger.error('web_server', f'Erro: {e}')
            return self.send_error(client, str(e))
        finally:
            client.close()
            
    def validate_config(self, config):
        """Valida dados de configuração"""
        required = ['ssid', 'password']
        return all(k in config for k in required) and \
               isinstance(config['ssid'], str) and \
               isinstance(config['password'], str) and \
               len(config['ssid']) >= 1 and \
               len(config['password']) >= 8
               
    def send_cors_headers(self, client):
        """Envia headers CORS"""
        response = """HTTP/1.1 200 OK
Access-Control-Allow-Origin: *
Access-Control-Allow-Methods: GET, POST, OPTIONS
Access-Control-Allow-Headers: Content-Type
Access-Control-Max-Age: 86400

"""
        client.send(response.encode())
        
    def send_unauthorized(self, client):
        """Envia resposta não autorizado"""
        response = """HTTP/1.1 401 Unauthorized
Content-Type: application/json

{"error": "Não autorizado"}"""
        client.send(response.encode())
        
    def send_error(self, client, message):
        """Envia resposta de erro"""
        response = f"""HTTP/1.1 400 Bad Request
Content-Type: application/json

{{"error": "{message}"}}"""
        client.send(response.encode())

    def start_ap_mode(self):
        """Inicia modo AP com captive portal"""
        try:
            self.logger.info('web_server', 'Iniciando modo AP...')
            
            # Configura WiFi em modo AP
            self.wifi_manager.start_ap()
            
            # Inicia servidor DNS
            self.logger.info('web_server', 'Iniciando servidor DNS...')
            self.dns_server = DNSServer()
            _thread.start_new_thread(self.dns_server.start, ())
            
            # Configura portal captivo
            self.logger.info('web_server', 'Configurando portal captivo...')
            self.captive_portal = CaptivePortal()
            
            # Inicia servidor web na porta 80
            self.logger.info('web_server', 'Iniciando servidor web na porta 80...')
            sock = socket.socket()
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.bind(('0.0.0.0', 80))  # Força porta 80 em modo AP
            sock.listen(1)
            
            while self.running:
                try:
                    client, addr = sock.accept()
                    self.logger.debug('web_server', f'Nova conexão de {addr}')
                    self.handle_request(client)
                except Exception as e:
                    self.logger.error('web_server', f'Erro na conexão: {e}')
                    
        except Exception as e:
            self.logger.error('web_server', f'Erro no modo AP: {e}')
            
    def start_basic_server(self):
        """Inicia servidor web básico"""
        try:
            sock = socket.socket()
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.bind(('0.0.0.0', self.WEB_PORT))
            sock.listen(1)
            self.logger.info('web_server', f'Servidor web pronto na porta {self.WEB_PORT}')
            
            while self.running:
                try:
                    client, addr = sock.accept()
                    self.logger.debug('web_server', f'Nova conexão de {addr}')
                    self.handle_request(client)
                except Exception as e:
                    self.logger.error('web_server', f'Erro na conexão: {e}')
                
        except Exception as e:
            self.logger.error('web_server', f'Erro ao iniciar servidor web: {e}')
            
    def start_data_server(self):
        """Inicia servidor de dados"""
        try:
            self.data_socket = socket.socket()
            self.data_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.data_socket.bind(('0.0.0.0', self.DATA_PORT))
            self.data_socket.listen(1)
            self.logger.info('web_server', f'Servidor de dados iniciado na porta {self.DATA_PORT}')
            _thread.start_new_thread(self._handle_data_requests, ())
            
        except Exception as e:
            self.logger.error('web_server', f'Erro ao iniciar servidor de dados: {e}')
            
    def _handle_data_requests(self):
        """Processa requisições de dados do Streamlit"""
        while self.running:
            try:
                client, addr = self.data_socket.accept()
                self.logger.debug('web_server', f'Nova conexão de dados de {addr}')
                
                request = client.recv(1024).decode()
                if "GET /data" in request:
                    data = self.can_handler.read_message()
                    response = {
                        'timestamp': time.time(),
                        'data': data
                    }
                    self.send_json_response(client, response)
                    
                client.close()
                
            except Exception as e:
                self.logger.error('web_server', f'Erro ao processar dados: {e}')
                
    def send_json_response(self, client, data):
        """Envia resposta JSON"""
        response = f"""HTTP/1.1 200 OK
Content-Type: application/json
Access-Control-Allow-Origin: *

{json.dumps(data)}"""
        client.send(response.encode())
        
    def send_html_response(self, client, html):
        """Envia resposta HTML"""
        response = f"""HTTP/1.1 200 OK
Content-Type: text/html
Access-Control-Allow-Origin: *

{html}"""
        client.send(response.encode())

    def handle_disconnect(self):
        """Trata desconexão WiFi"""
        self.logger.warning('web_server', 'Conexão WiFi perdida')
        self.running = False
        self.start_ap_mode()

    def apply_config(self, config):
        """Aplica configurações"""
        try:
            if 'wifi' in config:
                return self.wifi_manager.connect(config['wifi']['ssid'], 
                                              config['wifi']['password'])
            return False
        except Exception as e:
            self.logger.error('web_server', f'Erro ao aplicar config: {e}')
            return False

    def start(self):
        """Inicia os servidores"""
        try:
            if self.wifi_manager.connect_saved():
                self.logger.info('web_server', 'Conectado à rede WiFi')
                self.start_data_server()
                self.start_basic_server()
            else:
                self.logger.info('web_server', 'Iniciando modo AP')
                self.start_ap_mode()
                
        except Exception as e:
            self.logger.error('web_server', f'Erro ao iniciar servidor: {e}') 

    def cleanup(self):
        """Limpa recursos do servidor"""
        try:
            self.logger.info('web_server', 'Limpando recursos...')
            
            # Para threads e servidores
            self.running = False
            
            # Limpa servidor de dados
            if hasattr(self, 'data_socket'):
                try:
                    self.data_socket.close()
                except:
                    pass
                    
            # Para servidor DNS
            if self.dns_server:
                try:
                    self.dns_server.stop()
                except:
                    pass
                    
            # Fecha sockets abertos
            for attr in dir(self):
                obj = getattr(self, attr)
                if isinstance(obj, socket.socket):
                    try:
                        obj.close()
                    except:
                        pass
                    
            self.logger.info('web_server', 'Recursos liberados')
            
        except Exception as e:
            self.logger.error('web_server', f'Erro ao limpar recursos: {e}') 

    def get_status_page(self):
        """Retorna página de status do sistema"""
        return """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>JohnDeere Monitor</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        :root {
            --jd-green: #367C2B;
            --jd-yellow: #FDB515;
        }
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 0;
            background: #f4f4f4;
        }
        .header {
            background: var(--jd-green);
            color: white;
            padding: 1rem;
            text-align: center;
            border-bottom: 4px solid var(--jd-yellow);
        }
        .container {
            max-width: 1200px;
            margin: 20px auto;
            padding: 20px;
        }
        .card {
            background: white;
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
        }
        .metric {
            background: white;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .metric-value {
            font-size: 24px;
            font-weight: bold;
            color: var(--jd-green);
            margin: 10px 0;
        }
        .metric-label {
            color: #666;
            font-size: 14px;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }
        th, td {
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }
        th {
            background: var(--jd-green);
            color: white;
        }
        tr:nth-child(even) {
            background: #f9f9f9;
        }
        .status {
            display: inline-block;
            width: 10px;
            height: 10px;
            border-radius: 50%;
            margin-right: 5px;
        }
        .status.online {
            background: #4CAF50;
        }
        h2 {
            color: var(--jd-green);
            margin-top: 30px;
        }
        .btn {
            background: var(--jd-yellow);
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 4px;
            cursor: pointer;
        }
        .btn:hover {
            background: #e5a313;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>🚜 JohnDeere Monitor</h1>
    </div>

    <div class="container">
        <div class="grid">
            <div class="metric">
                <div class="metric-label">Status</div>
                <div class="metric-value">
                    <span class="status online"></span>
                    Online
                </div>
            </div>
            <div class="metric">
                <div class="metric-label">IP</div>
                <div class="metric-value" id="system-ip">-</div>
            </div>
            <div class="metric">
                <div class="metric-label">Porta de Dados</div>
                <div class="metric-value">8502</div>
            </div>
        </div>

        <h2>📊 Dados CAN</h2>
        <div class="card">
            <table>
                <thead>
                    <tr>
                        <th>PGN</th>
                        <th>Descrição</th>
                        <th>Valor</th>
                        <th>Unidade</th>
                        <th>Timestamp</th>
                    </tr>
                </thead>
                <tbody id="can-data">
                    <!-- Dados serão inseridos aqui -->
                </tbody>
            </table>
        </div>

        <h2>⚙️ Configurações</h2>
        <div class="card">
            <table>
                <tr>
                    <td><strong>Rede:</strong></td>
                    <td id="wifi-ssid">-</td>
                </tr>
                <tr>
                    <td><strong>Sinal:</strong></td>
                    <td id="wifi-signal">-</td>
                </tr>
                <tr>
                    <td><strong>Modo:</strong></td>
                    <td>Cliente</td>
                </tr>
            </table>
        </div>
    </div>

    <script>
        // Atualiza IP e SSID
        document.getElementById('system-ip').textContent = window.location.hostname;
        
        // Atualiza dados CAN a cada segundo
        setInterval(async () => {
            try {
                const response = await fetch('/data');
                const data = await response.json();
                
                if (data && data.data) {
                    const tbody = document.getElementById('can-data');
                    tbody.innerHTML = '';
                    
                    for (const [key, value] of Object.entries(data.data)) {
                        const row = document.createElement('tr');
                        row.innerHTML = `
                            <td>${getPGN(key)}</td>
                            <td>${getDescription(key)}</td>
                            <td>${value}</td>
                            <td>${getUnit(key)}</td>
                            <td>${new Date().toLocaleTimeString()}</td>
                        `;
                        tbody.appendChild(row);
                    }
                }
            } catch (error) {
                console.error('Erro:', error);
            }
        }, 1000);

        // Funções auxiliares
        function getPGN(key) {
            const pgns = {
                'engine_speed': '0xF004',
                'engine_temp': '0xFEEE',
                'vehicle_speed': '0xFEF1'
            };
            return pgns[key] || '-';
        }

        function getDescription(key) {
            const descriptions = {
                'engine_speed': 'Velocidade do Motor',
                'engine_temp': 'Temperatura do Motor',
                'vehicle_speed': 'Velocidade do Veículo'
            };
            return descriptions[key] || key;
        }

        function getUnit(key) {
            const units = {
                'engine_speed': 'RPM',
                'engine_temp': '°C',
                'vehicle_speed': 'km/h'
            };
            return units[key] || '-';
        }
    </script>
</body>
</html>
""" 