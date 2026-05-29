#The key thing here is Blueprint. This is how Flask organises routes across multiple files.
from flask import Blueprint, request,jsonify
from app.extensions import db
from app.models.category import Note

auth= Blueprint("auth", __name__)


@auth.route("/notes",methods=["POST"])
def create_note():
            data=request.get_json()

            if not data or not data.get("content"):
                return jsonify({"error": "content is required"}), 400

            if not data.get("title"):
                return jsonify({"error": "title is required"}), 400

            note = Note(title=data["title"], content=data["content"])
            db.session.add(note)
            db.session.commit()
    
            return jsonify({"message": "note saved", "id": note.id}), 201