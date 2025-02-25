# Configuração de Hardware

## ESP32
- Módulo: ESP32-WROOM-32
- Flash: 4MB
- RAM: 520KB

## MCP2515
- Interface: SPI
- Clock: 8MHz
- Velocidade CAN: 250kbps

## Conexões
| ESP32 | MCP2515 |
|-------|---------|
| GPIO5 | CS      |
| GPIO18| SCK     |
| GPIO19| MISO    |
| GPIO23| MOSI    |
| GPIO4 | INT     | 