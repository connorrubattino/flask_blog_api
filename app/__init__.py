from flask import Flask # Import the Flask class from the flask module
from flask_sqlalchemy import SQLAlchemy #import database
from config import Config


# Create an instance of Flask called app which will be the central object
app = Flask(__name__)

#set the configuration for the app
app.config.from_object(Config)

#create an instance of SQLAlchemy called db which will be the central object for our database
db = SQLAlchemy(app)

#import the routes to the app -- need this below the app or else will cause circular import because when it goes over to routes to look for app, app will not yet be defined
from . import routes
