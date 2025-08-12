# servidor_app/__init__.py
from flask import Flask

def create_app():
    """
    Cria e configura uma instância da aplicação Flask.
    """
    app = Flask(__name__, instance_relative_config=True)

    # Carrega a configuração a partir do objeto 'Config' no arquivo config.py
    app.config.from_object('config.Config')

    with app.app_context():
        # Importar e registrar os Blueprints (nossos Controllers)
        from .controllers.main_controller import main_bp
        from .controllers.api_controller import api_bp
        
        app.register_blueprint(main_bp)
        app.register_blueprint(api_bp)

    return app