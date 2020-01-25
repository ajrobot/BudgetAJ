from flask import render_template, url_for, flash, redirect, request, Blueprint, Markup
from flask_login import login_user, current_user, logout_user, login_required
from budget_aj_app import db
from budget_aj_app.models import User, Income, Budget, UserSelect, Expenses
from budget_aj_app.users.forms import UserCreateForm, LoginForm, IncomeForm, AddExpensesForm, AddBudgetForm, \
    BudgetSelectForm, BudgetDeleteForm, EditBudgetForm, EditExpensesForm, EditIncomeForm, ExpenseDeleteForm, IncomeDeleteForm, EditProfileForm
from plotly.offline import plot
import plotly.graph_objects as go
from datetime import datetime, date
from sqlalchemy.sql import func, extract

users = Blueprint('users', __name__)


@users.route('/create', methods=['GET', 'POST'])
def create_user():
    form = UserCreateForm()
    if form.validate_on_submit():
        user = User(email=form.email.data,
                    user_name=form.user_name.data,
                    password=form.password.data)

        db.session.add(user)
        db.session.commit()
        flash('Thanks for register. Now you can log in and manage your budget!')
        return redirect(url_for('users.login'))

    return render_template('create_account.html', form=form)


@users.route('/login', methods=['GET', 'POST'])
def login():

    form = LoginForm()

    if form.validate_on_submit():

        user = User.query.filter_by(email=form.user_login_id.data).first()

        if user is not None and user.check_password(form.login_password.data):

            login_user(user)
            flash('Logged in successfully.')

            next_page = request.args.get('next')

            if next_page is None or not next_page[0] == '/':
                next_page = url_for('users.user_dashboard')

            return redirect(next_page)
        else:
            flash('Unsuccessful login, you entered wrong user id or password !!')
    return render_template('login.html', form=form)


@users.route('/dashboard', methods=['GET', 'POST'])
@login_required
def user_dashboard():
    pie = create_pie()
    bar = create_bar()
    expenses_tab = expenses_table()
    select_budget = BudgetSelectForm(select_budget=selected_budget())
    delete_budget = BudgetDeleteForm()
    budgets_available = Budget.query.filter_by(user_id=current_user.id).all()
    select_budget.select_budget.choices = [(0, "")]+[(budget.id, budget.budget_name) for budget in budgets_available]
    if select_budget.submit1.data and select_budget.validate():
        if select_budget.select_budget.data != 0:
            the_select = select_budget.select_budget.data
            selected_budget(the_select)
            flash('Your budget selection has been changed')
            return redirect(url_for('users.user_dashboard'))
        else:
            flash("This Isn't a valid budget selection!!")
            selected_budget()
            return redirect(url_for('users.user_dashboard'))
    if delete_budget.submit2.data and delete_budget.validate():
        if selected_budget() != 0:
            budget_deleter()
            flash('Your budget has been deleted!')
            return redirect(url_for('users.user_dashboard'))
        else:
            flash("Select the budget that you want to delete?")
    return render_template('user_dashboard.html', pie_div=Markup(pie), bar_div=Markup(bar),
                           expenses_tab=Markup(expenses_tab), budget_select_form=select_budget, budget_delete_form=delete_budget)


@users.route('/profile', methods=['GET', 'POST'])
@login_required
def user_profile():
    user = User.query.filter_by(id=current_user.id).first()
    form = EditProfileForm()
    form.current_user_name.render_kw = {"placeholder": str(user.user_name)}
    form.current_email.render_kw = {"placeholder": str(user.email)}
    if form.validate_on_submit():
        for field in form:
            if field.data and field.data != 0 and not str(field.data).isspace() and not str(field.data) == "":
                if field.name == 'password':
                    user.password_hash = user.hash_password(form.password.data)
                else:
                    setattr(user, field.name, field.data)
        db.session.commit()
        flash('Thanks, your profile has been updated!!')
        return redirect(url_for('users.user_profile'))
    return render_template('user_profile.html', form=form)


