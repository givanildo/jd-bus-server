import network
import json
import os
import _thread
import time
from logger import Logger

class WifiManager:
    def __init__(self):
        self.logger = Logger()
        self.sta_if = network.WLAN(network.STA_IF)
        self.ap_if = network.WLAN(network.AP_IF)
        self.config_file = 'wifi_config.json'
        self._monitor_thread = None
        self._running = True
        
    def start_ap(self):
        """Inicia modo AP"""
        try:
            self.ap_if.active(True)
            self.ap_if.config(
                essid='JohnDeere_Monitor',
                authmode=network.AUTH_OPEN
            )
            self.logger.info('wifi', f'AP iniciado - IP: {self.ap_if.ifconfig()[0]}')
        except Exception as e:
            self.logger.error('wifi', f'Erro ao iniciar AP: {e}')
            
    def stop_ap(self):
        """Para modo AP"""
        self.ap_if.active(False)
        
    def scan_networks(self):
        """Busca redes disponíveis"""
        try:
            self.sta_if.active(True)
            networks = self.sta_if.scan()
            return [{'ssid': net[0].decode(), 'rssi': net[3]} for net in networks]
        except Exception as e:
            self.logger.error('wifi', f'Erro ao buscar redes: {e}')
            return []
            
    def connect(self, ssid, password):
        """Conecta em rede WiFi"""
        try:
            self.sta_if.active(True)
            self.sta_if.connect(ssid, password)
            
            # Aguarda conexão
            for _ in range(20):  # 10 segundos timeout
                if self.sta_if.isconnected():
                    ip = self.sta_if.ifconfig()[0]
                    self.logger.info('wifi', f'Conectado à rede {ssid}')
                    self.logger.info('wifi', f'IP na rede local: {ip}')
                    
                    # Salva configuração
                    config = {'ssid': ssid, 'password': password}
                    with open(self.config_file, 'w') as f:
                        json.dump(config, f)
                        
                    return True
                time.sleep(0.5)
            
            self.logger.error('wifi', f'Timeout ao conectar em {ssid}')
            return False
            
        except Exception as e:
            self.logger.error('wifi', f'Erro ao conectar: {e}')
            return False
            
    def connect_saved(self):
        """Conecta usando configuração salva"""
        try:
            if self.config_file in os.listdir():
                with open(self.config_file) as f:
                    config = json.load(f)
                return self.connect(config['ssid'], config['password'])
        except:
            return False
            
    def get_status(self):
        """Retorna status das conexões"""
        return {
            'ap_active': self.ap_if.active(),
            'sta_active': self.sta_if.active(),
            'sta_connected': self.sta_if.isconnected(),
            'sta_ip': self.sta_if.ifconfig()[0] if self.sta_if.active() else None
        }

    def monitor_connection(self):
        """Monitora conexão WiFi e tenta reconectar se necessário"""
        while self._running:
            if not self.sta_if.isconnected():
                self.logger.warning('wifi', 'Conexão perdida, tentando reconectar...')
                self.reconnect()
            time.sleep(5)
            
    def reconnect(self):
        """Tenta reconectar usando última configuração"""
        try:
            config = self.load_config()
            if config:
                self.connect(config['ssid'], config['password'])
        except:
            self.logger.error('wifi', 'Falha ao reconectar')
            
    def start_monitoring(self):
        """Inicia thread de monitoramento"""
        if not self._monitor_thread:
            self._monitor_thread = _thread.start_new_thread(self.monitor_connection, ())
            
    def cleanup(self):
        """Limpa recursos"""
        self._running = False
        if self.sta_if.active():
            self.sta_if.disconnect()
        if self.ap_if.active():
            self.ap_if.active(False) 