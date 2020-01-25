################################################
# __init__.py in budget_aj_app
################################################
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager

app = Flask(__name__)


"""""
CONFIGURATION
"""""
app.config['SECRET_KEY'] = 'thesecretkey'


"""""
DATABASE SETUP
"""""
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'data.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


db = SQLAlchemy(app)
Migrate(app, db)


"""""
LOGIN CONFIG
"""""

login_manager = LoginManager()

# We can now pass in our app to the login manager
login_manager.init_app(app)

# Tell users what view to go to when they need to login.
login_manager.login_view = "users.login"




"""""
BLUEPRINT CONFIGS
"""""
# import all views here
from budget_aj_app.core.views import core
from budget_aj_app.users.views import users


# register views blueprint
app.register_blueprint(core)
app.register_blueprint(users)
