from functools import wraps
from flask import flash, redirect, url_for
from flask_login import current_user

def role_required(roles):
    """
    Decorador que restringe o acesso a uma rota para usuários com perfis específicos.
    :param roles: Uma lista de UserRole enums permitidos. Ex: [UserRole.NUTRICIONISTA]
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Se o usuário não estiver autenticado, o @login_required já vai cuidar disso.
            # Aqui, verificamos se o perfil do usuário logado está na lista de perfis permitidos.
            if current_user.role not in roles:
                flash('Você não tem permissão para acessar esta página.', 'danger')
                return redirect(url_for('dashboard.index'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator