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

**Antes de usar:**
1. Solicite o firmware pelo email: givanildobrunetta@gmail.com
2. Coloque os arquivos em: `esp32/firmware/`
3. Execute: `python tools/upload_files.py`

Sem o firmware na pasta correta, o script de upload não funcionará!

## Estrutura 