from microdot import Microdot, Response
import network
import json
from dns.server import DNSServer
from captive_portal import CaptivePortal
from wifi_manager import WifiManager
import socket
import _thread

app = Microdot()
dns_server = None
captive_portal = None
wifi_manager = WifiManager()

# Porta específica para comunicação remota
SERVER_PORT = 8080

# Configuração do servidor web
def start_server():
    # Permitir conexões de qualquer origem (CORS)
    @app.route("/data", methods=["GET", "OPTIONS"])
    def get_data():
        if request.method == "OPTIONS":
            response = Response()
            response.headers["Access-Control-Allow-Origin"] = "*"
            response.headers["Access-Control-Allow-Headers"] = "*"
            response.headers["Access-Control-Allow-Methods"] = "GET"
            return response
            
        data = can_handler.get_latest_data()
        response = Response(json.dumps(data))
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Content-Type"] = "application/json"
        return response

    print(f"Servidor iniciado na porta {SERVER_PORT}")
    app.run(port=SERVER_PORT, debug=True)

@app.route('/api/wifi/scan')
def get_wifi_networks(request):
    networks = wifi_manager.scan_networks()
    return {'networks': networks}

@app.route('/api/wifi/connect', methods=['POST'])
def connect_wifi(request):
    data = request.json
    ssid = data.get('ssid')
    password = data.get('password')
    
    success = wifi_manager.connect(ssid, password)
    if success:
        # Após conectar com sucesso, inicia servidor na porta específica
        start_data_server()
        return {'status': 'success'}
    return {'status': 'error'}

def start_ap_mode():
    global dns_server, captive_portal
    
    wifi_manager.start_ap()
    dns_server = DNSServer()
    dns_server.start()
    
    captive_portal = CaptivePortal()
    app.run(port=80, debug=True)

def start_data_server():
    print(f"Iniciando servidor de dados na porta {SERVER_PORT}")
    # Inicia o servidor na porta específica após conectar à rede
    app.run(port=SERVER_PORT, debug=True)

def start_server():
    if wifi_manager.is_configured():
        if wifi_manager.connect_saved():
            start_data_server()
        else:
            start_ap_mode()
    else:
        start_ap_mode()

