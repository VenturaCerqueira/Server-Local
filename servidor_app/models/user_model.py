# servidor_app/models/user_model.py

from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

# Em uma aplicação real, você usaria um banco de dados para armazenar usuários
# Para este exemplo, vamos usar um usuário fixo.
class User(UserMixin):
    def __init__(self, id, username, password_hash):
        self.id = id
        self.username = username
        self.password_hash = password_hash

    @staticmethod
    def get(user_id):
        # Aqui, você buscaria o usuário no banco de dados pelo ID
        # Para o nosso exemplo, vamos retornar o usuário estático se o ID for '1'
        return users.get(user_id)

    def set_password(self, password):
        """Define a senha do usuário, fazendo o hash dela."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Verifica se a senha fornecida corresponde à hash armazenada."""
        return check_password_hash(self.password_hash, password)

# Criamos um "banco de dados" de usuários estático para este exemplo
users = {
    'admin': User(id='admin', username='admin', password_hash=generate_password_hash('kinfo2013'))
}