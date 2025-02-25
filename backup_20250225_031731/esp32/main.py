from wifi_manager import WifiManager
from can_handler import CANHandler
from web_server import WebServer
from logger import Logger

def main():
    try:
        logger = Logger()
        logger.info('main', 'Iniciando sistema...')
        
        # Inicializa WiFi
        wifi = WifiManager()
        
        # Inicializa CAN com retry
        can = CANHandler()
        if not can.init_can():
            logger.error('main', 'Falha ao inicializar CAN')
            return
            
        # Inicializa servidor
        server = WebServer(wifi, can)
        
        # Registra handlers de cleanup
        def cleanup():
            server.cleanup()
            wifi.cleanup()
            
        # Inicia servidor
        server.start()
        
    except Exception as e:
        logger.error('main', f'Erro fatal: {e}')
    finally:
        cleanup()

if __name__ == '__main__':
    main() 