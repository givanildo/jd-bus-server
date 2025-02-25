import os
import subprocess
import sys
import shutil  # Para operações de arquivo multiplataforma
from datetime import datetime
import fnmatch

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
            'backup_*/',
            '*.bak',
            '*~',
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
        
    def check_modified_files(self):
        """Verifica arquivos modificados"""
        try:
            print("\n🔍 Verificando modificações...")
            
            # Lista de padrões para ignorar
            ignore_patterns = [
                'backup*',
                '*.bak',
                '*~',
                '*.backup',
                'backup_*',
                '*.old'
            ]
            
            # Verifica arquivos modificados excluindo backups
            result = subprocess.run(
                ['git', 'status', '--porcelain', '-u'],
                capture_output=True,
                text=True
            )
            
            modified = []
            for line in result.stdout.split('\n'):
                if not line:
                    continue
                    
                file_path = line[3:]
                
                # Ignora arquivos de backup
                if any(fnmatch.fnmatch(file_path, pattern) 
                      for pattern in ignore_patterns):
                    continue
                    
                modified.append(file_path)
                print(f"📝 Modificado: {file_path}")
                
            return modified
            
        except Exception as e:
            print(f"❌ Erro ao verificar modificações: {e}")
            return []
        
    def update_github(self):
        """Atualiza repositório no GitHub com verificação melhorada"""
        try:
            print("\n🚀 Atualizando GitHub...")
            
            # Verifica arquivos modificados
            modified = self.check_modified_files()
            
            if not modified:
                print("✨ Nenhuma modificação encontrada!")
                return True
            
            # Adiciona todos os arquivos modificados
            for file in modified:
                try:
                    subprocess.run(['git', 'add', file], check=True)
                    print(f"✅ Adicionado: {file}")
                except Exception as e:
                    print(f"❌ Erro ao adicionar {file}: {e}")
            
            # Prepara mensagem de commit
            changes = [f"- {f}: Atualizado" for f in modified]
            
            commit_msg = f"""Atualização Monitor John Deere {datetime.now().strftime('%Y-%m-%d %H:%M')}:

Mudanças:
{chr(10).join(changes)}"""

            # Commit e push
            try:
                subprocess.run(['git', 'commit', '-m', commit_msg], check=True)
                subprocess.run(['git', 'push', 'origin', 'main'], check=True)
                print("\n✅ GitHub atualizado com sucesso!")
                return True
            except Exception as e:
                print(f"\n❌ Erro no commit/push: {e}")
                return False
            
        except Exception as e:
            print(f"\n❌ Erro ao atualizar GitHub: {e}")
            return False
            
    def clean_backups(self):
        """Remove backups do repositório"""
        try:
            print("\n🧹 Removendo backups do repositório...")
            
            # Remove backups do git
            subprocess.run([
                'git', 'rm', '-r', '--cached', 
                '--ignore-unmatch',  # Não falha se arquivo não existe
                'backup_*/',
                '*.bak',
                '*~'
            ], check=True)
            
            # Força git a respeitar .gitignore
            subprocess.run(['git', 'add', '.gitignore'])
            subprocess.run([
                'git', 'commit', '-m',
                'Remove backup files from repository'
            ])
            
            print("✅ Backups removidos!")
            return True
        except Exception as e:
            print(f"❌ Erro ao remover backups: {e}")
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
            
        # Remove backups
        if not self.clean_backups():
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