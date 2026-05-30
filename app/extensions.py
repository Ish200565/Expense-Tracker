#this file is used to initialize the extensions that we will be using in our application.
#  We will import the extensions and initialize them here, 
# so that we can use them in our application without having to import them in every file.
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager


db=SQLAlchemy()
migrate=Migrate()
jwt=JWTManager()
