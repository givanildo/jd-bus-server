# Monitor CAN Bus John Deere

Sistema de monitoramento CAN bus para implementos agrícolas John Deere usando ESP32 e interface web Streamlit.

## 🚜 Características

- Leitura de dados CAN J1939
- Interface web responsiva com tema John Deere
- Visualização em tempo real
- Gráficos e gauges interativos
- Decodificação de PGNs específicos John Deere
- Configuração WiFi automática via AP

## 📊 Parâmetros Monitorados

### Motor (PGN: 0xFEF1)
- RPM (0-8000 RPM)
- Torque (0-100%)
- Consumo de combustível (0-150 L/h)

### Implemento (PGN: 0xF004)
- Velocidade (0-50 km/h)
- Área total (0-1000 ha)
- Profundidade (0-100 cm)

### Fluidos (PGN: 0xFEE8)
- Nível de combustível (0-100%)
- Temperatura do motor (-40 a 150°C)
- Pressão do óleo (0-1000 kPa)

## 🛠️ Requisitos de Hardware

- ESP32
- Módulo MCP2515 CAN Bus
- Conexões:
  - ESP32 -> MCP2515
    - GPIO5  -> CS
    - GPIO18 -> SCK
    - GPIO19 -> MISO
    - GPIO23 -> MOSI
    - 3.3V   -> VCC
    - GND    -> GND

## 📦 Instalação

1. Clone o repositório:
```bash
git clone https://github.com/givanildo/jd-bus.git
cd jd-bus
```

2. Instale as dependências e execute:
```bash
python tools/run_webapp.py
```

## 🔧 Configuração do ESP32

1. Conecte o ESP32 via USB
2. Execute o upload do código:
```bash
python tools/upload_files.py
```

3. O ESP32 iniciará em modo AP:
   - SSID: JohnDeere-AP
   - Senha: 12345678

4. Conecte-se ao AP e configure sua rede WiFi

## 📱 Interface Web

1. Conecte-se à mesma rede do ESP32
2. Execute a aplicação web
3. Digite o IP do ESP32
4. Monitore em tempo real:
   - Gauges com valores atuais
   - Gráficos históricos
   - Status da conexão
   - Dados brutos

## 🗂️ Estrutura do Projeto

```
jd-bus/
├── esp32/
│   ├── can_handler.py     # Controlador CAN
│   ├── wifi_manager.py    # Gerenciador WiFi
│   ├── web_server.py      # Servidor Web
│   └── main.py           # Programa principal
├── web_app/
│   ├── app.py            # Interface Streamlit
│   ├── j1939_decoder.py  # Decodificador J1939
│   └── requirements.txt  # Dependências
├── tools/
│   ├── publish.py        # Publicação GitHub
│   ├── run_webapp.py     # Execução Web
│   └── upload_files.py   # Upload ESP32
└── README.md
```

## 👤 Autor

**Givanildo Brunetta**
- Email: givanildobrunetta@gmail.com
- GitHub: [@givanildo](https://github.com/givanildo)

## 📄 Licença

Este projeto está sob a licença MIT. 




# JD Bus Server

Monitor de Implementos Agrícolas John Deere usando protocolo ISO BUS/J1939

## ⚠️ IMPORTANTE: Firmware ESP32

### 1. Firmware MicroPython
Baixe a última versão do firmware MicroPython para ESP32:
- 📥 [MicroPython para ESP32 GENERIC](https://micropython.org/download/ESP32_GENERIC/)
- Versão recomendada: v1.24.1 ou superior
- Arquivo: `ESP32_GENERIC-20241129-v1.24.1.bin`

### 2. Firmware Monitor
Para o funcionamento correto do sistema, você precisa do firmware do Monitor. 
Por questões de segurança, ele não está no GitHub.

**Antes de usar:*
1. Faça o download do   genericfile microphyton para esp32.
2. Coloque os arquivos em: `esp32/firmware/`
3. Execute: `python tools/upload_files.py`

Sem o firmware na pasta correta, o script de upload não funcionará!

## Estrutura 