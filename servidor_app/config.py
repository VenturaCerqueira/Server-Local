# servidor_app/config.py
class Config:
    SECRET_KEY = 'kinfo2013'  # Substitua por uma chave segura e aleatória
    ROOT_DIR = 'D:/Servidor/' # Exemplo de diretório raiz
    UPLOAD_FOLDER = 'uploads' # Diretório para uploads
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB
    ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'zip'}