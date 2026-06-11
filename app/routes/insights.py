from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.extensions import db
from app.models.expense import Expense
from app.services.rag_service import search_expenses
from app.services.groq_services import get_groq_client

insights=Blueprint("insights",__name__)

@insights.route("/summary", methods=["GET"])
@jwt_required()
def get_summary():
    user_id=int(get_jwt_identity())
    expenses= Expense.query.filter_by(user_id=user_id).all()

    if not expenses:
         return jsonify({"error": "No expenses found"}),404
    
    expense_text="\n".join([f"{e.category}:{e.amount} on {e.date.strftime('%Y-%m-%d')}" for e in expenses])

    client = get_groq_client()
    response = client.chat.completions.create(
        model="meta-llama/llama-4-scout-17b-16e-instruct",
        messages=[
            {
                "role": "user",
                "content": f"""You are a personal finance assistant.
Analyse these expenses and give a brief, friendly summary in 3-4 sentences.
Mention total spending, biggest category, and one money saving tip.


Expenses:
{expense_text}"""
            }
        ]
    )

    return jsonify({
        "summary": response.choices[0].message.content
    }), 200

@insights.route("/ask", methods=["POST"])
@jwt_required()
def ask_question():
    user_id = int(get_jwt_identity())
    data = request.get_json()

    if not data.get("question"):
        return jsonify({"error": "question is required"}), 400

    question = data["question"]

    results = search_expenses(question, user_id=user_id, n_results=5)

    if not results["documents"][0]:
        return jsonify({"error": "no relevant expenses found"}), 404

    context = "\n".join(results["documents"][0])

    client = get_groq_client()
    response = client.chat.completions.create(
        model="meta-llama/llama-4-scout-17b-16e-instruct",
        messages=[
            {
                "role": "user",
                "content": f"""You are a personal finance assistant.
Answer this question based on the expense data provided.
Be specific with amounts and dates. Keep answer under 3 sentences.

Expense data:
{context}

Question: {question}"""
            }
        ]
    )

    return jsonify({
        "question": question,
        "answer": response.choices[0].message.content,
        "based_on_expenses": len(results["documents"][0])
    }), 200