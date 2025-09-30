# routes/management.py

"""
Blueprint para as rotas de gerenciamento do sistema, acessíveis apenas por perfis
privilegiados como Nutricionista e Administrador.

Inclui o Gerenciamento de Pratos (Dishes) e de Cardápios (Menus).
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from datetime import datetime

# Importações dos modelos e extensões
from models.models import Dish, Menu, UserRole, MealType
from extensions import db
from utils.decorators import role_required

# Definição do Blueprint
management_bp = Blueprint(
    'management',
    __name__,
    template_folder='templates',
    url_prefix='/management'
)


# --- GERENCIAMENTO DE PRATOS (DISHES) ---

@management_bp.route('/dishes')
@login_required
@role_required([UserRole.NUTRICIONISTA, UserRole.ADMIN])
def list_dishes():
    """Exibe uma lista de todos os pratos cadastrados, ordenados por nome."""
    dishes = Dish.query.order_by(Dish.name).all()
    return render_template('management/list_dishes.html', dishes=dishes)


@management_bp.route('/dishes/add', methods=['GET', 'POST'])
@login_required
@role_required([UserRole.NUTRICIONISTA, UserRole.ADMIN])
def add_dish():
    """Exibe o formulário para adicionar um novo prato e processa o envio."""
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        nutritional_info = request.form.get('nutritional_info')

        if not name:
            flash('O nome do prato é obrigatório.', 'danger')
        else:
            new_dish = Dish(name=name, description=description, nutritional_info=nutritional_info)
            db.session.add(new_dish)
            db.session.commit()
            flash('Prato cadastrado com sucesso!', 'success')
            return redirect(url_for('management.list_dishes'))

    # Para requisições GET, apenas exibe o formulário.
    # A variável 'dish' é None para indicar que é um formulário de adição.
    return render_template('management/dish_form.html', form_title='Cadastrar Novo Prato', dish=None)


@management_bp.route('/dishes/edit/<int:dish_id>', methods=['GET', 'POST'])
@login_required
@role_required([UserRole.NUTRICIONISTA, UserRole.ADMIN])
def edit_dish(dish_id):
    """Exibe o formulário para editar um prato existente e processa a atualização."""
    # get_or_404 busca o prato pelo ID ou retorna um erro 404 (Not Found) se não existir.
    dish = Dish.query.get_or_404(dish_id)

    if request.method == 'POST':
        # Atualiza os atributos do objeto 'dish' com os dados do formulário.
        dish.name = request.form.get('name')
        dish.description = request.form.get('description')
        dish.nutritional_info = request.form.get('nutritional_info')
        
        if not dish.name:
            flash('O nome do prato é obrigatório.', 'danger')
        else:
            db.session.commit() # Apenas 'commit' é necessário, pois o objeto já está na sessão.
            flash('Prato atualizado com sucesso!', 'success')
            return redirect(url_for('management.list_dishes'))

    # Para requisições GET, exibe o formulário preenchido com os dados do prato.
    return render_template('management/dish_form.html', form_title='Editar Prato', dish=dish)


@management_bp.route('/dishes/delete/<int:dish_id>', methods=['POST'])
@login_required
@role_required([UserRole.NUTRICIONISTA, UserRole.ADMIN])
def delete_dish(dish_id):
    """Deleta um prato do banco de dados, com validação."""
    dish = Dish.query.get_or_404(dish_id)
    
    # Validação importante: Verifica se o prato está sendo usado em algum cardápio.
    # 'dish.menus' é o backref que criamos no modelo Menu.
    if dish.menus:
        flash('Este prato não pode ser removido, pois está associado a um ou mais cardápios.', 'danger')
        return redirect(url_for('management.list_dishes'))

    db.session.delete(dish)
    db.session.commit()
    flash('Prato removido com sucesso!', 'success')
    return redirect(url_for('management.list_dishes'))


# --- GERENCIAMENTO DE CARDÁPIOS (MENUS) ---

@management_bp.route('/menus')
@login_required
@role_required([UserRole.NUTRICIONISTA, UserRole.ADMIN])
def list_menus():
    """Exibe uma lista de todos os cardápios cadastrados, ordenados por data."""
    menus = Menu.query.order_by(Menu.date.desc()).all()
    return render_template('management/list_menus.html', menus=menus)


@management_bp.route('/menus/add', methods=['GET', 'POST'])
@login_required
@role_required([UserRole.NUTRICIONISTA, UserRole.ADMIN])
def add_menu():
    """Exibe o formulário para criar um novo cardápio e processa o envio."""
    if request.method == 'POST':
        date_str = request.form.get('date')
        meal_type_str = request.form.get('meal_type')
        # request.form.getlist() é usado para obter todos os valores de campos com o mesmo nome (checkboxes).
        dish_ids = request.form.getlist('dishes')

        if not date_str or not meal_type_str or not dish_ids:
            flash('Data, tipo de refeição e ao menos um prato são obrigatórios.', 'danger')
        else:
            date = datetime.strptime(date_str, '%Y-%m-%d').date()
            meal_type = MealType[meal_type_str]
            
            new_menu = Menu(date=date, meal_type=meal_type)
            selected_dishes = Dish.query.filter(Dish.id.in_(dish_ids)).all()
            new_menu.dishes.extend(selected_dishes) # Adiciona os pratos à relação many-to-many.
            
            db.session.add(new_menu)
            db.session.commit()
            flash('Cardápio criado com sucesso!', 'success')
            return redirect(url_for('management.list_menus'))

    # Para requisições GET, busca todos os pratos e tipos de refeição para montar o formulário.
    all_dishes = Dish.query.order_by(Dish.name).all()
    return render_template('management/menu_form.html', form_title="Montar Novo Cardápio", 
                           all_dishes=all_dishes, meal_types=MealType, menu=None)


@management_bp.route('/menus/edit/<int:menu_id>', methods=['GET', 'POST'])
@login_required
@role_required([UserRole.NUTRICIONISTA, UserRole.ADMIN])
def edit_menu(menu_id):
    """Exibe o formulário para editar um cardápio e processa a atualização."""
    menu = Menu.query.get_or_404(menu_id)

    if request.method == 'POST':
        menu.date = datetime.strptime(request.form.get('date'), '%Y-%m-%d').date()
        menu.meal_type = MealType[request.form.get('meal_type')]
        dish_ids = request.form.getlist('dishes')

        if not dish_ids:
            flash('Um cardápio deve ter ao menos um prato.', 'danger')
        else:
            # Atualiza a relação many-to-many.
            # 1. Limpa a lista de pratos atual.
            menu.dishes.clear()
            # 2. Busca os novos pratos selecionados.
            selected_dishes = Dish.query.filter(Dish.id.in_(dish_ids)).all()
            # 3. Adiciona os novos pratos à lista.
            menu.dishes.extend(selected_dishes)

            db.session.commit()
            flash('Cardápio atualizado com sucesso!', 'success')
            return redirect(url_for('management.list_menus'))

    # Para requisições GET, envia os dados para o formulário.
    # Precisamos enviar todos os pratos para renderizar os checkboxes,
    # e o 'menu' atual para preencher os campos e marcar os checkboxes corretos.
    all_dishes = Dish.query.order_by(Dish.name).all()
    return render_template('management/menu_form.html', form_title="Editar Cardápio", 
                           all_dishes=all_dishes, meal_types=MealType, menu=menu)


@management_bp.route('/menus/delete/<int:menu_id>', methods=['POST'])
@login_required
@role_required([UserRole.NUTRICIONISTA, UserRole.ADMIN])
def delete_menu(menu_id):
    """Deleta um cardápio do banco de dados."""
    menu = Menu.query.get_or_404(menu_id)

    # Validação futura: verificar se o cardápio possui reservas antes de deletar.
    # if menu.reservations:
    #     flash('Este cardápio não pode ser removido, pois possui reservas associadas.', 'danger')
    #     return redirect(url_for('management.list_menus'))

    db.session.delete(menu)
    db.session.commit()
    flash('Cardápio removido com sucesso!', 'success')
    return redirect(url_for('management.list_menus'))