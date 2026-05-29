#this file is used to initialize the extensions that we will be using in our application.
#  We will import the extensions and initialize them here, 
# so that we can use them in our application without having to import them in every file.
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

db=SQLAlchemy()
migrate=Migrate()
