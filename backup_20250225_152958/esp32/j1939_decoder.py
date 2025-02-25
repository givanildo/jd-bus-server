class J1939Decoder:
    """Decodificador de mensagens J1939 para implementos John Deere"""
    
    def __init__(self):
        # Dicionário de PGNs suportados
        self.pgns = {
            # Engine (Motor)
            0xF004: self._decode_engine_speed,          # Velocidade do Motor
            0xFEF2: self._decode_engine_temperature,    # Temperatura do Motor
            0xFEF3: self._decode_engine_fluid_level,    # Níveis de Fluidos
            
            # Transmission (Transmissão)
            0xF005: self._decode_transmission,          # Estado da Transmissão
            0xFEF5: self._decode_transmission_speed,    # Velocidade da Transmissão
            
            # Hydraulics (Sistema Hidráulico)
            0xFE80: self._decode_hydraulic_pressure,    # Pressão Hidráulica
            0xFE81: self._decode_hydraulic_flow,        # Fluxo Hidráulico
            0xFE82: self._decode_hydraulic_temperature, # Temperatura Hidráulica
            
            # Implement (Implemento)
            0xFE0F: self._decode_implement_status,      # Status do Implemento
            0xFE10: self._decode_implement_position,    # Posição do Implemento
            0xFE11: self._decode_implement_load,        # Carga no Implemento
            
            # Performance (Desempenho)
            0xFEF1: self._decode_fuel_economy,          # Economia de Combustível
            0xFEE9: self._decode_fuel_level,           # Nível de Combustível
            0xFEFC: self._decode_vehicle_speed,        # Velocidade do Veículo
        }

        # Cache de decodificação
        self._decode_cache = {}
        self._cache_size = 100

    def decode_message(self, can_id, data):
        """Decodifica mensagem CAN"""
        try:
            # Extrai PGN
            pgn = (can_id >> 8) & 0x1FFFF
            
            # Verifica cache
            cache_key = f"{pgn}:{data.hex()}"
            if cache_key in self._decode_cache:
                return self._decode_cache[cache_key]
                
            # Decodifica
            if pgn in self.pgns:
                result = self.pgns[pgn](data)
                
                # Atualiza cache
                if len(self._decode_cache) >= self._cache_size:
                    self._decode_cache.pop(next(iter(self._decode_cache)))
                self._decode_cache[cache_key] = result
                
                return result
                
        except Exception as e:
            print(f"Erro ao decodificar mensagem: {e}")
            
        return None

    def _decode_engine_speed(self, data):
        """Decodifica velocidade do motor (RPM)"""
        rpm = ((data[3] << 8) | data[2]) * 0.125
        return {
            'engine_speed': round(rpm, 1),
            'unit': 'RPM'
        }

    def _decode_engine_temperature(self, data):
        """Decodifica temperatura do motor"""
        temp = ((data[1] << 8) | data[0]) * 0.03125 - 273
        return {
            'engine_temp': round(temp, 1),
            'unit': '°C'
        }

    def _decode_engine_fluid_level(self, data):
        """Decodifica níveis de fluidos"""
        return {
            'coolant_level': data[0] * 0.4,      # %
            'oil_level': data[1] * 0.4,          # %
            'unit': '%'
        }

    def _decode_transmission(self, data):
        """Decodifica estado da transmissão"""
        gear = data[0] & 0x0F
        mode = (data[0] >> 4) & 0x0F
        modes = ['Manual', 'Auto', 'PowrShift', 'IVT']
        return {
            'gear': gear,
            'mode': modes[mode] if mode < len(modes) else 'Unknown'
        }

    def _decode_transmission_speed(self, data):
        """Decodifica velocidade da transmissão"""
        speed = ((data[1] << 8) | data[0]) * 0.001
        return {
            'transmission_speed': round(speed, 2),
            'unit': 'km/h'
        }

    def _decode_hydraulic_pressure(self, data):
        """Decodifica pressão hidráulica"""
        pressure = ((data[1] << 8) | data[0]) * 0.5
        return {
            'hydraulic_pressure': round(pressure, 1),
            'unit': 'bar'
        }

    def _decode_hydraulic_flow(self, data):
        """Decodifica fluxo hidráulico"""
        flow = ((data[1] << 8) | data[0]) * 0.1
        return {
            'hydraulic_flow': round(flow, 1),
            'unit': 'L/min'
        }

    def _decode_hydraulic_temperature(self, data):
        """Decodifica temperatura hidráulica"""
        temp = ((data[1] << 8) | data[0]) * 0.03125 - 273
        return {
            'hydraulic_temp': round(temp, 1),
            'unit': '°C'
        }

    def _decode_implement_status(self, data):
        """Decodifica status do implemento"""
        status = data[0] & 0x0F
        states = ['Desligado', 'Ligado', 'Erro', 'Manutenção']
        return {
            'implement_status': states[status] if status < len(states) else 'Unknown'
        }

    def _decode_implement_position(self, data):
        """Decodifica posição do implemento"""
        position = data[0] * 0.4  # 0-100%
        return {
            'implement_position': round(position, 1),
            'unit': '%'
        }

    def _decode_implement_load(self, data):
        """Decodifica carga no implemento"""
        load = ((data[1] << 8) | data[0]) * 0.5
        return {
            'implement_load': round(load, 1),
            'unit': 'kg'
        }

    def _decode_fuel_economy(self, data):
        """Decodifica economia de combustível"""
        consumption = ((data[1] << 8) | data[0]) * 0.05
        return {
            'fuel_consumption': round(consumption, 1),
            'unit': 'L/h'
        }

    def _decode_fuel_level(self, data):
        """Decodifica nível de combustível"""
        level = data[0] * 0.4  # 0-100%
        return {
            'fuel_level': round(level, 1),
            'unit': '%'
        }

    def _decode_vehicle_speed(self, data):
        """Decodifica velocidade do veículo"""
        speed = ((data[1] << 8) | data[0]) * 0.001
        return {
            'vehicle_speed': round(speed, 1),
            'unit': 'km/h'
        }

    # PGNs (Parameter Group Numbers) John Deere
    PGN = {
        'EEC1': 0xF004,  # Electronic Engine Controller 1
        'LFE': 0xFEF2,   # Engine Fuel Economy
        'TFAC': 0xFE44,  # Transmission Fluids
        'ERC1': 0xFE4E,  # Electronic Retarder Controller 1
        'ETC1': 0xFE4D,  # Electronic Transmission Controller 1
        'VDHR': 0xFE49,  # Vehicle Dynamic Hydraulic Retarder
        'IC1': 0xFEDF,   # Instrument Cluster 1
        'VEP1': 0xFEF6,  # Vehicle Electrical Power 1
        'HRVD': 0xFE4F,  # High Resolution Vehicle Distance
        'AT1IG1': 0xF028, # Aftertreatment 1 Intake Gas 1
        'TCFG': 0xFE4C,  # Transmission Configuration
    }

    # SPNs (Suspect Parameter Numbers) específicos John Deere
    SPN = {
        # Engine
        'EngineSpeed': {
            'spn': 190,
            'offset': 0,
            'length': 2,
            'resolution': 0.125,
            'unit': 'rpm'
        },
        'EngineLoad': {
            'spn': 92,
            'offset': 2,
            'length': 1,
            'resolution': 1,
            'unit': '%'
        },
        'FuelRate': {
            'spn': 183,
            'offset': 0,
            'length': 2,
            'resolution': 0.05,
            'unit': 'L/h'
        },
        # Transmission
        'TransmissionGear': {
            'spn': 523,
            'offset': 3,
            'length': 1,
            'resolution': 1,
            'unit': None
        },
        'TransmissionOilTemp': {
            'spn': 177,
            'offset': 0,
            'length': 1,
            'resolution': 1,
            'unit': '°C'
        },
        # Vehicle
        'VehicleSpeed': {
            'spn': 84,
            'offset': 1,
            'length': 2,
            'resolution': 0.00390625,
            'unit': 'km/h'
        },
        # Hydraulics
        'HydraulicOilTemp': {
            'spn': 175,
            'offset': 0,
            'length': 1,
            'resolution': 1,
            'unit': '°C'
        },
        'HydraulicPressure': {
            'spn': 169,
            'offset': 2,
            'length': 1,
            'resolution': 16,
            'unit': 'kPa'
        }
    }

    def get_unit(self, parameter):
        """Retorna unidade de medida"""
        try:
            if parameter in self.SPN:
                return self.SPN[parameter]['unit']
        except:
            pass
        return None 