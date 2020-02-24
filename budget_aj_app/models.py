from budget_aj_app import db,login_manager
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from sqlalchemy.orm import backref


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


class User(db.Model, UserMixin):

    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), unique=True, index=True)
    user_name = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    creation_date = db.Column(db.DateTime, nullable=False,
                              default=datetime.utcnow(), onupdate=datetime.utcnow())
    budgets = db.relationship('Budget', backref='user', lazy=True, passive_deletes=True)
    budgets_selection = db.relationship('UserSelect', uselist=False, backref='user', cascade="all, delete, delete-orphan")

    def __init__(self, email, user_name, password):
        self.email = email
        self.user_name = user_name
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def hash_password(self, password):
        return generate_password_hash(password)


    def __repr__(self):
        return f"UserName: {self.user_name}"


class Budget(db.Model, UserMixin):

    __tablename__ = 'budget'

    id = db.Column(db.Integer, primary_key=True)
    budget_name = db.Column(db.String(64))
    budget_description = db.Column(db.String(128))
    creation_date = db.Column(db.DateTime, nullable=False,
                              default=datetime.utcnow(), onupdate=datetime.utcnow())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    incomes = db.relationship('Income', backref='budget', lazy=True, passive_deletes=True)
    expenses = db.relationship('Expenses', backref='budget', lazy=True, passive_deletes=True)

    def __init__(self, user_id, budget_name, budget_description=""):
        self.budget_name = budget_name
        self.budget_description = budget_description
        self.user_id = user_id

    def get_id(self):
        return self.id

    def __repr__(self):
        return f"New Budget has been added: {self.budget_name}."


class UserSelect(db.Model, UserMixin):

    __tablename__ = 'user_select'

    id = db.Column(db.Integer, primary_key=True)
    selected_budget_id = db.Column(db.Integer, nullable=False, default=0)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False, unique=True)

    def __init__(self, user_id, selected_budget_id=0):
        self.user_id = user_id
        self.selected_budget_id = selected_budget_id

    def __repr__(self):
        return f"Budget you selected is: {Budget.query.filter_by(id=self.selected_budget_id).first()}."


class Income(db.Model, UserMixin):

    __tablename__ = 'income'

    id = db.Column(db.Integer, primary_key=True)
    income_amount_month = db.Column(db.Float, nullable=False)
    income_description = db.Column(db.String(64), nullable=False)
    income_tax = db.Column(db.Float, default=0)
    creation_date = db.Column(db.DateTime, nullable=False,
                              default=datetime.utcnow(), onupdate=datetime.utcnow())
    budget_id = db.Column(db.Integer, db.ForeignKey('budget.id', ondelete='CASCADE'), nullable=False)

    def __init__(self, budget_id, income_amount_month, income_description, income_tax):
        self.budget_id = budget_id
        self.income_amount_month = income_amount_month
        self.income_description = income_description
        self.income_tax = income_tax

    def __repr__(self):
        return f"New income added to the budget.."


class Expenses(db.Model, UserMixin):

    __tablename__ = 'expenses'

    id = db.Column(db.Integer, primary_key=True)
    expense_description = db.Column(db.String(128), nullable=False)
    expense_amount = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(64), nullable=False)
    expense_type = db.Column(db.String(32), nullable=False)
    due_date = db.Column(db.DateTime, nullable=True)
    transaction_date = db.Column(db.DateTime, nullable=False)
    creation_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow(), onupdate=datetime.utcnow())
    budget_id = db.Column(db.Integer, db.ForeignKey('budget.id', ondelete='CASCADE'), nullable=False)

    def __init__(self, budget_id, expense_description, expense_amount, category, expense_type, transaction_date, due_date=None):
        self.budget_id = budget_id
        self.expense_description = expense_description
        self.expense_amount = expense_amount
        self.category = category
        self.expense_type = expense_type
        self.transaction_date = transaction_date
        self.due_date = due_date

    def __repr__(self):
        return f"New Expense has been added to the budget.."
