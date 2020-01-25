from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, FloatField, SelectField, DateField
from wtforms.fields.html5 import DateTimeLocalField
from wtforms.validators import DataRequired, Email, EqualTo, Optional, StopValidation, InputRequired
from wtforms import ValidationError
from flask_wtf.file import FileField, FileAllowed
from budget_aj_app.models import User, Income, Budget
from budget_aj_app.users import views
from wtforms.fields.html5 import DateField


class LoginForm(FlaskForm):
    user_login_id = StringField(validators=[DataRequired()])
    login_password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Log In')


class UserCreateForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    user_name = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired(), EqualTo('pass_confirm', message='Passwords Must Match!')])
    pass_confirm = PasswordField('Confirm password', validators=[DataRequired()])
    submit = SubmitField('Create')

    def validate_email(self, field):
        # Check if not None for that user email!
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Your email has been registered already!')

    def validate_username(self, field):
        # Check if not None for that username!
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('Sorry, that username is taken!')


class EditProfileForm(FlaskForm):
    current_email = StringField('Email')
    email = StringField('Email', validators=[Email(), Optional(strip_whitespace=True)])
    current_user_name = StringField('Username')
    user_name = StringField('Username', validators=[Optional(strip_whitespace=True)])
    password = PasswordField('Password', validators=[EqualTo('pass_confirm', message='Passwords Must Match!')])
    pass_confirm = PasswordField('Confirm password')
    submit = SubmitField('Edit')

    def validate_email(self, field):
        # Check if not None for that user email!
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Your email has been registered already!')

    def validate_username(self, field):
        # Check if not None for that username!
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('Sorry, that username is taken!')



class AddBudgetForm(FlaskForm):
    budget_name = StringField('Budget Name', validators=[DataRequired()])
    budget_description = StringField('Budget Description')
    submit = SubmitField('Create')


class BudgetSelectForm(FlaskForm):
    select_budget = SelectField("Select Budget", coerce=int)
    submit1 = SubmitField("Select")


class IncomeForm(FlaskForm):
    income_description = StringField('Income Description', validators=[DataRequired()])
    pay_period = SelectField('Pay Period', choices=[('semi-monthly', ""), ('weekly', 'weekly'),
    ('bi-weekly', 'bi-weekly(every other week)'), ('semi-monthly', 'semi-monthly(twice a month)'),
    ('monthly', 'monthly')], validators=[DataRequired()])
    income_amount_month = FloatField('Amount', validators=[DataRequired()])
    income_tax = FloatField('Tax')
    submit = SubmitField('Add Income')


class RequiredIf(object):
    # a validator which makes a field required if
    # another field is set and has a truthy value

    def __init__(self, other_field_name, *args, **kwargs):
        self.other_field_name = other_field_name
        super(RequiredIf, self).__init__(*args, **kwargs)

    def __call__(self, form, field):
        other_field = form._fields.get(self.other_field_name)
        if other_field.data == 'month_bill':
            field.validators.insert(1, DataRequired())



class AddExpensesForm(FlaskForm):
    expense_description = StringField('Expense Description', validators=[DataRequired()])
    category = SelectField('Expense Category', validators=[DataRequired()])
    expense_type = SelectField('Expense Type', choices=[("", ""), ('one', 'One Time'), ('month_bill', 'Monthly Bill')],
                               validators=[DataRequired()])
    expense_amount = FloatField('Amount', validators=[DataRequired()])
    due_date = SelectField('Due Day', coerce=int, validators=[RequiredIf('expense_type')])
    transaction_date = DateField('Transaction Date', format='%Y-%m-%d')
    submit = SubmitField('Add Expense')


class EditBudgetForm(FlaskForm):
    budget_name = StringField('Budget Name', validators=[DataRequired()])
    budget_description = StringField('Budget Description')
    edit_budget_submit = SubmitField('Edit')


class EditIncomeForm(FlaskForm):
    income_description = StringField('Income Description', validators=[DataRequired()])
    pay_period = SelectField('Pay Period', choices=[('semi-monthly', ""), ('weekly', 'weekly'),
    ('bi-weekly', 'bi-weekly(every other week)'), ('semi-monthly', 'semi-monthly(twice a month)'),
    ('monthly', 'monthly')], validators=[DataRequired()])
    income_amount_month = FloatField('Amount', validators=[DataRequired()])
    income_tax = FloatField('Tax', validators=[DataRequired()])
    select_income = SelectField("Income Id", coerce=int, validators=[DataRequired()])
    edit_income_submit = SubmitField('Edit Income')






class EditExpensesForm(FlaskForm):
    select_expense = SelectField("Expense Id", coerce=int, validators=[InputRequired()])
    expense_description = StringField('Expense Description')
    category = SelectField('Expense Category', validators=[Optional(strip_whitespace=True)])
    expense_type = SelectField('Expense Type', choices=[('', ''), ('one', 'One Time'), ('month_bill', 'Monthly Bill')], validators=[Optional(strip_whitespace=True)])
    expense_amount = FloatField('Amount', validators=[Optional(strip_whitespace=True)])
    due_date = SelectField('Due Day', coerce=int, validators=[RequiredIf('expense_type')])
    transaction_date = DateField('Transaction Date', format='%Y-%m-%d', validators=[Optional(strip_whitespace=True)])

    edit_expenses_submit = SubmitField('Edit Expense')


class BudgetDeleteForm(FlaskForm):
    submit2 = SubmitField("Delete Budget")


class IncomeDeleteForm(FlaskForm):
    select_income = SelectField("Income Id", coerce=int, validators=[DataRequired()])
    income_delete_submit = SubmitField("Delete Income")


class ExpenseDeleteForm(FlaskForm):
    select_expense = SelectField("Expense Id", coerce=int, validators=[DataRequired()])
    expense_delete_submit = SubmitField("Delete Expense")


def make_optional(fields):
    for field in fields:
        field.validators.insert(0, Optional())


def make_optional2(fields):
    for field in fields:
        field.validators.insert(0, Optional())


