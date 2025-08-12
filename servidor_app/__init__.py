# servidor_app/__init__.py

from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
import os

# Instanciar o SQLAlchemy e o LoginManager
db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'main.login'
login_manager.login_message_category = 'info'
login_manager.login_message = 'Por favor, faça login para acessar esta página.'

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object('servidor_app.config.Config')

    if test_config:
        app.config.from_mapping(test_config)

    # Inicializar as extensões com a aplicação
    db.init_app(app)
    login_manager.init_app(app)

    # Importar os modelos e blueprints após db ser inicializado para evitar o circular import
    from .models.user_model import User
    from .controllers.main_controller import main_bp
    from .controllers.api_controller import api_bp
    
    # Registrar os Blueprints
    app.register_blueprint(main_bp)
    app.register_blueprint(api_bp)

    return app

# Adicionar o user loader, que o Flask-Login precisa para carregar os usuários
from .models.user_model import User
@login_manager.user_loader
def load_user(user_id):
    # Carrega o usuário do banco de dados
    return User.query.get(int(user_id))