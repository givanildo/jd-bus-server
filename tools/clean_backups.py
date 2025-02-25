import os
import shutil
import subprocess
from datetime import datetime

class BackupCleaner:
    def __init__(self):
        self.backup_patterns = [
            'backup_*',
            '*.bak',
            '*~',
            '*.backup',
            '*.old'
        ]
        
    def find_backups(self):
        """Encontra todos os backups no repositório"""
        backups = []
        
        print("\n🔍 Procurando backups...")
        
        # Percorre diretório recursivamente
        for root, dirs, files in os.walk('.'):
            # Ignora pasta .git
            if '.git' in root:
                continue
                
            # Verifica diretórios
            for d in dirs[:]:  # Copia lista para poder modificar
                if any(d.startswith('backup_') for p in self.backup_patterns):
                    full_path = os.path.join(root, d)
                    backups.append(full_path)
                    print(f"📁 Encontrado: {full_path}")
                    
            # Verifica arquivos
            for f in files:
                if any(f.endswith(ext) for ext in ['.bak', '~', '.backup', '.old']):
                    full_path = os.path.join(root, f)
                    backups.append(full_path)
                    print(f"📄 Encontrado: {full_path}")
                    
        return backups
        
    def remove_backups(self, backups):
        """Remove backups encontrados"""
        try:
            if not backups:
                print("\n✨ Nenhum backup encontrado!")
                return True
                
            print(f"\n🗑️  Removendo {len(backups)} backups...")
            
            for path in backups:
                try:
                    if os.path.isdir(path):
                        shutil.rmtree(path)
                    else:
                        os.remove(path)
                    print(f"✅ Removido: {path}")
                except Exception as e:
                    print(f"❌ Erro ao remover {path}: {e}")
                    
            # Remove do git
            subprocess.run([
                'git', 'rm', '-r', '--cached',
                '--ignore-unmatch'
            ] + backups)
            
            # Commit remoção
            subprocess.run([
                'git', 'commit', '-m',
                f'Remove backup files ({datetime.now().strftime("%Y-%m-%d %H:%M")})'
            ])
            
            print("\n✅ Backups removidos com sucesso!")
            return True
            
        except Exception as e:
            print(f"\n❌ Erro ao remover backups: {e}")
            return False
            
    def run(self):
        """Executa limpeza"""
        print("\n🧹 Iniciando limpeza de backups...")
        print("=" * 50)
        
        # Encontra backups
        backups = self.find_backups()
        
        # Remove backups
        if not self.remove_backups(backups):
            return False
            
        print("\n✨ Limpeza concluída!")
        print("=" * 50)
        return True

def main():
    cleaner = BackupCleaner()
    cleaner.run()

if __name__ == "__main__":
    main() 