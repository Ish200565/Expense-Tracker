from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.extensions import db
from app.models.expense import Expense

expenses = Blueprint("expenses", __name__)

@expenses.route("/expenses", methods=["GET"])
@jwt_required()
def get_expenses():
    user_id = int(get_jwt_identity())

    expenses_list = Expense.query.filter_by(user_id=user_id).all()

    return jsonify([e.to_dict() for e in expenses_list]), 200

@expenses.route("/expenses", methods=["POST"])
@jwt_required()
def add_expense():
    data = request.get_json()
    user_id = int(get_jwt_identity())
    amount = data.get("amount")       
    category = data.get("category")
    description = data.get("description", "")

    if amount is None or category is None:
        return jsonify({"error": "Amount and category are required"}), 400
    if not isinstance(amount, (int, float)):
        return jsonify({"error": "Amount should be a number"}), 400
    if amount <= 0:
        return jsonify({"error": "Amount must be greater than zero"}), 400
    if not category.strip():
        return jsonify({"error": "Category cannot be empty"}), 400

    new_expense = Expense(
        amount=amount,
        category=category,
        description=description,
        user_id=user_id
        
    )
    db.session.add(new_expense)
    db.session.commit()

    from app.services.rag_service import store_expense
    store_expense(new_expense)
    
    return jsonify({"message": "expense added", "expense": new_expense.to_dict()}), 201

@expenses.route("/expenses/<int:expense_id>", methods=["PATCH"])
@jwt_required()
def update_expenses_list(expense_id):
    user_id = int(get_jwt_identity())
    data = request.get_json()

    expense = Expense.query.filter_by(id=expense_id, user_id=user_id).first()
    if not expense:
        return jsonify({"error": "Expense not found"}), 404
    
    if "amount" in data:
        amount = data["amount"]
        if not isinstance(amount, (int, float)):
            return jsonify({"error": "Amount should be a number"}), 400
        if amount <= 0:
            return jsonify({"error": "Amount must be greater than zero"}), 400
        expense.amount = amount
        
    if "category" in data:
        category = data["category"]
        if not category.strip():
            return jsonify({"error": "Category cannot be empty"}), 400
        expense.category = category

    db.session.commit()

    return jsonify({"message": "EXPENSE UPDATED", "expense": expense.to_dict()}), 200

@expenses.route("/expenses/<int:expense_id>", methods=["DELETE"])
@jwt_required()
def delete_expense(expense_id):
    user_id = int(get_jwt_identity())

    expense = Expense.query.filter_by(id=expense_id, user_id=user_id).first()
    if not expense:
        return jsonify({"error": "expense not found"}), 404

    db.session.delete(expense)
    db.session.commit()

    return jsonify({"message": "expense deleted"}), 200

@expenses.route("/expenses/category/<string:category>", methods=["GET"])
@jwt_required()
def get_exepenses_by_category(category):
    user_id = int(get_jwt_identity())

    expense_list = Expense.query.filter_by(user_id=user_id, category=category).all()
    if not expense_list:
        return jsonify({"expenses": []})
    
    return jsonify({"expenses": [e.to_dict() for e in expense_list]})

@expenses.route("/expenses/summary", methods=["GET"])
@jwt_required()
def expense_summary():
    user_id = int(get_jwt_identity())   

    expenses_list = Expense.query.filter_by(user_id=user_id).all()
    total = sum(expense.amount for expense in expenses_list)
    breakdown = {}
    for expense in expenses_list:
        if expense.category in breakdown:
            breakdown[expense.category] += expense.amount
        else:
            breakdown[expense.category] = expense.amount

    return jsonify({"total": total, "breakdown": breakdown})  


