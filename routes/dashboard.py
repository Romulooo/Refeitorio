from flask import Blueprint, render_template
from flask_login import login_required, current_user
from models.models import Menu
from datetime import date # Para pegar a data de hoje

dashboard_bp = Blueprint(
    'dashboard',
    __name__,
    template_folder='templates',
    url_prefix='/dashboard'
)

@dashboard_bp.route('/')
@login_required
def index():
    """
    Página principal após o login.
    Exibe uma saudação personalizada e o cardápio do dia.
    """
    # 1. Busca o cardápio cadastrado para a data de hoje
    # O ideal é filtrar por data e tipo de refeição (Almoço/Janta), 
    # mas para simplificar, vamos pegar apenas pela data.
    today = date.today()
    todays_menu = Menu.query.filter_by(date=today).first()
    
    # 2. Envia o usuário logado (current_user) e o cardápio para o template
    return render_template('dashboard/index.html', user=current_user, menu=todays_menu)


@dashboard_bp.route('/perfil')
@login_required
def profile():
    """
    Página para o usuário visualizar e editar seu perfil.
    Aqui ele poderá registrar restrições alimentares ([US14]).
    """
    return render_template('dashboard/profile.html')

@dashboard_bp.route('/minhas-reservas')
@login_required
def my_reservations():
    """
    Página para o usuário ver seu histórico de agendamentos ([US06], [US07]).
    """
    return render_template('dashboard/my_reservations.html')