@users.route('/budget', methods=['GET', 'POST'])
@login_required
def create_budget():
    budget_form = AddBudgetForm()
    income_form = IncomeForm()
    income_tab = incomes_table()
    budget_tab = budgets_table()
    expenses_tab = expenses_table()
    form = AddExpensesForm()
    form.category.choices = category_choice()
    form.due_date.choices = [(0, "")]+[(i, str(i)) for i in range(1, 29)]

    if budget_form.validate_on_submit():
        budget = Budget(user_id=current_user.id,
                        budget_name=budget_form.budget_name.data,
                        budget_description=budget_form.budget_description.data)
        db.session.add(budget)
        db.session.commit()
        if UserSelect.query.filter_by(user_id=current_user.id).first() is None:
            select_user = UserSelect(user_id=current_user.id, selected_budget_id=budget.id)
            db.session.add(select_user)
            db.session.commit()
        else:
            selected_budget(budget.id)
        flash('Thanks for Creating new budget!')
        return redirect(url_for('users.create_budget'))

    if income_form.validate_on_submit():
        if selected_budget() != 0:
            print(selected_budget())
            income = Income(budget_id=selected_budget(),
                            income_amount_month=income_form.income_amount_month.data,
                            income_description=income_form.income_description.data,
                            income_tax=income_form.income_tax.data)
            db.session.add(income)
            db.session.commit()
            flash('Income added to the budget!')
            return redirect(url_for('users.create_budget'))
        elif selected_budget() == 0:
            flash('Please select your budget and filling all the required fields.!!')


    if form.validate_on_submit():
        if selected_budget() != 0:
            print(selected_budget())
            expenses = Expenses(budget_id=selected_budget(),
                                expense_description=form.expense_description.data,
                                expense_amount=form.expense_amount.data,
                                category=form.category.data,
                                expense_type=form.expense_type.data,
                                transaction_date=form.transaction_date.data,
                                due_date=form.due_date.data)
            db.session.add(expenses)
            db.session.commit()
            return redirect(url_for('users.create_budget'))
        elif selected_budget() == 0:
            flash('Please select your budget and filling all the required fields.!!')

    return render_template('create_budget.html', budget_form=budget_form, income_form=income_form, form=form, expenses_tab=Markup(expenses_tab),
                           income_tab=Markup(income_tab), budget_tab=Markup(budget_tab))


@users.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('core.index'))


@users.route('/edit', methods=['GET', 'POST'])
@login_required
def edit_budget():

    edit_budget_form = EditBudgetForm()
    edit_income_form = EditIncomeForm()
    edit_expense_form = EditExpensesForm()
    delete_income_form = IncomeDeleteForm()
    delete_expense_form = ExpenseDeleteForm()


    incomes_available = Income.query.filter_by(budget_id=selected_budget()).all()
    edit_income_form.select_income.choices = [(0, "")] + [(income.id, income.id) for income in incomes_available]
    delete_income_form.select_income.choices = [(0, "")] + [(income.id, income.id) for income in incomes_available]
    expenses_available = Expenses.query.filter_by(budget_id=selected_budget()).all()
    edit_expense_form.select_expense.choices = [(0, "")] + [(expense.id, expense.id) for expense in expenses_available]
    delete_expense_form.select_expense.choices = [(0, "")] + [(expense.id, expense.id) for expense in expenses_available]
    edit_expense_form.category.choices = category_choice()
    edit_expense_form.due_date.choices = [(0, "")]+[(i, str(i)) for i in range(1, 29)]

    income_tab = incomes_table()
    budget_tab = budgets_table()
    expenses_tab = expenses_table()

    if edit_budget_form.edit_budget_submit.data and edit_budget_form.validate():
        budget = Budget.query.filter_by(id=selected_budget()).first()
        budget.budget_name = edit_budget_form.budget_name.data
        budget.budget_description = edit_budget_form.budget_description.data
        db.session.commit()
        flash(f'Budget with Id {selected_budget()} has been edited')
        return redirect(url_for('users.edit_budget'))

    if delete_income_form.income_delete_submit.data and delete_income_form.validate():
        if delete_income_form.select_income != 0:
            Income.query.filter_by(id=edit_income_form.select_income.data).delete()
            db.session.commit()
            flash(f'Income with Id {edit_income_form.select_income.data} has been deleted')
            return redirect(url_for('users.edit_budget'))
        else:
            flash('Please select income Id for the income you trying to delete!')

    if edit_income_form.edit_income_submit.data and edit_income_form.validate():
        if edit_income_form.select_income != 0:
            income = Income.query.filter_by(id=edit_income_form.select_income.data).first()
            income.income_amount_month = edit_income_form.income_amount_month.data
            income.income_description = edit_income_form.income_description.data
            income.income_tax = edit_income_form.income_tax.data
            db.session.commit()
            flash(f'Income with Id {edit_income_form.select_income.data} has been edited')
            return redirect(url_for('users.edit_budget'))
        else:
            flash('Please select income Id for the income you trying to delete!')

    if delete_expense_form.expense_delete_submit.data and delete_expense_form.validate():
        if delete_expense_form.select_expense.data != 0:
            Expenses.query.filter_by(id=delete_expense_form.select_expense.data).delete()
            db.session.commit()
            flash(f'Expense with Id {delete_expense_form.select_expense.data} has been deleted')
            return redirect(url_for('users.edit_budget'))
        else:
            flash('Please select expense Id for the expense you trying to delete!')

    if edit_expense_form.edit_expenses_submit.data and edit_expense_form.validate():
        if edit_expense_form.select_expense.data != 0:
            expense = Expenses.query.filter_by(id=edit_expense_form.select_expense.data).first()
            for field in edit_expense_form:
                if field.data and field.data != 0 and not str(field.data).isspace() and not str(field.data) == "":
                    setattr(expense, field.name, field.data)


            db.session.commit()
            flash(f'Expense with Id {edit_expense_form.select_expense.data} has been edited')
            return redirect(url_for('users.edit_budget'))
        else:
            flash('Please select expense Id for the expense you trying to edit!')

    return render_template('edit_budget.html', edit_budget_form=edit_budget_form, edit_income_form=edit_income_form,
                           delete_income_form=delete_income_form, edit_expense_form=edit_expense_form,
                           delete_expense_form=delete_expense_form, expenses_tab=Markup(expenses_tab),
                           income_tab=Markup(income_tab), budget_tab=Markup(budget_tab))


