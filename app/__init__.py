from flask import Flask, jsonify
from flask_cors import CORS
from sqlalchemy import text
from .extensions import db, migrate, jwt
from .config import Config

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)           
    CORS(app, resources={r"/*": {"origins": app.config["CORS_ORIGINS"]}})

    @app.get("/")
    def home():
        return jsonify({"service": "AI Expense Tracker API", "status": "ok"}), 200

    @app.get("/health")
    def health():
        try:
            db.session.execute(text("SELECT 1"))
            return jsonify({"status": "healthy", "database": "ok"}), 200
        except Exception:
            db.session.rollback()
            return jsonify({"status": "unhealthy", "database": "unavailable"}), 503

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

