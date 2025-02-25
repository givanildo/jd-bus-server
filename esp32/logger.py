import time
import os

class Logger:
    """Sistema de logs com rotação de arquivos"""
    
    # Níveis de log
    DEBUG = 10
    INFO = 20
    WARNING = 30
    ERROR = 40
    
    # Configurações
    MAX_LOG_SIZE = 1024 * 1024  # 1MB
    MAX_LOG_FILES = 3
    
    def __init__(self, min_level=INFO):
        self.min_level = min_level
        self.log_dir = 'logs'
        self.log_file = 'jd_monitor.log'
        
        # Cria diretório de logs
        if not self.log_dir in os.listdir():
            os.mkdir(self.log_dir)
            
        # Verifica tamanho do log
        self._check_log_size()
            
    def _check_log_size(self):
        """Verifica e rotaciona logs se necessário"""
        try:
            log_path = f'{self.log_dir}/{self.log_file}'
            if log_path in os.listdir(self.log_dir):
                if os.stat(log_path)[6] > self.MAX_LOG_SIZE:
                    self._rotate_logs()
        except:
            pass
            
    def _rotate_logs(self):
        """Rotaciona arquivos de log"""
        try:
            # Remove log mais antigo
            old_log = f'{self.log_dir}/{self.log_file}.{self.MAX_LOG_FILES}'
            if old_log in os.listdir(self.log_dir):
                os.remove(old_log)
                
            # Move logs existentes
            for i in range(self.MAX_LOG_FILES-1, 0, -1):
                old = f'{self.log_dir}/{self.log_file}.{i}'
                new = f'{self.log_dir}/{self.log_file}.{i+1}'
                if old in os.listdir(self.log_dir):
                    os.rename(old, new)
                    
            # Move log atual
            os.rename(
                f'{self.log_dir}/{self.log_file}',
                f'{self.log_dir}/{self.log_file}.1'
            )
        except:
            pass
            
    def _log(self, level, module, message):
        """Registra uma mensagem de log"""
        if level >= self.min_level:
            try:
                # Formata mensagem
                timestamp = time.localtime()
                log_entry = (
                    f"{timestamp[3]:02d}:{timestamp[4]:02d}:{timestamp[5]:02d} "
                    f"[{module}] {message}\n"
                )
                
                # Imprime no console
                print(log_entry, end='')
                
                # Salva no arquivo
                with open(f'{self.log_dir}/{self.log_file}', 'a') as f:
                    f.write(log_entry)
                    
                # Verifica tamanho
                self._check_log_size()
                    
            except Exception as e:
                print(f"Erro ao salvar log: {e}")
                
    def debug(self, module, message):
        self._log(self.DEBUG, module, message)
        
    def info(self, module, message):
        self._log(self.INFO, module, message)
        
    def warning(self, module, message):
        self._log(self.WARNING, module, message)
        
    def error(self, module, message):
        self._log(self.ERROR, module, message)
        
    def critical(self, module, message):
        """Log nível CRITICAL"""
        self._log(50, module, message) 