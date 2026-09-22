import os
import uuid
from collections import Counter
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import get_jwt_identity, jwt_required
from werkzeug.utils import secure_filename
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
        return jsonify({"error": "no receipt image provided"}), 400

    file = request.files["receipt"]

    if file.filename == "":
        return jsonify({"error": "no file selected"}), 400

    safe_filename = secure_filename(file.filename)
    if not safe_filename or not allowed_file(safe_filename):
        return jsonify({"error": "only jpg and png files allowed"}), 400

    file_path = os.path.join(UPLOAD_FOLDER, f"{uuid.uuid4().hex}_{safe_filename}")
    file.save(file_path)

    try:
        receipt_data = extract_receipt_data(file_path)

        def item_key(item):
            name = str(item["name"]).strip().casefold()
            amount = round(float(item["amount"]), 2)
            return name, amount

        receipt_items = Counter(item_key(item) for item in receipt_data["items"])
        existing_items = Counter(
            item_key({"name": expense.category, "amount": expense.amount})
            for expense in Expense.query.filter_by(user_id=user_id).all()
            if expense.description and expense.description.startswith("Auto:")
        )
        if all(existing_items[key] >= count for key, count in receipt_items.items()):
            return jsonify({"error": "this receipt has already been processed"}), 409

        saved_expenses = []
        for item in receipt_data["items"]:
            expense = Expense(
                user_id=user_id,
                category=item["name"],
                amount=item["amount"],
                description=f"Auto: {item['name']}"
            )
            db.session.add(expense)
            saved_expenses.append(expense)      

        db.session.commit()

        from app.services.background_tasks import queue_expense_index
        app = current_app._get_current_object()
        for expense in saved_expenses:
            queue_expense_index(app, expense.id)

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "processing failed", "details": str(e)}), 500

    finally:
        if os.path.exists(file_path):
            if not os.environ.get("DEBUG_KEEP_FILES", "false").lower() == "true":
                os.remove(file_path)

    return jsonify({
        "message": "receipt processed",
        "expenses_created": len(saved_expenses),
        "data": receipt_data
    }), 201