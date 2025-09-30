import enum
from datetime import datetime
from extensions import db
from flask_login import UserMixin # Essencial para o Flask-Login

# Usamos Enums do Python para garantir a integridade dos dados em campos específicos
class UserRole(enum.Enum):
    ESTUDANTE = 'Estudante'
    SERVIDOR = 'Servidor'
    NUTRICIONISTA = 'Nutricionista'
    FUNCIONARIO = 'Funcionário do Refeitório'
    ADMIN = 'Administrador'

class ReservationStatus(enum.Enum):
    CONFIRMADA = 'Confirmada'
    UTILIZADA = 'Utilizada'
    NAO_COMPARECEU = 'Não Compareceu'
    CANCELADA = 'Cancelada'

class MealType(enum.Enum):
    ALMOCO = 'Almoço'
    JANTA = 'Janta'

# Tabela de Associação para a relação Muitos-para-Muitos entre Menu e Dish
menu_dishes = db.Table('menu_dishes',
    db.Column('menu_id', db.Integer, db.ForeignKey('menu.id'), primary_key=True),
    db.Column('dish_id', db.Integer, db.ForeignKey('dish.id'), primary_key=True)
)

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.Enum(UserRole), nullable=False, default=UserRole.ESTUDANTE)
    
    # Atributos específicos
    is_scholarship_student = db.Column(db.Boolean, default=False) # Para [US11]
    credits = db.Column(db.Numeric(10, 2), default=0.00) # Para [US12]
    dietary_restrictions = db.Column(db.Text, nullable=True) # Para [US14]

    # Relacionamento: Um usuário pode ter várias reservas
    reservations = db.relationship('Reservation', backref='user', lazy=True)

    def __repr__(self):
        return f'<User {self.email}>'

class Dish(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=True)
    nutritional_info = db.Column(db.Text, nullable=True) # Para [US04]

    def __repr__(self):
        return f'<Dish {self.name}>'

class Menu(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    meal_type = db.Column(db.Enum(MealType), nullable=False)

    # Relacionamento Muitos-para-Muitos com Dish
    # Um cardápio (menu) é composto por vários pratos (dishes)
    dishes = db.relationship('Dish', secondary=menu_dishes, lazy='subquery',
        backref=db.backref('menus', lazy=True))
    
    # Relacionamento: Um menu pode ter várias reservas associadas
    reservations = db.relationship('Reservation', backref='menu', lazy=True)

    def __repr__(self):
        return f'<Menu {self.date.strftime("%d/%m/%Y")} - {self.meal_type.value}>'

class Reservation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    reservation_timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    status = db.Column(db.Enum(ReservationStatus), nullable=False, default=ReservationStatus.CONFIRMADA)
    
    # Chaves Estrangeiras
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    menu_id = db.Column(db.Integer, db.ForeignKey('menu.id'), nullable=False)

    def __repr__(self):
        return f'<Reservation {self.id} by User {self.user_id}>'