from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.extensions import db
from app.models.expense import Expense
from app.services.groq_services import get_groq_client

insights = Blueprint("insights", __name__)


@insights.route("/summary", methods=["GET"])
@jwt_required()
def get_summary():
    user_id = int(get_jwt_identity())
    expenses = Expense.query.filter_by(user_id=user_id).all()

    if not expenses:
        return jsonify({"error": "no expenses found"}), 404

    expense_text = "\n".join([
        f"{e.category}: {e.amount} on {e.date.strftime('%Y-%m-%d')}"
        for e in expenses
    ])

    client = get_groq_client()
    response = client.chat.completions.create(
        model="meta-llama/llama-4-scout-17b-16e-instruct",
        messages=[
            {
                "role": "user",
                "content": f"""You are a personal finance assistant.
Analyse these expenses and give a brief friendly summary in 3-4 sentences.
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

    if not data:
        return jsonify({"error": "request body must be JSON"}), 400

    expense_count = Expense.query.filter_by(user_id=user_id).count()
    if expense_count == 0:
        return jsonify({"error": "no expenses found. add some expenses first"}), 404

    if not data.get("question"):
        return jsonify({"error": "question is required"}), 400

    question = data["question"]

    if any(w in question.lower() for w in ["all", "total", "every", "breakdown", "summary"]):
        n_results = 15
    elif any(w in question.lower() for w in ["compare", "vs", "difference"]):
        n_results = 10
    else:
        n_results = 5

    try:
        from app.services.rag_service import search_expenses
        results = search_expenses(question, user_id=user_id, n_results=n_results)

        if not results["documents"][0]:
            return jsonify({"error": "no relevant expenses found. add more expenses first"}), 404

        context = "\n".join(results["documents"][0])

    except Exception as e:
        return jsonify({"error": "search failed", "details": str(e)}), 500

    client = get_groq_client()
    response = client.chat.completions.create(
        model="meta-llama/llama-4-scout-17b-16e-instruct",
        messages=[
            {
                "role": "user",
                "content": f"""You are a personal finance assistant.
Answer this question based on the expense data provided.
Rules:
- Always add up amounts before answering totals
- If data seems incomplete say so
- Use the currency from the data
- Be specific — mention exact amounts and categories
- If asked to compare, calculate each category separately first
- Keep answer under 3 sentences

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