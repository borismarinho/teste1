from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager

app = Flask(__name__)

app.config['SECRET_KEY'] = '5827213f2db869a56ffe319b09db2d94'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///leposticho.db'

database = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_menager = LoginManager(app)
login_menager.login_view = 'login'
login_menager.login_message_category = 'alert-info'

from leposticheBI import routes
