import streamlit as st
import requests
import time
import json
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
from j1939_decoder import J1939Decoder

# Atualiza porta para comunicação remota
ESP32_PORT = 8502

def connect_to_esp32():
    st.sidebar.title("Configuração ESP32")
    
    if 'esp32_ip' not in st.session_state:
        st.session_state.esp32_ip = ""
    
    esp32_ip = st.sidebar.text_input(
        "IP do ESP32",
        value=st.session_state.esp32_ip,
        help="Digite o IP público ou DNS do ESP32"
    )
    
    if st.sidebar.button("Testar Conexão"):
        try:
            # Usa porta 8502 para comunicação remota
            url = f"http://{esp32_ip}:{ESP32_PORT}/data"
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                st.sidebar.success("Conexão estabelecida!")
                st.session_state.esp32_ip = esp32_ip
                return True
        except Exception as e:
            st.sidebar.error(f"Falha na conexão: {str(e)}")
            return False
    
    return esp32_ip != ""

def fetch_can_data():
    if not st.session_state.esp32_ip:
        return None
        
    try:
        # Usa porta 8502 para dados
        url = f"http://{st.session_state.esp32_ip}:{ESP32_PORT}/data"
        response = requests.get(url, timeout=2)
        return response.json() if response.status_code == 200 else None
    except Exception as e:
        st.warning(f"Erro ao obter dados: {str(e)}")
        return None

def main():
    st.title("Monitor CAN Bus John Deere")
    
    if not connect_to_esp32():
        st.warning("Configure o IP do ESP32 no menu lateral")
        return
        
    # Atualização em tempo real
    placeholder = st.empty()
    while True:
        try:
            # Usando a porta específica
            response = requests.get(f"http://{st.session_state.esp32_ip}:{ESP32_PORT}/data")
            data = response.json()
            
            with placeholder.container():
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("RPM Motor", f"{data['engine_rpm']:.0f}")
                with col2:
                    st.metric("Velocidade", f"{data['speed']:.1f} km/h")
                with col3:
                    st.metric("Consumo", f"{data['fuel_rate']:.1f} L/h")
                
                # Adicionar mais métricas...
                
        except Exception as e:
            st.error(f"Erro na comunicação: {str(e)}")
            time.sleep(5)
            
        time.sleep(1)

if __name__ == "__main__":
    main() 