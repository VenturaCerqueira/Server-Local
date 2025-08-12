# run.py
import os
from dotenv import load_dotenv
from pyngrok import ngrok, conf
from servidor_app import create_app

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

def start_ngrok(port):
    """Inicia um túnel ngrok seguro com autenticação."""
    # Obtém o authtoken e as credenciais de autenticação das variáveis de ambiente
    authtoken = os.environ.get("NGROK_AUTHTOKEN")
    basic_auth = os.environ.get("NGROK_BASIC_AUTH")

    if not basic_auth:
        print("AVISO: A variável de ambiente NGROK_BASIC_AUTH não foi definida. O túnel será público.")
    
    try:
        if authtoken:
            ngrok.set_auth_token(authtoken)

        print("Iniciando túnel ngrok...")
        public_url = ngrok.connect(port, "http", auth=basic_auth).public_url
        print(f" * Túnel Ngrok seguro rodando em: {public_url}")
        print(f" * Usuário/Senha para acesso: {basic_auth.split(':')[0]} / {'*' * len(basic_auth.split(':')[1])}")
        
        return public_url

    except Exception as e:
        print(f"Erro ao iniciar o ngrok: {e}")
        return None

if __name__ == '__main__':
    # Define a porta da aplicação
    port = 5000
    
    # O modo debug não deve ser usado em produção, mas é útil para desenvolvimento.
    debug_mode = True 

    # Inicia o túnel ngrok APENAS UMA VEZ
    # antes de iniciar a aplicação Flask.
    public_url = start_ngrok(port)
    
    if public_url:
        print(f" * A aplicação Flask será acessível publicamente através de: {public_url}")
    else:
        print(" * Não foi possível iniciar o túnel ngrok. A aplicação rodará apenas localmente.")

    try:
        # Cria a aplicação Flask
        app = create_app()

        # Inicia a aplicação Flask
        # Use `use_reloader=False` para evitar que o ngrok seja reiniciado
        # e cause o erro de sessão duplicada. O reloader ainda funcionará,
        # mas o processo principal não será reiniciado.
        app.run(port=port, debug=debug_mode, use_reloader=False)

    except Exception as e:
        print(f"Erro ao rodar a aplicação Flask: {e}")