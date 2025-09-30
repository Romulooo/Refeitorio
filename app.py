import os
from flask import Flask, redirect, url_for
from config import config_by_name
from extensions import db, migrate, bcrypt, login_manager
from models.models import User

def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config_by_name[config_name])
    
    # Inicializa as extensões com a aplicação
    db.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    from models.models import User, Dish, Menu, Reservation 

    # --- Configuração do Flask-Login ---
    # Informa ao LoginManager qual é a rota de login
    login_manager.login_view = 'auth.login'
    # Mensagem exibida ao tentar acessar uma página protegida sem login
    login_manager.login_message = 'Por favor, faça login para acessar esta página.'
    login_manager.login_message_category = 'info' # Categoria da mensagem flash

    @login_manager.user_loader
    def load_user(user_id):
        # Esta função é usada pelo Flask-Login para recarregar o objeto do usuário
        # a partir do ID de usuário armazenado na sessão.
        return User.query.get(int(user_id))

    with app.app_context():
        # --- Importa e Registra os Blueprints ---
        from routes.auth import auth_bp
        app.register_blueprint(auth_bp)

        from routes.dashboard import dashboard_bp
        app.register_blueprint(dashboard_bp)

        from routes.management import management_bp
        app.register_blueprint(management_bp)

        # --- Rota Principal ---
        @app.route('/')
        def index():
            return redirect(url_for('auth.login'))

    return app

# --- Execução da Aplicação ---
app = create_app('dev')

if __name__ == '__main__':
    app.run(host='0.0.0.0')