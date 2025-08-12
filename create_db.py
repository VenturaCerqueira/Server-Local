# create_db.py

from servidor_app import create_app, db
from servidor_app.models.user_model import User
import os

app = create_app()
app.app_context().push()

# Crie o banco de dados e as tabelas
db.create_all()

# Crie um usuário inicial (substitua a senha)
if not User.query.filter_by(username='admin').first():
    admin_user = User(username='admin')
    admin_user.set_password('sua_nova_senha_segura') # TROQUE ESTA SENHA!
    db.session.add(admin_user)
    db.session.commit()
    print("Usuário 'admin' criado com sucesso!")
else:
    print("Usuário 'admin' já existe.")

print("Banco de dados 'app.db' inicializado.")