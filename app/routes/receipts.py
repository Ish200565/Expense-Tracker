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

    try:                                              # wrap Groq call
        receipt_data = extract_receipt_data(file_path)
    except Exception as e:
        os.remove(file_path)
        return jsonify({"error": "AI processing failed", "details": str(e)}), 500

    saved_expenses = []
    for item in receipt_data["items"]:
        expense = Expense(
            user_id=user_id,
            category=item["name"],
            amount=item["amount"],
            
        )
        db.session.add(expense)

    db.session.commit()                       


    for expense in db.session.query(Expense).filter_by(user_id=user_id).order_by(Expense.id.desc()).limit(len(receipt_data["items"])).all():
        saved_expenses.append(expense.to_dict())

    # os.remove(file_path)
   
    DEBUG_KEEP_FILES = False   # change to False before deployment

    if not DEBUG_KEEP_FILES:
        os.remove(file_path)

    return jsonify({
        "message": "receipt processed",
        "expenses_created": len(saved_expenses),
        "data": receipt_data
    }), 201