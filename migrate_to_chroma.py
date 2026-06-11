from app import create_app
from app.models.expense import Expense
from app.services.rag_service import store_expense

app = create_app()

with app.app_context():
    expenses = Expense.query.all()
    for expense in expenses:
        try:
            store_expense(expense)
            print(f"Stored expense {expense.id} — {expense.category}")
        except Exception as e:
            print(f"Failed expense {expense.id}: {e}")
    
    print(f"Done. {len(expenses)} expenses migrated to ChromaDB.")