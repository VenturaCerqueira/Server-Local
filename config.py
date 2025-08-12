# config.py
import os

class Config:
    """
    Classe de configuração para a aplicação Flask.
    """
    # IMPORTANTE: VERIFIQUE SE O CAMINHO ESTÁ CORRETO
    # Certifique-se de que este caminho é o mesmo do seu servidor.
    ROOT_DIR = os.path.abspath(r'd:\\Servidor')

    # Chave secreta para segurança da sessão do Flask
    SECRET_KEY = os.urandom(24)

    # Limite de 16 GB para uploads
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024 * 1024