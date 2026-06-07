from flask import Flask
from .extensions import db, migrate, jwt
from .config import Config

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)           #loading the config file

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)

    from app.models.user import User
    from app.models.expense import Expense 

    from app.routes.auth import auth          #blueprint that connects routes with init 
    app.register_blueprint(auth)              #registering the blueprint with the app

    from app.routes.expenses import expenses
    app.register_blueprint(expenses)          

    from app.routes.receipts import receipts
    app.register_blueprint(receipts)

    return app

