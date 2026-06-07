import os
from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity, jwt_required
from app.extensions import db
from app.models.expense import Expense
from app.services.groq_services import extract_receipt_data

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
print("UPLOAD FOLDER PATH:", UPLOAD_FOLDER)
receipts = Blueprint("receipts", __name__)

@receipts.route("/upload-receipt", methods=["POST"])
@jwt_required()
def upload_receipt():
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    user_id = int(get_jwt_identity())

    if "receipt" not in request.files:
        return jsonify({"error": "No receipt image provided"}), 400

    file = request.files["receipt"]
    print("FILENAME:", file.filename)
    file_path = os.path.join(UPLOAD_FOLDER, file.filename or "receipt.jpg")
    file.save(file_path)

    receipt_data = extract_receipt_data(file_path)

    saved_expenses = []
    for item in receipt_data["items"]:
        expense = Expense(
            user_id=user_id,
            category=item["name"],
            amount=item["amount"],
            
        )
        db.session.add(expense)

    db.session.commit()                          # commit first

    for expense in db.session.query(Expense).filter_by(user_id=user_id).order_by(Expense.id.desc()).limit(len(receipt_data["items"])).all():
        saved_expenses.append(expense.to_dict()) # then to_dict()

    os.remove(file_path)

    return jsonify({
        "message": "receipt processed",
        "expenses_created": len(saved_expenses),
        "data": receipt_data
    }), 201