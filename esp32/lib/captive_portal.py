class CaptivePortal:
    def __init__(self):
        pass
            
    def get_config_page(self):
        """Retorna página de configuração"""
        return """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>JohnDeere Monitor</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body {
            font-family: Arial;
            margin: 20px;
            background: #f0f0f0;
        }
        .container {
            max-width: 500px;
            margin: 0 auto;
            background: white;
            padding: 20px;
            border-radius: 8px;
            border: 2px solid #367C2B;
        }
        .header {
            background: #367C2B;
            color: white;
            padding: 20px;
            margin: -20px -20px 20px -20px;
            border-radius: 6px 6px 0 0;
            text-align: center;
            border-bottom: 4px solid #FDB515;
        }
        h1 { margin: 0; }
        select {
            width: 100%;
            padding: 10px;
            margin: 10px 0;
            border: 1px solid #ddd;
            border-radius: 4px;
        }
        input {
            width: 100%;
            padding: 10px;
            margin: 10px 0;
            border: 1px solid #ddd;
            border-radius: 4px;
            box-sizing: border-box;
        }
        button {
            width: 100%;
            padding: 12px;
            background: #367C2B;
            color: white;
            border: none;
            border-radius: 4px;
            font-size: 16px;
            cursor: pointer;
            margin-top: 10px;
        }
        button:hover {
            background: #2B6022;
        }
        #status {
            margin-top: 20px;
            text-align: center;
            color: #666;
        }
        .password-container {
            position: relative;
            width: 100%;
        }
        
        .password-toggle {
            position: absolute;
            right: 10px;
            top: 50%;
            transform: translateY(-50%);
            cursor: pointer;
            color: #666;
            user-select: none;
        }
        
        #status-modal {
            display: none;
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.2);
            z-index: 1000;
            text-align: center;
        }
        
        #modal-backdrop {
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(0,0,0,0.5);
            z-index: 999;
        }
        
        .spinner {
            display: inline-block;
            width: 30px;
            height: 30px;
            border: 3px solid #f3f3f3;
            border-top: 3px solid #367C2B;
            border-radius: 50%;
            animation: spin 1s linear infinite;
            margin-bottom: 10px;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>JohnDeere Monitor</h1>
        </div>
        
        <h2>Configuração WiFi</h2>
        
        <select id="network-select" onchange="networkSelected()">
            <option value="">Selecione uma rede...</option>
        </select>
        
        <div class="password-container">
            <input type="password" id="password" placeholder="Senha da rede">
            <span class="password-toggle" onclick="togglePassword()">👁️</span>
        </div>
        
        <button onclick="connectWifi()">Conectar</button>
        <div id="status"></div>
    </div>
    
    <div id="modal-backdrop"></div>
    <div id="status-modal">
        <div class="spinner"></div>
        <p id="modal-message">Conectando...</p>
        <p id="modal-ip" style="display:none">
            IP na rede local: <strong id="device-ip"></strong>
            <br><br>
            Acesse: <strong>http://<span id="device-ip-link"></span></strong>
        </p>
    </div>

    <script>
        // Busca redes disponíveis
        async function loadNetworks() {
            try {
                const response = await fetch('/scan');
                const data = await response.json();
                const select = document.getElementById('network-select');
                
                // Limpa opções anteriores
                select.innerHTML = '<option value="">Selecione uma rede...</option>';
                
                // Adiciona redes encontradas
                data.networks.forEach(network => {
                    const option = document.createElement('option');
                    option.value = network.ssid;
                    option.text = network.ssid;
                    select.appendChild(option);
                });
            } catch (error) {
                document.getElementById('status').textContent = 'Erro ao buscar redes';
            }
        }

        function networkSelected() {
            const select = document.getElementById('network-select');
            if (select.value) {
                document.getElementById('password').style.display = 'block';
                document.getElementById('status').textContent = 'Digite a senha da rede';
            } else {
                document.getElementById('password').style.display = 'none';
                document.getElementById('status').textContent = '';
            }
        }

        function togglePassword() {
            const pwd = document.getElementById('password');
            pwd.type = pwd.type === 'password' ? 'text' : 'password';
        }

        async function connectWifi() {
            const ssid = document.getElementById('network-select').value;
            const password = document.getElementById('password').value;
            const modal = document.getElementById('status-modal');
            const backdrop = document.getElementById('modal-backdrop');
            const message = document.getElementById('modal-message');
            const ipInfo = document.getElementById('modal-ip');
            
            if (!ssid) {
                status.textContent = 'Selecione uma rede';
                return;
            }
            
            // Mostra modal
            modal.style.display = 'block';
            backdrop.style.display = 'block';
            message.textContent = `Conectando à rede "${ssid}"...`;
            ipInfo.style.display = 'none';
            
            try {
                const response = await fetch('/connect', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ssid, password})
                });
                
                const data = await response.json();
                
                if (data.status === 'success') {
                    message.textContent = 'Conectado com sucesso!';
                    document.getElementById('device-ip').textContent = data.ip;
                    document.getElementById('device-ip-link').textContent = data.ip;
                    ipInfo.style.display = 'block';
                    
                    // Aguarda 10 segundos antes de redirecionar
                    setTimeout(() => {
                        window.location.href = `http://${data.ip}`;
                    }, 10000);
                } else {
                    message.textContent = 'Erro ao conectar. Verifique a senha.';
                    setTimeout(() => {
                        modal.style.display = 'none';
                        backdrop.style.display = 'none';
                    }, 3000);
                }
            } catch (error) {
                message.textContent = 'Erro ao conectar. Tente novamente.';
                setTimeout(() => {
                    modal.style.display = 'none';
                    backdrop.style.display = 'none';
                }, 3000);
            }
        }

        // Carrega redes ao iniciar
        loadNetworks();
        
        // Atualiza lista a cada 30 segundos
        setInterval(loadNetworks, 30000);
        
        // Esconde campo de senha inicialmente
        document.getElementById('password').style.display = 'none';
    </script>
</body>
</html>
""" 