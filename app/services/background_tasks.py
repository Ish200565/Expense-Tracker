from concurrent.futures import ThreadPoolExecutor

from app.extensions import db
from app.models.expense import Expense


executor = ThreadPoolExecutor(max_workers=1)


def _index_expense(app, expense_id):
    with app.app_context():
        try:
            expense = db.session.get(Expense, expense_id)
            if expense:
                from app.services.rag_service import store_expense
                store_expense(expense)
        except Exception as error:
            print(f"ChromaDB store failed: {error}")
        finally:
            db.session.remove()


def queue_expense_index(app, expense_id):
    executor.submit(_index_expense, app, expense_id)