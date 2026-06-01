#The key thing here is Blueprint. This is how Flask organises routes across multiple files.
from flask import Blueprint, request,jsonify
from app.extensions import db
from app.models.expense import Expense
import bcrypt
from flask_jwt_extended import jwt_required,get_jwt_identity

expenses= Blueprint("expenses", __name__)

@expenses.route("/expenses",methods=["POST"])
@jwt_required()
def add_expense():
    data=request.get_json()
    user_id=get_jwt_identity()

    if not data.get("amount") or not data.get("category"):
        return jsonify({"error":"Amount and category are required "}),400
    

    new_expense = Expense(
        amount=data["amount"],
        category=data["category"],
        user_id=user_id
    )
    db.session.add(new_expense)
    db.session.commit()

    return jsonify({"message": "expense added", "expense": new_expense.to_dict()}), 201


@expenses.route("/expenses", methods=["GET"])
@jwt_required()
def get_expenses():
    user_id = get_jwt_identity()
    expenses_list = Expense.query.filter_by(user_id=user_id).all()
    return jsonify([e.to_dict() for e in expenses_list]), 200


@expenses.route("/expense/<int:expense_id>",methods=["DELETE"])
@jwt_required()
def delete_expense(expense_id):
    user_id=get_jwt_identity()
    expense = Expense.query.filter_by(id=expense_id, user_id=user_id).first()

    if not expense:
        return jsonify({"error": "expense not found"}), 404

    db.session.delete(expense)
    db.session.commit()

    return jsonify({"message": "expense deleted"}), 200

