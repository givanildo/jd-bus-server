import network
import json
import os

class WifiManager:
    def __init__(self):
        self.sta_if = network.WLAN(network.STA_IF)
        self.ap_if = network.WLAN(network.AP_IF)
        self.config_file = 'wifi_config.json'
        
    def start_ap(self):
        """Inicia modo AP com nome específico"""
        self.ap_if.active(True)
        self.ap_if.config(essid='JD-Monitor', password='12345678')
        
    def scan_networks(self):
        """Busca redes WiFi disponíveis"""
        self.sta_if.active(True)
        networks = self.sta_if.scan()
        return [net[0].decode('utf-8') for net in networks]
        
    def connect_wifi(self, ssid, password):
        """Conecta a uma rede WiFi"""
        self.sta_if.active(True)
        self.sta_if.connect(ssid, password)
        
        # Salva configuração
        config = {'ssid': ssid, 'password': password}
        with open(self.config_file, 'w') as f:
            json.dump(config, f)
            
        return self.sta_if.isconnected()
        
    def get_status(self):
        """Retorna status atual das conexões"""
        return {
            'sta_active': self.sta_if.active(),
            'sta_connected': self.sta_if.isconnected(),
            'sta_ip': self.sta_if.ifconfig()[0] if self.sta_if.isconnected() else None,
            'ap_active': self.ap_if.active()
        } 