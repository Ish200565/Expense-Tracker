#This is the actual Database file .
#  We will be using SQLAlchemy as our ORM and Flask-Migrate for database migrations.
#  We will also be using PostgreSQL as our database, so we will be using psycopg2-binary as our database adapter.
#  We will also be using Flask-JWT-Extended for authentication and Bcrypt for password hashing.
from flask import Flask
from .extensions import db,migrate 

def create_app():
     app=Flask(__name__)
     app.config["SQLALCHEMY_DATABASE_URI"]="sqlite:///notes.db"
     app.config["SQLALCHEMY_TRACK_MODIFICATIONS"]=False

     db.init_app(app)
     migrate.init_app(app,db)

     from app.routes.auth import auth #blueprint that connects routes with init 
     app.register_blueprint(auth) #registering the blueprint with the app

     return app
