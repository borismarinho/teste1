from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager

#site = app
app = Flask(__name__)
app.config['SECRET_KEY'] = '48bf3f8c58c8bc17b625fe42054af04b'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///Concord.db'

database = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'criar_conta'
login_manager.login_message_category = 'alert-info'

from concord import routes

