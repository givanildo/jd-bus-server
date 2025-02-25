# Documentação ESP32

## Componentes Principais

### web_server.py
- Gerencia conexões web
- Porta 80: Portal de configuração (modo AP)
- Porta 8502: Servidor de dados
- Gerencia transição AP -> Cliente

### main.py
- Ponto de entrada do sistema
- Inicializa componentes
- Gerencia ciclo de vida

### j1939_decoder.py
Decodifica mensagens CAN com protocolo J1939:

| PGN    | Descrição          | Unidade |
|--------|-------------------|---------|
| 0xF004 | RPM do Motor      | RPM     |
| 0xFEEE | Temperatura Motor | °C      |
| 0xFEF1 | Velocidade       | km/h    |
| 0xFEF2 | Nível Combustível| %       |
| 0xF003 | Carga do Motor   | %       | 