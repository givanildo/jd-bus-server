import os
import subprocess

def publish_to_github():
    """Publica projeto no GitHub"""
    try:
        # Configurar credenciais
        os.system('git config --global user.email "givanildobrunetta@gmail.com"')
        os.system('git config --global user.name "givanildo"')
        
        # Inicializar novo repositório
        os.system('git init')
        
        # Adicionar remote
        os.system('git remote add origin https://github.com/givanildo/jd-bus-server.git')
        
        # Adicionar alterações
        os.system('git add .')
        
        # Commit inicial
        commit_msg = "feat: Implementa sistema de monitoramento remoto CAN"
        os.system(f'git commit -m "{commit_msg}"')
        
        # Push
        os.system('git push -u origin main')
        
        print("Projeto publicado com sucesso!")
        
    except Exception as e:
        print(f"Erro na publicação: {str(e)}")

if __name__ == "__main__":
    publish_to_github() 