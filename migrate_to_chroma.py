from app import create_app
from app.models.expense import Expense
from app.services.rag_service import store_expense, collection

app = create_app()

with app.app_context():
    expenses = Expense.query.all()
    
    for expense in expenses:
        try:
            # delete old embedding first
            try:
                collection.delete(ids=[str(expense.id)])
            except:
                pass
            
            # store with new format
            store_expense(expense)
            print(f"Re-embedded expense {expense.id} — {expense.category}")
        except Exception as e:
            print(f"Failed expense {expense.id}: {e}")
    
    print(f"Done. {len(expenses)} expenses re-embedded.")