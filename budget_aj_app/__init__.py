################################################
# __init__.py in budget_aj_app
################################################
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate


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