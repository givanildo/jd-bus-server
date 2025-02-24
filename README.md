# JD Bus Server

Monitor CAN Bus para Implementos Agrícolas John Deere

## Descrição

Este projeto implementa um sistema de monitoramento remoto para implementos agrícolas John Deere, utilizando ESP32 para leitura do barramento CAN e uma interface web para visualização dos dados.

## Características

- Leitura de dados CAN via ESP32 + MCP2515
- Interface web responsiva
- Comunicação remota via porta 8502
- Suporte ao protocolo J1939
- Visualização em tempo real
- Gráficos e indicadores

## Configuração

1. ESP32:
   - Carregar os arquivos da pasta `esp32/` para o ESP32
   - Conectar MCP2515 ao ESP32
   - Configurar WiFi via interface web

2. Servidor Web:
   - Instalar dependências: `pip install -r web_app/requirements.txt`
   - Executar: `streamlit run web_app/app.py`

3. Configuração de Rede:
   - Abrir porta 8502 no firewall
   - Configurar port forwarding no roteador
   - Configurar security group no servidor Oracle

## Uso

1. Conecte o ESP32 ao implemento
2. Acesse a interface web local (porta 80) para configuração inicial
3. Use a aplicação Streamlit para monitoramento remoto (porta 8502)

## Autor

Givanildo Brunetta
- Email: givanildobrunetta@gmail.com
- GitHub: [@givanildo](https://github.com/givanildo) 