# from curses import raw
import os
from flask import Blueprint, json, request, jsonify
from flask_jwt_extended import get_jwt_identity, jwt_required
from app.extensions import db
from app.models.expense import Expense
from app.services.groq_services import extract_receipt_data

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png"}  

def allowed_file(filename):                           
    return "." in filename and \
           filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

receipts = Blueprint("receipts", __name__)

@receipts.route("/upload-receipt", methods=["POST"])
@jwt_required()
def upload_receipt():
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    user_id = int(get_jwt_identity())

    if "receipt" not in request.files:
        return jsonify({"error": "No receipt image provided"}), 400

    file = request.files["receipt"]
    
    if file.filename == "":                           #empty filename
        return jsonify({"error": "no file selected"}), 400

    if not allowed_file(file.filename):               # helper function
        return jsonify({"error": "only jpg and png files allowed"}), 400

    file_path = os.path.join(UPLOAD_FOLDER, file.filename or "receipt.jpg")
    file.save(file_path) #Prevents saving to a path with no filename.


    try:
        receipt_data = extract_receipt_data(file_path)

        saved_expenses = []
        for item in receipt_data["items"]:
            expense = Expense(
                user_id=user_id,
                category=item["name"],
                amount=item["amount"],
                
        )
            db.session.add(expense)
            saved_expenses.append(item)

        db.session.commit()

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "processing failed", "details": str(e)}), 500

    finally:
        if os.path.exists(file_path):
            os.remove(file_path)        # ← always runs, success or failure

    return jsonify({
    "message": "receipt processed",
    "expenses_created": len(saved_expenses),
    "data": receipt_data
}), 201