class WebServer:
    def __init__(self, wifi_manager, can_handler):
        self.wifi_manager = wifi_manager
        self.can_handler = can_handler
        self.socket = None
        self.can_data = []
        self.monitoring = True
        self.remote_server = Microdot()
        
    def setup_remote_server(self):
        """Configura servidor remoto na porta 8502"""
        @self.remote_server.route("/data", methods=["GET", "OPTIONS"])
        def get_remote_data(request):
            if request.method == "OPTIONS":
                response = Response()
                response.headers["Access-Control-Allow-Origin"] = "*"
                response.headers["Access-Control-Allow-Headers"] = "*"
                response.headers["Access-Control-Allow-Methods"] = "GET"
                return response
                
            data = self.can_handler.read_message()
            if data:
                self.can_data.append(data)
                if len(self.can_data) > 100:
                    self.can_data.pop(0)
                    
            response = Response(json.dumps({
                "current": data,
                "history": self.can_data
            }))
            response.headers["Access-Control-Allow-Origin"] = "*"
            response.headers["Content-Type"] = "application/json"
            return response
            
        # Inicia servidor remoto em thread separada
        _thread.start_new_thread(self.remote_server.run, (), {'port': 8502, 'debug': True})
    
    def start(self):
        """Inicia servidor web principal"""
        # Inicia servidor remoto
        self.setup_remote_server()
        
        # Inicia servidor web local
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind(('', 80))
        self.socket.listen(5)
        print('Servidor web iniciado na porta 80')
        
        while True:
            try:
                client, addr = self.socket.accept()
                # Processa cada cliente em uma thread separada
                _thread.start_new_thread(self.handle_request, (client,))
            except Exception as e:
                print(f"Erro ao aceitar conexão: {e}")

    def handle_request(self, client):
        try:
            request = client.recv(1024).decode()
            
            # Verifica se está no modo AP ou Station
            status = self.wifi_manager.get_status()
            is_ap_mode = status['ap_active']
            
            if "GET /scan" in request:
                networks = self.wifi_manager.scan_networks()
                self.send_json_response(client, {"networks": networks})
                
            elif "POST /connect" in request:
                body = request.split('\r\n\r\n')[1]
                config = json.loads(body)
                success = self.wifi_manager.connect_wifi(config['ssid'], config['password'])
                
                # Carrega configuração salva para pegar o IP
                saved_config = self.wifi_manager.load_config()
                new_ip = saved_config.get('last_ip') if saved_config else None
                
                self.send_json_response(client, {
                    "status": "success" if success else "error",
                    "ip": new_ip,
                    "ssid": config['ssid']
                })
                    
            elif "GET /status" in request:
                self.send_json_response(client, self.wifi_manager.get_status())
                
            elif "GET /data" in request:
                data = self.can_handler.read_message()
                if data:
                    self.can_data.append(data)
                    if len(self.can_data) > 100:
                        self.can_data.pop(0)
                self.send_json_response(client, {
                    "current": data,
                    "history": self.can_data
                })
                
            else:
                if is_ap_mode:
                    self.send_ap_page(client)
                else:
                    self.send_monitor_page(client)
            
        except Exception as e:
            print(f"Erro ao processar requisição: {e}")
        finally:
            client.close()
    
    def send_json_response(self, client, data):
        response = json.dumps(data)
        client.send('HTTP/1.1 200 OK\n')
        client.send('Content-Type: application/json\n')
        client.send('Connection: close\n\n')
        client.send(response)
    
    def send_ap_page(self, client):
        """Página de configuração do WiFi (modo AP)"""
        html = """<!DOCTYPE html>
        <html>
        <head>
            <title>Configuração WiFi - John Deere Monitor</title>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <style>
                body { 
                    font-family: Arial; 
                    margin: 0;
                    padding: 20px;
                    background: #367C2B;
                    color: white;
                }
                .container {
                    max-width: 600px;
                    margin: 0 auto;
                    background: rgba(255,255,255,0.1);
                    padding: 20px;
                    border-radius: 10px;
                    box-shadow: 0 2px 5px rgba(0,0,0,0.2);
                }
                h1 { 
                    text-align: center;
                    color: #FFDE00;
                }
                .logo {
                    text-align: center;
                    margin-bottom: 20px;
                }
                .wifi-form {
                    max-width: 400px;
                    margin: 0 auto;
                }
                select, input {
                    width: 100%;
                    padding: 12px;
                    margin: 8px 0;
                    border: none;
                    border-radius: 5px;
                    background: white;
                    box-sizing: border-box;
                    font-size: 16px;
                }
                .btn {
                    background: #FFDE00;
                    color: #367C2B;
                    padding: 12px 20px;
                    border: none;
                    border-radius: 5px;
                    cursor: pointer;
                    width: 100%;
                    font-weight: bold;
                    font-size: 16px;
                    margin-top: 15px;
                }
                .btn:hover {
                    background: #FFE534;
                }
                #status {
                    padding: 15px;
                    margin: 15px 0;
                    border-radius: 5px;
                    display: none;
                    text-align: center;
                    line-height: 1.5;
                }
                .success { 
                    background: #4CAF50;
                    color: white;
                }
                .error { 
                    background: #f44336;
                    color: white;
                }
                .pending {
                    background: #FFC107;
                    color: #333;
                }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="logo">
                    <h1>John Deere Monitor</h1>
                    <p>Configuração de Rede WiFi</p>
                </div>
                
                <div class="wifi-form">
                    <select id="ssid">
                        <option value="">Buscando redes...</option>
                    </select>
                    <input type="password" id="password" placeholder="Senha da rede">
                    <button class="btn" onclick="connectWifi()">Conectar</button>
                    <div id="status"></div>
                </div>
            </div>

            <script>
                let statusElement;
                
                window.onload = function() {
                    statusElement = document.getElementById('status');
                    updateNetworks();
                    checkCurrentStatus();
                }

                function updateNetworks() {
                    fetch('/scan')
                        .then(response => response.json())
                        .then(data => {
                            const select = document.getElementById('ssid');
                            select.innerHTML = '';
                            data.networks.forEach(net => {
                                const option = document.createElement('option');
                                option.value = option.text = net;
                                select.add(option);
                            });
                        })
                        .catch(error => showStatus('Erro ao buscar redes', false));
                }

                function checkCurrentStatus() {
                    fetch('/status')
                        .then(response => response.json())
                        .then(status => {
                            if (status.sta_connected) {
                                showStatus(`Conectado à rede WiFi<br>IP Local: ${status.sta_ip}`, true);
                            }
                        });
                }

                function connectWifi() {
                    const ssid = document.getElementById('ssid').value;
                    const password = document.getElementById('password').value;
                    
                    if (!ssid || !password) {
                        showStatus('Preencha todos os campos', false);
                        return;
                    }

                    showStatus(`
                        Conectando à rede: ${ssid}<br>
                        Por favor, aguarde...
                    `, 'pending');
                    
                    fetch('/connect', {
                        method: 'POST',
                        body: JSON.stringify({ssid, password})
                    })
                    .then(response => response.json())
                    .then(data => {
                        if (data.status === 'success') {
                            showStatus(`
                                Conexão em andamento...<br>
                                Aguarde alguns segundos e acesse:<br>
                                http://${data.ip}
                            `, true);
                        } else {
                            showStatus('Falha na conexão. Verifique a senha e tente novamente.', false);
                        }
                    })
                    .catch(() => {
                        showStatus(`
                            Conexão em andamento...<br>
                            Se a senha estiver correta, em alguns segundos<br>
                            o dispositivo estará disponível na sua rede.
                        `, 'pending');
                    });
                }

                function showStatus(message, type) {
                    if (!statusElement) return;
                    
                    statusElement.innerHTML = message;
                    statusElement.className = '';
                    statusElement.style.display = 'block';
                    
                    if (type === true) {
                        statusElement.classList.add('success');
                    } else if (type === false) {
                        statusElement.classList.add('error');
                    } else if (type === 'pending') {
                        statusElement.classList.add('pending');
                    }
                }
            </script>
        </body>
        </html>
        """
        client.send('HTTP/1.1 200 OK\n')
        client.send('Content-Type: text/html; charset=utf-8\n')
        client.send('Connection: close\n\n')
        client.send(html)
    
    def send_monitor_page(self, client):
        """Página de monitoramento CAN (modo Station)"""
        html = """<!DOCTYPE html>
        <html>
        <head>
            <title>Monitor CAN Bus - John Deere</title>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <style>
                body { 
                    font-family: Arial; 
                    margin: 0;
                    padding: 20px;
                    background: #367C2B;
                    color: white;
                }
                .container {
                    max-width: 1200px;
                    margin: 0 auto;
                    background: rgba(255,255,255,0.1);
                    padding: 20px;
                    border-radius: 10px;
                    box-shadow: 0 2px 5px rgba(0,0,0,0.2);
                }
                .header {
                    text-align: center;
                    margin-bottom: 30px;
                    padding-bottom: 20px;
                    border-bottom: 1px solid rgba(255,255,255,0.2);
                }
                h1 { 
                    color: #FFDE00;
                    margin: 0;
                    font-size: 2.2em;
                }
                .status-bar {
                    background: rgba(255,255,255,0.15);
                    padding: 15px;
                    border-radius: 8px;
                    margin-bottom: 20px;
                    text-align: center;
                    font-size: 1.1em;
                }
                .data-grid {
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                    gap: 20px;
                    margin-bottom: 30px;
                }
                .data-card {
                    background: rgba(255,255,255,0.1);
                    padding: 20px;
                    border-radius: 8px;
                    border: 1px solid rgba(255,255,255,0.2);
                    transition: all 0.3s ease;
                }
                .data-card:hover {
                    transform: translateY(-5px);
                    background: rgba(255,255,255,0.15);
                }
                .data-card h3 {
                    color: #FFDE00;
                    margin: 0 0 15px 0;
                    font-size: 1.3em;
                }
                .value { 
                    font-size: 28px;
                    color: white;
                    font-weight: bold;
                    text-align: center;
                    font-family: monospace;
                }
                .data-history {
                    background: rgba(0,0,0,0.2);
                    padding: 20px;
                    border-radius: 8px;
                    margin-top: 20px;
                    height: 300px;
                    overflow-y: auto;
                }
                .data-history h2 {
                    color: #FFDE00;
                    margin: 0 0 15px 0;
                }
                .history-item {
                    background: rgba(255,255,255,0.1);
                    padding: 10px;
                    margin: 5px 0;
                    border-radius: 5px;
                    font-family: monospace;
                }
                .history-item:hover {
                    background: rgba(255,255,255,0.15);
                }
                .connected { color: #4CAF50; }
                .disconnected { color: #f44336; }
                
                ::-webkit-scrollbar {
                    width: 10px;
                }
                ::-webkit-scrollbar-track {
                    background: rgba(255,255,255,0.1);
                    border-radius: 5px;
                }
                ::-webkit-scrollbar-thumb {
                    background: #FFDE00;
                    border-radius: 5px;
                }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Monitor CAN Bus John Deere</h1>
                    <p>Sistema de Monitoramento de Implementos Agrícolas</p>
                </div>
                
                <div class="status-bar" id="status-bar">
                    Verificando conexão...
                </div>
                
                <div class="data-grid" id="data-grid">
                    <!-- Dados dinâmicos serão inseridos aqui -->
                </div>
                
                <div class="data-history">
                    <h2>Histórico de Mensagens</h2>
                    <div id="data-history">
                        <!-- Histórico será inserido aqui -->
                    </div>
                </div>
            </div>

            <script>
                function updateStatus() {
                    fetch('/status')
                        .then(response => response.json())
                        .then(status => {
                            const statusBar = document.getElementById('status-bar');
                            const isConnected = status.sta_connected;
                            statusBar.innerHTML = `
                                Status da Conexão: 
                                <span class="${isConnected ? 'connected' : 'disconnected'}">
                                    ${isConnected ? 'Conectado' : 'Desconectado'}
                                </span> |
                                IP: ${status.sta_ip || 'N/A'}
                            `;
                        });
                }
                
                function updateData() {
                    fetch('/data')
                        .then(response => response.json())
                        .then(data => {
                            if (data.current) {
                                updateDataGrid(data.current);
                                updateHistory(data.history);
                            }
                        });
                }
                
                function updateDataGrid(data) {
                    const grid = document.getElementById('data-grid');
                    grid.innerHTML = `
                        <div class="data-card">
                            <h3>PGN (Parameter Group Number)</h3>
                            <div class="value">${data.pgn}</div>
                        </div>
                        <div class="data-card">
                            <h3>Dados Recebidos</h3>
                            <div class="value">${data.data.map(x => x.toString(16).padStart(2, '0')).join(' ')}</div>
                        </div>
                        <div class="data-card">
                            <h3>Origem</h3>
                            <div class="value">${data.source}</div>
                        </div>
                        <div class="data-card">
                            <h3>Prioridade</h3>
                            <div class="value">${data.priority}</div>
                        </div>
                    `;
                }
                
                function updateHistory(history) {
                    const historyDiv = document.getElementById('data-history');
                    historyDiv.innerHTML = history.map(msg => `
                        <div class="history-item">
                            [${new Date(msg.timestamp).toLocaleTimeString('pt-BR')}] 
                            PGN: ${msg.pgn} | 
                            Origem: ${msg.source} | 
                            Dados: ${msg.data.map(x => x.toString(16).padStart(2, '0')).join(' ')}
                        </div>
                    `).join('');
                    historyDiv.scrollTop = historyDiv.scrollHeight;
                }
                
                // Atualiza status a cada 5 segundos
                setInterval(updateStatus, 5000);
                // Atualiza dados CAN a cada 1 segundo
                setInterval(updateData, 1000);
                
                // Primeira atualização
                updateStatus();
                updateData();
            </script>
        </body>
        </html>
        """
        client.send('HTTP/1.1 200 OK\n')
        client.send('Content-Type: text/html; charset=utf-8\n')
        client.send('Connection: close\n\n')
        client.send(html) 