@users.route('/expenses', methods=['GET', 'POST'])
@login_required
def add_expenses():
    expenses_tab = expenses_table()
    form = AddExpensesForm()
    form.category.choices = category_choice()
    form.due_date.choices = [(i, str(i))for i in range(1, 29)]
    if form.validate_on_submit():
        if selected_budget() != 0:
            print(selected_budget())
            expenses = Expenses(budget_id=selected_budget(),
                                expense_description=form.expense_description.data,
                                expense_amount=form.expense_amount.data,
                                category=form.category.data,
                                expense_type=form.expense_type.data,
                                transaction_date=form.transaction_date.data,
                                due_date=form.due_date.data)
            db.session.add(expenses)
            db.session.commit()
            return redirect(url_for('users.add_expenses'))
        elif selected_budget() == 0:
            flash('Please select your budget and filling all the required fields.!!')
    return render_template('add_expenses.html', form=form, expenses_tab=Markup(expenses_tab))


@users.route('/bills', methods=['GET', 'POST'])
@login_required
def show_bills():
    income_tab = incomes_table()
    return render_template('user_bill.html', income_tab=Markup(income_tab))


def create_pie():
    labels = []
    values = []
    for key, val in total_expenses_category().items():
        labels.append(key)
        values.append(val)

    # pull is given as a fraction of the pie radius
    my_plot_div = plot([go.Pie(labels=labels, values=values, hole=.3)], output_type='div')
    return my_plot_div


def create_bar():
    expenses_bars = []
    months = []
    income_bars = []
    total_income = Income.query.with_entities(func.sum(Income.income_amount_month)). \
        filter_by(budget_id=selected_budget()).first()
    for i in total_expenses_month():
        expenses_bars.append(i[0])
        income_bars.append(total_income[0])
        months.append(f"{i[1]}-{i[2]}")
    fig = plot(
        [go.Bar(
            x=months,
            y=income_bars,
            name='Total Income',
            marker_color='#5fbae9'
        ),
            go.Bar(
                x=months,
                y=expenses_bars,
                name='Total Spend',
                marker_color='red'
            )], output_type='div')
    return fig


def budgets_table():
    budgets = Budget.query.filter_by(user_id=current_user.id).all()
    budget_description = []
    budget_name = []
    budget_selected = []
    if budgets:
        for budget in budgets:
            if budget.id == selected_budget():
                budget_selected.append("*")
            else:
                budget_selected.append("")
            budget_name.append(budget.budget_name)
            budget_description.append(budget.budget_description)

    fig = plot([go.Table(columnorder=[1, 2, 3],
                         columnwidth=[20, 40, 90],
                         header=dict(values=['Selected', 'Budget Name', 'Budget Description'],
                                     fill_color='#39ace7',
                                     font=dict(color='white', size=12),
                                     align='center'),
                         cells=dict(values=[budget_selected, budget_name, budget_description],
                                    fill_color='lightcyan',
                                    align='center'))], output_type='div')



    return fig


def incomes_table():
    incomes = Income.query.filter_by(budget_id=selected_budget()).all()
    income_id = []
    income_description = []
    amount_before = []
    amount_after = []
    income_tax = []
    if incomes:
        for income in incomes:
            income_id.append(income.id)
            income_description.append(income.income_description)
            amount_before.append(round(income.income_amount_month, 2))
            amount_after.append(round(income.income_amount_month - income.income_amount_month * (income.income_tax / 100), 2))
            income_tax.append(income.income_tax)
    fig = plot([go.Table(columnorder=[1, 2, 3, 4, 5],
                         columnwidth=[35, 60, 55, 25, 80],
        header=dict(values=['Income Id', 'Amount Before Tax', 'Amount After Tax', 'Tax %', 'Income Description'],
                    fill_color='#39ace7',
                    font=dict(color='white', size=12),
                    align='center'),
        cells=dict(values=[income_id, amount_before, amount_after, income_tax, income_description],
                   fill_color='lightcyan',
                   align='center'))], output_type='div')

    return fig


