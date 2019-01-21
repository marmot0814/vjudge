from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

from oj import OJ
from config import Config

import os
import json

from buffer import Buffer
from oj import OJ

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SECRET_KEY'] = 'nctuojvirtualjudge'[::-1]*3
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'app.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS '] = False
app.config['MAX_CONTENT_LENGTH'] = 1<<20
db = SQLAlchemy(app)
migrate = Migrate(app, db)


Config.load()
OJ.initial()
Buffer.initial(OJ)

login = LoginManager(app)
login.login_view = 'login'

from app import routes, models
