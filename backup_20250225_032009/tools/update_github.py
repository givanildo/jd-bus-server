import os
import subprocess
import sys
import shutil  # Para operações de arquivo multiplataforma
from datetime import datetime

class GitHubUpdater:
    def __init__(self):
        self.repo_url = "https://github.com/givanildo/jd-bus-server.git"
        self.main_files = [
            'esp32/web_server.py',
            'esp32/j1939_decoder.py',
            'web_app/app.py',
            'esp32/main.py',
            'tools/upload_files.py',
            'tools/update_github.py'
        ]
        self.support_files = [
            'docs/',
            '.gitignore',
            'requirements.txt'
        ]
        self.ignore_patterns = [
            'esp32/firmware/*',
            '*.bin',
            '*.hex',
            '*.elf'
        ]
        
    def check_git(self):
        """Verifica se git está configurado"""
        try:
            print("\n🔍 Verificando configuração git...")
            
            # Verifica se é repositório git
            if not os.path.exists('.git'):
                print("❌ Não é um repositório git. Inicializando...")
                subprocess.run(['git', 'init'])
                subprocess.run(['git', 'remote', 'add', 'origin', self.repo_url])
            
            # Verifica branch main
            result = subprocess.run(['git', 'branch', '--show-current'], 
                                 capture_output=True, text=True)
            if 'main' not in result.stdout:
                print("🔄 Mudando para branch main...")
                subprocess.run(['git', 'checkout', '-b', 'main'])
                
            print("✅ Git configurado!")
            return True
            
        except Exception as e:
            print(f"❌ Erro na configuração git: {e}")
            return False
            
    def verify_files(self):
        """Verifica se arquivos principais existem"""
        print("\n🔍 Verificando arquivos...")
        
        missing = []
        for file in self.main_files:
            if not os.path.exists(file):
                missing.append(file)
                
        if missing:
            print(f"❌ Arquivos não encontrados: {missing}")
            return False
            
        print("✅ Todos os arquivos principais encontrados!")
        return True
        
    def backup_files(self):
        """Faz backup dos arquivos principais"""
        try:
            print("\n💾 Criando backup...")
            
            # Cria diretório de backup
            backup_dir = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            os.makedirs(backup_dir, exist_ok=True)
            
            # Copia arquivos usando shutil (multiplataforma)
            for file in self.main_files:
                if os.path.exists(file):
                    # Cria estrutura de diretórios no backup
                    backup_path = os.path.join(backup_dir, file)
                    os.makedirs(os.path.dirname(backup_path), exist_ok=True)
                    
                    # Copia arquivo
                    shutil.copy2(file, backup_path)
                    print(f"✅ Backup: {file}")
                    
            print(f"✅ Backup criado em: {backup_dir}")
            return True
            
        except Exception as e:
            print(f"❌ Erro no backup: {e}")
            return False
        
    def update_github(self):
        """Atualiza repositório no GitHub"""
        try:
            print("\n🚀 Atualizando GitHub...")
            
            # Adiciona arquivos principais
            for file in self.main_files:
                subprocess.run(['git', 'add', file])
                print(f"✅ Adicionado: {file}")
                
            # Adiciona arquivos de suporte
            for file in self.support_files:
                subprocess.run(['git', 'add', file])
                print(f"✅ Adicionado: {file}")
                
            # Commit
            commit_msg = f"""Atualização Monitor John Deere {datetime.now().strftime('%Y-%m-%d %H:%M')}:

- web_server.py: Servidor web funcional
- j1939_decoder.py: Decodificador CAN
- app.py: Interface Streamlit atualizada
- main.py: Programa principal
- upload_files.py: Ferramenta de upload
- update_github.py: Script de atualização
+ Documentação completa"""

            subprocess.run(['git', 'commit', '-m', commit_msg])
            
            # Push
            subprocess.run(['git', 'push', 'origin', 'main'])
            
            print("\n✅ GitHub atualizado com sucesso!")
            return True
            
        except Exception as e:
            print(f"\n❌ Erro ao atualizar GitHub: {e}")
            return False
            
    def run(self):
        """Executa atualização completa"""
        print("\n🚀 Iniciando atualização do Monitor John Deere...")
        print("=" * 50)
        
        # Verifica requisitos
        if not self.check_git():
            return False
            
        if not self.verify_files():
            return False
            
        # Faz backup
        if not self.backup_files():
            return False
            
        # Atualiza GitHub
        if not self.update_github():
            return False
            
        print("\n✨ Atualização concluída com sucesso!")
        print("=" * 50)
        return True

def main():
    updater = GitHubUpdater()
    updater.run()

if __name__ == "__main__":
    main() 