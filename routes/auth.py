from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required
from extensions import db, bcrypt
from models.models import User

auth_bp = Blueprint(
    'auth', 
    __name__,
    template_folder='templates',
    url_prefix='/auth'
)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """
    Rota para o cadastro de novos usuários.
    - Se o método for GET, exibe o formulário de cadastro.
    - Se o método for POST, processa os dados do formulário.
    """
    if request.method == 'POST':
        # 1. Obter os dados do formulário
        full_name = request.form.get('full_name')
        email = request.form.get('email')
        password = request.form.get('password')

        # 2. Validar os dados
        # Verifica se já existe um usuário com este e-mail
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('Este e-mail já está em uso. Por favor, tente outro.', 'danger')
            return redirect(url_for('auth.register'))

        # 3. Criptografar a senha para armazenamento seguro
        # A função generate_password_hash cria um hash seguro da senha.
        # .decode('utf-8') é usado para converter o hash de bytes para string.
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

        # 4. Criar o novo usuário com o modelo User
        # O role padrão já é 'ESTUDANTE' conforme definido no models.py
        new_user = User(
            full_name=full_name,
            email=email,
            password_hash=hashed_password
        )

        # 5. Salvar o novo usuário no banco de dados
        try:
            db.session.add(new_user)
            db.session.commit()
            flash('Cadastro realizado com sucesso! Faça o login para continuar.', 'success')
            return redirect(url_for('auth.login'))
        except Exception as e:
            db.session.rollback()
            flash(f'Ocorreu um erro ao realizar o cadastro: {e}', 'danger')
            return redirect(url_for('auth.register'))

    # Se a requisição for GET, apenas renderiza a página de cadastro
    return render_template('auth/register.html')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """
    Rota para o login de usuários.
    - Se o método for GET, exibe o formulário de login.
    - Se o método for POST, autentica o usuário.
    """
    if request.method == 'POST':
        # 1. Obter os dados do formulário
        email = request.form.get('email')
        password = request.form.get('password')
        remember = True if request.form.get('remember') else False

        # 2. Buscar o usuário no banco de dados pelo e-mail
        user = User.query.filter_by(email=email).first()

        # 3. Validar se o usuário existe e se a senha está correta
        # bcrypt.check_password_hash compara a senha enviada com o hash salvo no banco.
        if user and bcrypt.check_password_hash(user.password_hash, password):
            # 4. Se a validação for bem-sucedida, inicia a sessão do usuário
            # A função login_user do Flask-Login gerencia a sessão.
            login_user(user, remember=remember)
            flash('Login realizado com sucesso!', 'success')
            # Redireciona o usuário para o dashboard após o login
            return redirect(url_for('dashboard.index'))
        
        # Se a validação falhar, exibe uma mensagem de erro
        flash('Login inválido. Verifique seu e-mail e senha.', 'danger')
        return redirect(url_for('auth.login'))

    # Se a requisição for GET, apenas renderiza a página de login
    return render_template('auth/login.html')


@auth_bp.route('/logout')
@login_required # Garante que apenas usuários logados possam acessar esta rota
def logout():
    """
    Rota para fazer o logout do usuário.
    """
    # A função logout_user do Flask-Login encerra a sessão do usuário.
    logout_user()
    flash('Você saiu do sistema.', 'info')
    return redirect(url_for('auth.login'))