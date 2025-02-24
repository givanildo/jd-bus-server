class J1939Decoder:
    @staticmethod
    def decode_message(pgn, data):
        """Decodifica mensagem J1939"""
        if pgn == 61444:  # Electronic Engine Controller 1
            return {
                'name': 'Electronic Engine Controller 1',
                'values': {
                    'engine_rpm': {
                        'value': (data[4] * 256 + data[3]) * 0.125,
                        'unit': 'RPM',
                        'range': [0, 8000]
                    },
                    'speed': {
                        'value': (data[2] * 256 + data[1]) * 0.0039,
                        'unit': 'km/h',
                        'range': [0, 250]
                    },
                    'fuel_rate': {
                        'value': (data[6] * 256 + data[5]) * 0.05,
                        'unit': 'L/h',
                        'range': [0, 100]
                    }
                }
            }
        return None 