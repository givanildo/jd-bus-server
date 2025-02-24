from machine import Pin, SPI
from web_server import WebServer
from wifi_manager import WifiManager
from can_handler import CanHandler

def main():
    # Configuração do CAN Bus
    spi = SPI(1, baudrate=10000000, polarity=0, phase=0)
    cs = Pin(5, Pin.OUT)
    can_handler = CanHandler(spi, cs)
    
    # Configuração do WiFi
    wifi_manager = WifiManager()
    
    # Configuração do Servidor Web
    web_server = WebServer(wifi_manager, can_handler)
    web_server.start()

if __name__ == "__main__":
    main() 