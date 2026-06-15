from flask import Flask
from .extensions import db, migrate, jwt
from .config import Config

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)           

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)

    from app.models.user import User
    from app.models.expense import Expense 

    from app.routes.auth import auth         
    app.register_blueprint(auth)              

    from app.routes.expenses import expenses
    app.register_blueprint(expenses)          

    from app.routes.receipts import receipts
    app.register_blueprint(receipts)

    from app.routes.insights import insights
    app.register_blueprint(insights)

    return app

