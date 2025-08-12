# servidor_app/__init__.py

from flask import Flask
from .config import Config
from .controllers.main_controller import main_bp
from .controllers.api_controller import api_bp
from flask_login import LoginManager
from werkzeug.security import generate_password_hash
import os

# Instanciar o LoginManager
login_manager = LoginManager()
login_manager.login_view = 'main.login' # Rota para a página de login
login_manager.login_message_category = 'info' # Categoria para mensagens de flash
login_manager.login_message = 'Por favor, faça login para acessar esta página.'

def create_app(test_config=None):
    # Cria e configura a aplicação
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(Config)
    
    # Gerar uma SECRET_KEY se não existir. Isso é crucial para sessões do Flask
    if not app.config.get('SECRET_KEY'):
        app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') or os.urandom(24)

    if test_config:
        app.config.from_mapping(test_config)

    # Inicializar o Flask-Login com a aplicação
    login_manager.init_app(app)

    # Registrar os Blueprints
    app.register_blueprint(main_bp)
    app.register_blueprint(api_bp)

    return app

# Adicionar o user loader, que o Flask-Login precisa para carregar os usuários
from .models.user_model import User
@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)