def expenses_table():
    expenses = Expenses.query.filter_by(budget_id=selected_budget()).all()
    expenses_description = []
    categories = []
    expenses_amount = []
    transaction_dates = []
    due_dates_list = []
    reports = []
    if expenses:
        for expense in expenses:
            expenses_description.append(expense.expense_description)
            categories.append(category_choice(expense.category))
            expenses_amount.append(round(expense.expense_amount, 2))
            transaction_dates.append(expense.transaction_date.strftime('%m/%d/%Y'))
            due_date = expense.due_date if expense.due_date is not None and expense.due_date != 0 else ""
            due_dates_list.append(due_date)
            reports.append(due_dates(expense.due_date))
    fig = plot([go.Table(columnorder=[1, 2, 3, 4, 5, 6],
                         columnwidth=[80, 50, 40, 50, 35, 90],
                         header=dict(values=['Description', 'Category', 'Amount', 'Transaction', 'Due', 'Reports'],
                                     fill_color='#39ace7',
                                     font=dict(color='white', size=12),
                                     #fill=dict(color=['#39ace7', 'white']),
                                     align='center'),
                         cells=dict(values=[expenses_description, categories, expenses_amount, transaction_dates,
                                            due_dates_list, reports],
                                    fill_color='lightcyan',
                                    align='center'))], output_type='div')

    return fig


def due_dates(due_day):
    if due_day and due_day != 0:
        current_day = datetime.now().day
        current_month = datetime.now().month
        current_year = datetime.now().year
        current_date = date(current_year, current_month, current_day)
        due_date = date(current_year, current_month, due_day)
        delta = due_date - current_date
        if delta.days < 5 and delta.days >= 0:
            return f"This Bill will due in {delta.days} day/s !!"
        elif delta.days < 0 and delta.days > -3:
            return f"This Bill is passed due date form {delta.days} day/s !!"
        else:
            return ""
    else:
        return ""


def selected_budget(select=None):

    select_user = UserSelect.query.filter_by(user_id=current_user.id).first()
    if select is not None:
        if select_user:
            select_user.selected_budget_id = select
            db.session.commit()
            return select_user.selected_budget_id
        else:
            return 0
    elif select_user:
        return select_user.selected_budget_id
    else:
        return 0


def category_choice(choice=None):
    choices = [("", ""), ('shopping', "Shopping"), ('housing', 'Housing'), ('utility', 'Utility'), ('insurance', 'Insurance'),
               ('medical', 'Medical'), ('transportation', 'Transportation'),
               ('investing_debt', 'Saving, Investing, or Debt'),
               ('other', 'Other Expense')]
    if choice:
        choice_list = [x for x in choices if x[0] == choice]
        if choice_list:
            return choice_list[0][1]
        else:
            return ""
    else:
        return choices


def total_expenses_category():
    total_category = {}
    for cat in category_choice():
        expenses = Expenses.query.with_entities(func.sum(Expenses.expense_amount).label('expenses_by_cat')).\
            filter(Expenses.budget_id == selected_budget()).filter(Expenses.category == cat[0]).\
            filter(extract('year', Expenses.transaction_date) == datetime.now().year,
                   extract('month', Expenses.transaction_date) == datetime.now().month).first()
        if expenses[0]:
            total_category[cat[1]] = expenses[0]
    if len(total_category) > 0:
        return total_category
    else:
        return {"ex1": 5, 'ex2': 10, 'ex3': 3}


def total_expenses_month():

    # expenses = Expenses.query.with_entities(func.sum(Expenses.expense_amount).label('total_month')). \
    #     filter(Expenses.budget_id == selected_budget()).\
    #     group_by(extract('year', Expenses.creation_date),
    #            extract('month', Expenses.creation_date)).first()

    mendObj = Expenses.query.with_entities(func.sum(Expenses.expense_amount).label('Amount'),
                               extract('year', Expenses.transaction_date),
                               extract('month', Expenses.transaction_date)). \
        group_by(extract('year', Expenses.transaction_date),
                 extract('month', Expenses.transaction_date)). \
        all()


    #total_income_month = Income.query.with_entities(func.sum(Income.income_amount_month).label('total_inc')). \
            #filter(Expenses.budget_id == selected_budget()).first()
    return mendObj
    #if total_income_month:
     #   return total_income_month
    #else:
      #  return 0


def budget_deleter():
    Budget.query.filter_by(id=selected_budget()).delete()
    Income.query.filter_by(budget_id=selected_budget()).delete()
    Expenses.query.filter_by(budget_id=selected_budget()).delete()
    select_user = UserSelect.query.filter_by(user_id=current_user.id).first()
    select_user.selected_budget_id = 0
    db.session.commit()










