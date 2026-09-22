from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.extensions import db
from app.models.expense import Expense
from app.services.groq_services import GROQ_MODEL, get_groq_client

insights = Blueprint("insights", __name__)


@insights.route("/summary", methods=["GET"])
@jwt_required()
def get_summary():
    user_id = int(get_jwt_identity())
    expenses = Expense.query.filter_by(user_id=user_id).all()

    if not expenses:
        return jsonify({"error": "no expenses found"}), 404

    total_amount = sum(expense.amount for expense in expenses)
    expense_text = "\n".join([
        f"{e.category}: {e.amount} on {e.date.strftime('%Y-%m-%d')}"
        for e in expenses
    ])

    client = get_groq_client()
    response = client.chat.completions.create(
        model=GROQ_MODEL,
        temperature=0,
        messages=[
            {
                "role": "user",
                "content": f"""You are a personal finance assistant.
Analyse these expenses and give a brief friendly summary in 3-4 sentences.
Mention total spending, biggest category, and one money saving tip.

    Expenses:
    All amounts are in Indian rupees (INR). The exact total calculated by the application is INR {total_amount:.2f}; use this value and do not convert it to another currency.
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

    expenses = Expense.query.filter_by(user_id=user_id).all()
    expense_count = len(expenses)
    total_amount = sum(expense.amount for expense in expenses)
    if expense_count == 0:
        return jsonify({"error": "no expenses found. add some expenses first"}), 404

    if not data.get("question"):
        return jsonify({"error": "question is required"}), 400

    question = data["question"]

    question_lower = question.lower()
    numeric_question = any(w in question_lower for w in [
        "total", "how much", "spent", "spend", "amount", "cost", "bill"
    ])
    matched_categories = [
        category for category in {expense.category for expense in expenses}
        if category.lower() in question_lower
    ]
    if numeric_question:
        selected_expenses = [
            expense for expense in expenses
            if not matched_categories or expense.category in matched_categories
        ]
        selected_total = sum(expense.amount for expense in selected_expenses)
        scope = " and ".join(matched_categories) if matched_categories else "all categories"
        return jsonify({
            "question": question,
            "answer": f"The total spent on {scope} is INR {selected_total:.2f}.",
            "based_on_expenses": len(selected_expenses)
        }), 200

    needs_complete_ledger = any(w in question_lower for w in [
        "all", "total", "every", "breakdown", "summary", "amount", "bill", "spend", "spent", "cost", "how much", "current"
    ])

    if needs_complete_ledger:
        context = "\n".join([
            f"{expense.category}: {expense.amount} on {expense.date.strftime('%Y-%m-%d')}"
            for expense in expenses
        ])
        based_on_expenses = expense_count
    elif any(w in question_lower for w in ["compare", "vs", "difference"]):
        n_results = 10
        based_on_expenses = n_results
    else:
        n_results = 5
        based_on_expenses = n_results

    if not needs_complete_ledger:
        try:
            from app.services.rag_service import search_expenses
            results = search_expenses(question, user_id=user_id, n_results=n_results)

            if not results["documents"][0]:
                return jsonify({"error": "no relevant expenses found. add more expenses first"}), 404

            context = "\n".join(results["documents"][0])
            based_on_expenses = len(results["documents"][0])

        except Exception as e:
            return jsonify({"error": "search failed", "details": str(e)}), 500

    client = get_groq_client()
    response = client.chat.completions.create(
        model=GROQ_MODEL,
        temperature=0,
        messages=[
            {
                "role": "user",
                "content": f"""You are a personal finance assistant.
Answer this question based on the expense data provided.
Rules:
- Always add up amounts before answering totals
- All amounts are in Indian rupees (INR). Never use dollars or convert the amounts.
- For total, bill, amount, spending, or "how much" questions, use every expense in the data provided.
- The exact application-calculated total for the complete ledger is INR {total_amount:.2f}. Use this exact total whenever the question asks for total spending or the total amount.
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
        "based_on_expenses": based_on_expenses
    }), 200