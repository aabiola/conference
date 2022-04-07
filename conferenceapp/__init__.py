from flask import Flask
from flask_wtf.csrf import CSRFProtect

from flask_sqlalchemy import SQLAlchemy

from flask_mail import Mail, Message

from flask_migrate import Migrate


#instantiate a Flask app
app = Flask(__name__, instance_relative_config=True)
csrf = CSRFProtect(app)


#local import starts here:
from conferenceapp import config
app.config.from_object(config.ProductionConfig)
#load below the config within instance
app.config.from_pyfile('config.py', silent=False)

db = SQLAlchemy(app)
mail = Mail(app)
migrate = Migrate(app,db)

#load the routes/views , #our routes is now separated

from conferenceapp.myroutes import adminroutes, userroutes
from conferenceapp import forms, mymodels