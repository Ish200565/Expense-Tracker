#The key thing here is Blueprint. This is how Flask organises routes across multiple files.
from flask import Blueprint, request,jsonify
from app.extensions import db
from app.models.user import User
import bcrypt
from flask_jwt_extended import create_access_token

auth= Blueprint("auth", __name__)


@auth.route("/register",methods=["POST"])
def register():
            data=request.get_json()

            if not data.get("email") or not data.get("password"):
                return jsonify({"error": "email and password required"}), 400

            if User.query.filter_by(email=data["email"]).first():
                return jsonify({"error": "email already exists"}), 400


            hashed=bcrypt.hashpw(
                   data["password"].encode("utf-8"), 
                   bcrypt.gensalt()
            )
            user = User(email=data["email"], password=hashed.decode("utf-8"))
            db.session.add(user)
            db.session.commit()

            return jsonify({"message": "user created successfully"}), 201




@auth.route("/login",methods=["POST"])
def login():
            data=request.get_json()


            user = User.query.filter_by(email=data["email"]).first()

            if not user:
                return jsonify({"error": "invalid email or password"}), 401

            if not bcrypt.checkpw(
                   data["password"].encode("utf-8"), 
                   user.password.encode("utf-8")):

                return jsonify({"error": "invalid email or password"}), 401
            
            token = create_access_token(identity=str(user.id))
            return jsonify({"access_token": token}), 200