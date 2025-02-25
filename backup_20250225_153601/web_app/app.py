import streamlit as st
import requests
import json
import time
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

# Paleta de cores John Deere
JOHN_DEERE_GREEN = "#367C2B"
JOHN_DEERE_YELLOW = "#FDB515"
JOHN_DEERE_DARK_GREEN = "#1E4B19"
JOHN_DEERE_LIGHT_GREEN = "#89B983"
JOHN_DEERE_DARK_YELLOW = "#D49212"
JOHN_DEERE_LIGHT_YELLOW = "#FFD47F"
BACKGROUND_COLOR = "#E8F0E7"  # Verde muito claro para fundo
CARD_BACKGROUND = "#F5F9F5"   # Verde mais claro ainda para cards

class JDMonitor:
    # Configurações
    ESP32_WEB_PORT = 8080
    ESP32_DATA_PORT = 8502
    
    def __init__(self):
        # Configuração da página
        st.set_page_config(
            page_title="John Deere Monitor",
            page_icon="🚜",
            layout="wide",
            initial_sidebar_state="expanded"
        )
        
        # Aplica tema John Deere
        self.apply_theme()
        
        # Estado da aplicação
        if 'connected' not in st.session_state:
            st.session_state.connected = False
        if 'esp32_ip' not in st.session_state:
            st.session_state.esp32_ip = "192.168.4.1"
        if 'data_buffer' not in st.session_state:
            st.session_state.data_buffer = []
            
    def apply_theme(self):
        """Aplica tema John Deere"""
        st.markdown(f"""
            <style>
                .stApp {{
                    background: linear-gradient(135deg, {BACKGROUND_COLOR} 0%, #F8F8F8 100%);
                }}
                
                .main {{
                    background: {BACKGROUND_COLOR};
                }}
                
                .css-1d391kg {{
                    background-color: {CARD_BACKGROUND};
                    border-radius: 10px;
                    padding: 20px;
                    box-shadow: 0 2px 4px rgba(54, 124, 43, 0.1);
                    border-left: 4px solid {JOHN_DEERE_GREEN};
                }}
                
                .st-emotion-cache-1wrcr25 {{
                    background: linear-gradient(90deg, {JOHN_DEERE_GREEN} 0%, {JOHN_DEERE_DARK_GREEN} 100%);
                }}
                
                .stButton>button {{
                    background: linear-gradient(90deg, {JOHN_DEERE_GREEN} 0%, {JOHN_DEERE_DARK_GREEN} 100%);
                    color: white;
                    border: none;
                    border-radius: 5px;
                    padding: 10px 20px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                }}
                
                .stButton>button:hover {{
                    background: linear-gradient(90deg, {JOHN_DEERE_DARK_GREEN} 0%, {JOHN_DEERE_GREEN} 100%);
                    box-shadow: 0 4px 8px rgba(0,0,0,0.2);
                }}
                
                h1, h2, h3 {{
                    color: {JOHN_DEERE_DARK_GREEN};
                    text-shadow: 1px 1px 2px rgba(0,0,0,0.1);
                }}
                
                .status-card {{
                    background: {CARD_BACKGROUND};
                    padding: 20px;
                    border-radius: 10px;
                    box-shadow: 0 2px 4px rgba(54, 124, 43, 0.1);
                    margin: 10px 0;
                    border-left: 4px solid {JOHN_DEERE_GREEN};
                }}
                
                .metric-card {{
                    text-align: center;
                    padding: 15px;
                    background: linear-gradient(135deg, {CARD_BACKGROUND} 0%, white 100%);
                    border-radius: 8px;
                    box-shadow: 0 2px 4px rgba(54, 124, 43, 0.1);
                    border: 1px solid {JOHN_DEERE_LIGHT_GREEN};
                }}
                
                .metric-value {{
                    font-size: 24px;
                    font-weight: bold;
                    color: {JOHN_DEERE_GREEN};
                    text-shadow: 1px 1px 2px rgba(0,0,0,0.05);
                }}
                
                .metric-label {{
                    color: {JOHN_DEERE_DARK_GREEN};
                    font-size: 14px;
                }}
                
                /* Estilo para os expanders */
                .streamlit-expanderHeader {{
                    background: linear-gradient(90deg, {JOHN_DEERE_GREEN} 0%, {JOHN_DEERE_DARK_GREEN} 100%);
                    color: white !important;
                    border-radius: 5px;
                }}
                
                /* Estilo para os selects */
                .stSelectbox {{
                    border-color: {JOHN_DEERE_GREEN};
                }}
                
                /* Estilo para sliders */
                .stSlider {{
                    accent-color: {JOHN_DEERE_GREEN};
                }}
            </style>
        """, unsafe_allow_html=True)
            
    def render_sidebar(self):
        """Renderiza barra lateral"""
        with st.sidebar:
            st.image(
                "https://www.deere.com/assets/images/region-4/products/tractors/large/r4d066744_8rx_1366.jpg", 
                use_container_width=True
            )
            
            st.title("🚜 Configurações")
            
            # IP do ESP32
            esp32_ip = st.text_input(
                "IP do ESP32",
                value=st.session_state.esp32_ip,
                help="Digite o IP do seu ESP32"
            )
            
            # Botão de conexão
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Testar Conexão", use_container_width=True):
                    self.test_connection(esp32_ip)
            with col2:
                if st.session_state.connected:
                    st.success("✅ Conectado")
                else:
                    st.error("❌ Desconectado")
                    
            st.divider()
            
            # Filtros
            st.subheader("📊 Filtros")
            self.pgn_filter = st.multiselect(
                "PGNs",
                options=self.get_available_pgns(),
                default=None,
                help="Selecione os PGNs para filtrar"
            )
            
            # Taxa de atualização
            st.subheader("⚙️ Configurações")
            self.update_rate = st.slider(
                "Taxa de Atualização (s)",
                min_value=1,
                max_value=10,
                value=1
            )
            
    def test_connection(self, ip):
        """Testa conexão com ESP32"""
        try:
            # Tenta conectar apenas na porta de dados (8502)
            url = f"http://{ip}:{self.ESP32_DATA_PORT}/data"
            print(f"Tentando conectar em: {url}")  # Debug
            
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                st.session_state.connected = True
                st.session_state.esp32_ip = ip
                st.success(f"✅ Conectado ao ESP32 em {ip}:{self.ESP32_DATA_PORT}")
                return True
            
            st.error(f"❌ Erro: Servidor respondeu {response.status_code}")
            st.session_state.connected = False
            return False
        
        except requests.exceptions.ConnectionError:
            st.error(f"❌ Erro: Não foi possível conectar ao ESP32 em {ip}:{self.ESP32_DATA_PORT}")
            st.session_state.connected = False
            return False
        except Exception as e:
            st.error(f"❌ Erro: {str(e)}")
            st.session_state.connected = False
            return False
            
    def get_available_pgns(self):
        """Retorna PGNs disponíveis"""
        pgns = set()
        for data in st.session_state.data_buffer:
            if 'pgn' in data:
                pgns.add(hex(data['pgn']))
        return list(pgns)
            
    def update_data(self):
        """Atualiza dados do ESP32"""
        if not st.session_state.connected:
            return False
        
        try:
            url = f"http://{st.session_state.esp32_ip}:{self.ESP32_DATA_PORT}/data"
            response = requests.get(url, timeout=2)
            
            if response.status_code == 200:
                data = response.json()
                # Adiciona timestamp local
                data['local_time'] = datetime.now().strftime('%H:%M:%S')
                st.session_state.data_buffer.append(data)
                
                # Mantém buffer com tamanho máximo
                if len(st.session_state.data_buffer) > 1000:
                    st.session_state.data_buffer.pop(0)
                return True
            
            else:
                print(f"Erro ao obter dados: Status {response.status_code}")  # Debug
                return False
        
        except requests.exceptions.ConnectionError:
            print(f"Erro de conexão com ESP32")  # Debug
            st.session_state.connected = False  # Marca como desconectado
            return False
        except Exception as e:
            print(f"Erro ao atualizar dados: {e}")  # Debug
            return False
        
    def render_metrics(self, data):
        """Renderiza métricas principais"""
        try:
            # Verifica se temos dados válidos
            if not data or not isinstance(data, dict):
                st.warning("Aguardando dados do ESP32...")
                return
            
            # Extrai dados com segurança
            can_data = data.get('data', {})
            if not can_data:
                st.warning("Sem dados CAN disponíveis")
                return
            
            st.subheader("📊 Métricas Principais")
            
            cols = st.columns(4)
            metrics = [
                ("RPM Motor", can_data.get('engine_speed', 0), "RPM"),
                ("Temperatura", can_data.get('engine_temp', 0), "°C"),
                ("Velocidade", can_data.get('vehicle_speed', 0), "km/h"),
                ("Combustível", can_data.get('fuel_level', 0), "%")
            ]
            
            for i, (label, value, unit) in enumerate(metrics):
                with cols[i]:
                    st.markdown(f"""
                        <div class="metric-card">
                            <div class="metric-value">{value} {unit}</div>
                            <div class="metric-label">{label}</div>
                        </div>
                    """, unsafe_allow_html=True)
                
        except Exception as e:
            st.error(f"Erro ao renderizar métricas: {str(e)}")

    def render_gauges(self):
        """Renderiza medidores no estilo John Deere"""
        try:
            if not st.session_state.data_buffer:
                st.warning("Aguardando dados do ESP32...")
                return
            
            last_data = st.session_state.data_buffer[-1]
            if not isinstance(last_data, dict):
                st.warning("Formato de dados inválido")
                return
            
            data = {}
            if 'data' in last_data and isinstance(last_data['data'], dict):
                data = last_data['data']
            
            # Valores padrão para teste/desenvolvimento
            default_data = {
                'engine_speed': 0,
                'engine_temp': 0,
                'oil_pressure': 0,
                'vehicle_speed': 0,
                'fuel_level': 0,
                'engine_load': 0
            }
            
            # Combina dados reais com padrões
            data = {**default_data, **data}
            
            # Seção Motor
            st.markdown(f"""
                <div style='background: white; padding: 15px; border-radius: 10px; border-left: 4px solid {JOHN_DEERE_GREEN}; margin-bottom: 20px;'>
                    <h3 style='color: {JOHN_DEERE_GREEN}; margin:0;'>🔧 Parâmetros do Motor</h3>
                    <p style='color: #666; margin:0;'>Monitoramento em tempo real do motor</p>
                </div>
            """, unsafe_allow_html=True)
            
            col1, col2, col3 = st.columns(3)
            
            # RPM do Motor (PGN 61444 - EEC1)
            with col1:
                fig = go.Figure(go.Indicator(
                    mode="gauge+number+delta",
                    value=data.get('engine_speed', 0),
                    title={
                        'text': "Rotação do Motor<br><span style='font-size:0.8em;color:gray'>Velocidade Atual</span>",
                        'font': {'color': JOHN_DEERE_GREEN}
                    },
                    delta={
                        'reference': 2200,
                        'increasing': {'color': "red"},
                        'decreasing': {'color': JOHN_DEERE_GREEN}
                    },
                    gauge={
                        'axis': {'range': [0, 3000], 'tickwidth': 1},
                        'bar': {'color': JOHN_DEERE_GREEN},
                        'bgcolor': "white",
                        'borderwidth': 2,
                        'bordercolor': "gray",
                        'steps': [
                            {'range': [0, 800], 'color': '#e6f2e6', 'name': 'Marcha Lenta'},
                            {'range': [800, 2200], 'color': '#b3d9b3', 'name': 'Operação Normal'},
                            {'range': [2200, 3000], 'color': '#ffcccc', 'name': 'Alerta'}
                        ],
                        'threshold': {
                            'line': {'color': "red", 'width': 4},
                            'thickness': 0.75,
                            'value': 2500
                        }
                    }
                ))
                fig.update_layout(
                    height=250,
                    font={'color': JOHN_DEERE_GREEN},
                    margin=dict(l=20, r=20, t=50, b=20)
                )
                st.plotly_chart(fig, use_container_width=True)
                st.markdown("""
                    <div style='text-align: center; color: #666;'>
                        <small>PGN: 61444 (EEC1) - Rotação nominal: 2200 RPM</small>
                    </div>
                """, unsafe_allow_html=True)

            # Temperatura do Motor (PGN 65262 - ET1)
            with col2:
                fig = go.Figure(go.Indicator(
                    mode="gauge+number+delta",
                    value=data.get('engine_temp', 0),
                    title={
                        'text': "Temperatura do Motor<br><span style='font-size:0.8em;color:gray'>Monitoramento Térmico</span>",
                        'font': {'color': JOHN_DEERE_GREEN}
                    },
                    delta={
                        'reference': 85,
                        'increasing': {'color': "red"},
                        'decreasing': {'color': JOHN_DEERE_GREEN}
                    },
                    gauge={
                        'axis': {'range': [0, 120], 'tickwidth': 1},
                        'bar': {'color': JOHN_DEERE_GREEN},
                        'bgcolor': "white",
                        'borderwidth': 2,
                        'bordercolor': "gray",
                        'steps': [
                            {'range': [0, 40], 'color': '#cce5ff', 'name': 'Frio'},
                            {'range': [40, 85], 'color': '#b3d9b3', 'name': 'Ideal'},
                            {'range': [85, 120], 'color': '#ffcccc', 'name': 'Crítico'}
                        ],
                        'threshold': {
                            'line': {'color': "red", 'width': 4},
                            'thickness': 0.75,
                            'value': 95
                        }
                    }
                ))
                fig.update_layout(
                    height=250,
                    font={'color': JOHN_DEERE_GREEN},
                    margin=dict(l=20, r=20, t=50, b=20)
                )
                st.plotly_chart(fig, use_container_width=True)
                st.markdown("""
                    <div style='text-align: center; color: #666;'>
                        <small>PGN: 65262 (ET1) - Temperatura ideal: 85°C</small>
                    </div>
                """, unsafe_allow_html=True)

            # Pressão do Óleo (PGN 65263 - EOP)
            with col3:
                fig = go.Figure(go.Indicator(
                    mode="gauge+number+delta",
                    value=data.get('oil_pressure', 0),
                    title={
                        'text': "Pressão do Óleo<br><span style='font-size:0.8em;color:gray'>Sistema de Lubrificação</span>",
                        'font': {'color': JOHN_DEERE_GREEN}
                    },
                    delta={
                        'reference': 3.5,
                        'decreasing': {'color': "red"},
                        'increasing': {'color': JOHN_DEERE_GREEN}
                    },
                    gauge={
                        'axis': {'range': [0, 7], 'tickwidth': 1},
                        'bar': {'color': JOHN_DEERE_GREEN},
                        'bgcolor': "white",
                        'borderwidth': 2,
                        'bordercolor': "gray",
                        'steps': [
                            {'range': [0, 2], 'color': '#ffcccc', 'name': 'Crítico'},
                            {'range': [2, 5], 'color': '#b3d9b3', 'name': 'Normal'},
                            {'range': [5, 7], 'color': '#ffe6b3', 'name': 'Alto'}
                        ],
                        'threshold': {
                            'line': {'color': "red", 'width': 4},
                            'thickness': 0.75,
                            'value': 2
                        }
                    }
                ))
                fig.update_layout(
                    height=250,
                    font={'color': JOHN_DEERE_GREEN},
                    margin=dict(l=20, r=20, t=50, b=20)
                )
                st.plotly_chart(fig, use_container_width=True)
                st.markdown("""
                    <div style='text-align: center; color: #666;'>
                        <small>PGN: 65263 (EOP) - Pressão mínima: 2.0 bar</small>
                    </div>
                """, unsafe_allow_html=True)

            # Seção Veículo
            st.markdown(f"""
                <div style='background: white; padding: 15px; border-radius: 10px; border-left: 4px solid {JOHN_DEERE_GREEN}; margin: 20px 0;'>
                    <h3 style='color: {JOHN_DEERE_GREEN}; margin:0;'>🚜 Parâmetros do Veículo</h3>
                    <p style='color: #666; margin:0;'>Informações gerais do equipamento</p>
                </div>
            """, unsafe_allow_html=True)
            
            col1, col2, col3 = st.columns(3)

            # Velocidade (PGN 65256 - VP)
            with col1:
                fig = go.Figure(go.Indicator(
                    mode="gauge+number",
                    value=data.get('vehicle_speed', 0),
                    title={
                        'text': "Velocidade do Veículo<br><span style='font-size:0.8em;color:gray'>Velocidade de Operação</span>",
                        'font': {'color': JOHN_DEERE_GREEN}
                    },
                    gauge={
                        'axis': {'range': [0, 50], 'tickwidth': 1},
                        'bar': {'color': JOHN_DEERE_GREEN},
                        'bgcolor': "white",
                        'borderwidth': 2,
                        'bordercolor': "gray",
                        'steps': [
                            {'range': [0, 15], 'color': '#e6f2e6', 'name': 'Baixa'},
                            {'range': [15, 30], 'color': '#b3d9b3', 'name': 'Média'},
                            {'range': [30, 50], 'color': '#ffe6b3', 'name': 'Alta'}
                        ]
                    }
                ))
                fig.update_layout(
                    height=250,
                    font={'color': JOHN_DEERE_GREEN},
                    margin=dict(l=20, r=20, t=50, b=20)
                )
                st.plotly_chart(fig, use_container_width=True)
                st.markdown("""
                    <div style='text-align: center; color: #666;'>
                        <small>PGN: 65256 (VP) - Velocidade de trabalho</small>
                    </div>
                """, unsafe_allow_html=True)

            # Nível de Combustível (PGN 65276 - FL)
            with col2:
                fig = go.Figure(go.Indicator(
                    mode="gauge+number",
                    value=data.get('fuel_level', 0),
                    title={
                        'text': "Nível de Combustível<br><span style='font-size:0.8em;color:gray'>Capacidade Restante</span>",
                        'font': {'color': JOHN_DEERE_GREEN}
                    },
                    gauge={
                        'axis': {'range': [0, 100], 'tickwidth': 1},
                        'bar': {'color': JOHN_DEERE_GREEN},
                        'bgcolor': "white",
                        'borderwidth': 2,
                        'bordercolor': "gray",
                        'steps': [
                            {'range': [0, 20], 'color': '#ffcccc', 'name': 'Reserva'},
                            {'range': [20, 60], 'color': '#ffe6b3', 'name': 'Médio'},
                            {'range': [60, 100], 'color': '#b3d9b3', 'name': 'Cheio'}
                        ],
                        'threshold': {
                            'line': {'color': "red", 'width': 4},
                            'thickness': 0.75,
                            'value': 15
                        }
                    }
                ))
                fig.update_layout(
                    height=250,
                    font={'color': JOHN_DEERE_GREEN},
                    margin=dict(l=20, r=20, t=50, b=20)
                )
                st.plotly_chart(fig, use_container_width=True)
                st.markdown("""
                    <div style='text-align: center; color: #666;'>
                        <small>PGN: 65276 (FL) - Alerta em 15%</small>
                    </div>
                """, unsafe_allow_html=True)

            # Carga do Motor (PGN 61443 - EEC2)
            with col3:
                fig = go.Figure(go.Indicator(
                    mode="gauge+number",
                    value=data.get('engine_load', 0),
                    title={
                        'text': "Carga do Motor<br><span style='font-size:0.8em;color:gray'>Demanda de Potência</span>",
                        'font': {'color': JOHN_DEERE_GREEN}
                    },
                    gauge={
                        'axis': {'range': [0, 100], 'tickwidth': 1},
                        'bar': {'color': JOHN_DEERE_GREEN},
                        'bgcolor': "white",
                        'borderwidth': 2,
                        'bordercolor': "gray",
                        'steps': [
                            {'range': [0, 40], 'color': '#e6f2e6', 'name': 'Leve'},
                            {'range': [40, 80], 'color': '#b3d9b3', 'name': 'Moderada'},
                            {'range': [80, 100], 'color': '#ffe6b3', 'name': 'Pesada'}
                        ]
                    }
                ))
                fig.update_layout(
                    height=250,
                    font={'color': JOHN_DEERE_GREEN},
                    margin=dict(l=20, r=20, t=50, b=20)
                )
                st.plotly_chart(fig, use_container_width=True)
                st.markdown("""
                    <div style='text-align: center; color: #666;'>
                        <small>PGN: 61443 (EEC2) - Carga atual do motor</small>
                    </div>
                """, unsafe_allow_html=True)

        except Exception as e:
            st.error(f"Erro ao renderizar gauges: {str(e)}")
            print(f"Debug - Dados recebidos: {st.session_state.data_buffer}")

    def render_charts(self):
        """Renderiza gráficos"""
        try:
            # Verifica se temos dados no buffer
            if not st.session_state.data_buffer:
                st.warning("Sem dados para exibir nos gráficos")
                return
            
            st.subheader("📈 Gráficos")
            
            # Converte buffer para DataFrame com segurança
            valid_data = []
            for data in st.session_state.data_buffer:
                if isinstance(data, dict) and 'data' in data:
                    valid_data.append(data)
                    
            if not valid_data:
                st.warning("Dados inválidos para gráficos")
                return
            
            df = pd.DataFrame(valid_data)
            
            # Aplica filtros com segurança
            if hasattr(self, 'pgn_filter') and self.pgn_filter:
                try:
                    df = df[df['pgn'].isin([int(p, 16) for p in self.pgn_filter])]
                except:
                    pass  # Ignora erro de filtro
            
            # Verifica se temos colunas para plotar
            plot_columns = [col for col in df.columns 
                           if col not in ['timestamp', 'pgn', 'source', 'local_time']]
            
            if not plot_columns:
                st.warning("Sem dados para plotar")
                return
            
            # Gráfico de linha
            fig = go.Figure()
            
            for col in plot_columns:
                try:
                    fig.add_trace(go.Scatter(
                        x=df['local_time'],
                        y=df[col],
                        name=col,
                        line=dict(color=JOHN_DEERE_GREEN)
                    ))
                except:
                    continue  # Pula coluna com erro
                
            fig.update_layout(
                title="Dados no Tempo",
                xaxis_title="Hora",
                yaxis_title="Valor",
                height=400,
                paper_bgcolor="white",
                plot_bgcolor="white",
                font={'color': '#444'},
                showlegend=True,
                legend=dict(
                    bgcolor="white",
                    bordercolor=JOHN_DEERE_GREEN
                )
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
        except Exception as e:
            st.error(f"Erro ao renderizar gráficos: {str(e)}")

    def render_header(self):
        """Renderiza cabeçalho personalizado"""
        header_html = f"""
            <div style="
                background: linear-gradient(90deg, {JOHN_DEERE_GREEN} 0%, {JOHN_DEERE_DARK_GREEN} 100%);
                padding: 1.5rem;
                border-radius: 10px;
                margin-bottom: 2rem;
                border-bottom: 4px solid {JOHN_DEERE_YELLOW};
                display: flex;
                align-items: center;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            ">
                <img src="https://www.deere.com/assets/images/common/deere-logo.svg" 
                     style="height: 50px; margin-right: 20px;">
                <div>
                    <h1 style="color: white; margin: 0;">Monitor ISO BUS</h1>
                    <p style="color: {JOHN_DEERE_YELLOW}; margin: 0;">Sistema de Monitoramento de Implementos Agrícolas</p>
                </div>
            </div>
        """
        st.markdown(header_html, unsafe_allow_html=True)

    def render_status_cards(self):
        """Renderiza cards de status"""
        cols = st.columns(4)
        
        # Status da Conexão
        with cols[0]:
            st.markdown(f"""
                <div style="
                    background: white;
                    padding: 1rem;
                    border-radius: 8px;
                    border-left: 4px solid {JOHN_DEERE_GREEN};
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                ">
                    <p style="color: #666; margin: 0;">Status da Conexão</p>
                    <h3 style="color: {JOHN_DEERE_GREEN}; margin: 0;">
                        {'🟢 Online' if st.session_state.connected else '🔴 Offline'}
                    </h3>
                </div>
            """, unsafe_allow_html=True)
        
        # IP do Dispositivo
        with cols[1]:
            st.markdown(f"""
                <div style="
                    background: white;
                    padding: 1rem;
                    border-radius: 8px;
                    border-left: 4px solid {JOHN_DEERE_GREEN};
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                ">
                    <p style="color: #666; margin: 0;">IP do Dispositivo</p>
                    <h3 style="color: {JOHN_DEERE_GREEN}; margin: 0;">
                        {st.session_state.esp32_ip}
                    </h3>
                </div>
            """, unsafe_allow_html=True)
        
        # Total de Mensagens
        with cols[2]:
            total_msgs = len(st.session_state.data_buffer)
            st.markdown(f"""
                <div style="
                    background: white;
                    padding: 1rem;
                    border-radius: 8px;
                    border-left: 4px solid {JOHN_DEERE_GREEN};
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                ">
                    <p style="color: #666; margin: 0;">Total de Mensagens</p>
                    <h3 style="color: {JOHN_DEERE_GREEN}; margin: 0;">
                        {total_msgs}
                    </h3>
                </div>
            """, unsafe_allow_html=True)
        
        # Taxa de Atualização
        with cols[3]:
            st.markdown(f"""
                <div style="
                    background: white;
                    padding: 1rem;
                    border-radius: 8px;
                    border-left: 4px solid {JOHN_DEERE_GREEN};
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                ">
                    <p style="color: #666; margin: 0;">Taxa de Atualização</p>
                    <h3 style="color: {JOHN_DEERE_GREEN}; margin: 0;">
                        {self.update_rate}s
                    </h3>
                </div>
            """, unsafe_allow_html=True)

    def run(self):
        """Executa aplicação"""
        try:
            # Renderiza sidebar
            self.render_sidebar()
            
            # Container principal
            with st.container():
                # Cabeçalho personalizado
                self.render_header()
                
                # Cards de status
                self.render_status_cards()
                
                # Atualiza dados
                if self.update_data() and st.session_state.data_buffer:
                    # Renderiza componentes
                    col1, col2 = st.columns([2,1])
                    
                    with col1:
                        # Gauges principais
                        self.render_gauges()
                        
                    with col2:
                        # Métricas e alertas
                        self.render_metrics(st.session_state.data_buffer[-1])
                        
                    # Gráficos em tela cheia
                    self.render_charts()
                    
                    # Dados brutos (expansível)
                    with st.expander("🔍 Dados ISO BUS"):
                        st.json(st.session_state.data_buffer[-1])
                else:
                    st.warning("⏳ Aguardando dados do ESP32...")
                
            # Atualiza conforme taxa configurada
            time.sleep(self.update_rate)
            st.rerun()
            
        except Exception as e:
            st.error(f"Erro na execução: {str(e)}")

if __name__ == "__main__":
    app = JDMonitor()
    app.run() 