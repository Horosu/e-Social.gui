import json
import bcrypt
import os

def adicionar_usuario(usuario, senha):
    # Verifica se o arquivo existe
    if os.path.exists('credenciais.json'):
        # Carrega o arquivo existente
        with open('credenciais.json', 'r') as f:
            credenciais = json.load(f)
    else:
        # Cria um novo dicionário se o arquivo não existir
        credenciais = {}

    # Gera o hash da senha
    senha_hash = bcrypt.hashpw(senha.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    # Adiciona ou atualiza o usuário
    credenciais[usuario] = senha_hash

    # Salva as credenciais atualizadas no arquivo JSON
    with open('credenciais.json', 'w') as f:
        json.dump(credenciais, f, indent=4)

# Exemplo de uso
usuario_novo = input("Digite o novo usuário: ")
senha_nova = input("Digite a nova senha: ")

adicionar_usuario(usuario_novo, senha_nova)

print(f"Usuário '{usuario_novo}' adicionado com sucesso!")