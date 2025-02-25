# Baixar de: https://github.com/jxltom/micropython-mcp2515 

from machine import Pin, SPI

class MCP2515:
    # Registradores MCP2515
    MCP_CANSTAT = 0x0E
    MCP_CANCTRL = 0x0F
    MCP_CNF3 = 0x28
    MCP_CNF2 = 0x29
    MCP_CNF1 = 0x2A
    MCP_RXB0CTRL = 0x60
    MCP_RXB1CTRL = 0x70
    MCP_TXB0CTRL = 0x30
    MCP_TXB1CTRL = 0x40
    MCP_TXB2CTRL = 0x50
    
    # Comandos SPI
    RESET = 0xC0
    READ = 0x03
    WRITE = 0x02
    BIT_MODIFY = 0x05
    READ_RX = 0x90
    LOAD_TX = 0x40
    RTS = 0x80
    
    # Modos de operação
    MODE_NORMAL = 0x00
    MODE_SLEEP = 0x20
    MODE_LOOPBACK = 0x40
    MODE_LISTEN = 0x60
    MODE_CONFIG = 0x80
    
    class CANMessage:
        def __init__(self, id=0, data=None, dlc=0):
            self.id = id
            self.data = data if data else bytearray(8)
            self.dlc = dlc
    
    def __init__(self, spi, cs):
        self.spi = spi
        self.cs = cs
        self.cs.value(1)
        
    def reset(self):
        """Reset do controlador"""
        self.cs.value(0)
        self.spi.write(bytes([self.RESET]))
        self.cs.value(1)
        
    def read_register(self, addr):
        """Lê um registrador"""
        self.cs.value(0)
        self.spi.write(bytes([self.READ, addr]))
        value = self.spi.read(1)[0]
        self.cs.value(1)
        return value
        
    def write_register(self, addr, value):
        """Escreve em um registrador"""
        self.cs.value(0)
        self.spi.write(bytes([self.WRITE, addr, value]))
        self.cs.value(1)
        
    def modify_register(self, addr, mask, data):
        """Modifica bits específicos de um registrador"""
        self.cs.value(0)
        self.spi.write(bytes([self.BIT_MODIFY, addr, mask, data]))
        self.cs.value(1)
        
    def set_mode(self, mode):
        """Define modo de operação"""
        self.modify_register(self.MCP_CANCTRL, 0xE0, mode)
        
    def set_config_mode(self):
        """Entra em modo de configuração"""
        self.set_mode(self.MODE_CONFIG)
        
    def set_normal_mode(self):
        """Entra em modo normal"""
        self.set_mode(self.MODE_NORMAL)
        
    def set_bitrate(self, bitrate):
        """Configura taxa de bits"""
        self.set_config_mode()
        
        if bitrate == 250000:  # 250kbps para cristal de 8MHz
            self.write_register(self.MCP_CNF1, 0x00)
            self.write_register(self.MCP_CNF2, 0x90)
            self.write_register(self.MCP_CNF3, 0x02)
            
    def recv(self):
        """Recebe mensagem CAN"""
        # Lê buffer RX0
        self.cs.value(0)
        self.spi.write(bytes([self.READ_RX]))
        
        # Lê ID, DLC e dados
        data = self.spi.read(13)
        self.cs.value(1)
        
        if data:
            msg = self.CANMessage()
            msg.id = (data[0] << 3) | (data[1] >> 5)
            msg.dlc = data[4] & 0x0F
            msg.data = data[5:5+msg.dlc]
            return msg
            
        return None
        
    def send(self, msg):
        """Envia mensagem CAN"""
        # Carrega buffer TX0
        self.cs.value(0)
        self.spi.write(bytes([self.LOAD_TX]))
        
        # ID
        self.spi.write(bytes([msg.id >> 3, (msg.id & 0x07) << 5]))
        
        # DLC e dados
        self.spi.write(bytes([0, 0, msg.dlc]))
        self.spi.write(msg.data)
        self.cs.value(1)
        
        # Solicita envio
        self.cs.value(0)
        self.spi.write(bytes([self.RTS | 0x01]))  # TX0
        self.cs.value(1) 