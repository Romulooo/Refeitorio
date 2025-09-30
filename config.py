import os
from dotenv import load_dotenv

# Carrega as variáveis de ambiente do arquivo .env
basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

class Config:
    """Configurações base que servem para qualquer ambiente."""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'uma-chave-secreta-de-fallback-muito-dificil'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

class DevelopmentConfig(Config):
    """Configurações específicas para o ambiente de desenvolvimento."""
    DEBUG = True
    
    # Monta a URI de conexão com o banco de dados a partir das variáveis de ambiente
    DB_USER = os.environ.get('DB_USER')
    DB_PASSWORD = os.environ.get('DB_PASSWORD')
    DB_HOST = os.environ.get('DB_HOST')
    DB_PORT = os.environ.get('DB_PORT')
    DB_NAME = os.environ.get('DB_NAME')
    
    SQLALCHEMY_DATABASE_URI = f"postgresql+psycopg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Você pode adicionar outras classes de configuração no futuro
# class ProductionConfig(Config):
#     DEBUG = False
#     # ... outras configs de produção

# Dicionário para facilitar a escolha da configuração no app.py
config_by_name = dict(
    dev=DevelopmentConfig,
    # prod=ProductionConfig
)