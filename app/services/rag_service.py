from datetime import datetime

import chromadb
import os


from app.services.embedding_service import get_embedding


BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
CHROMA_PATH = os.path.join(BASE_DIR, "chroma_db")

client =chromadb.PersistentClient(path=CHROMA_PATH)
collection=client.get_or_create_collection(name="expenses")


def store_expense(expense):
    content=f"{expense.category} {expense.description}  amount {expense.amount} "
    embedding = get_embedding(content)
    collection.add(
        ids=[str(expense.id)],
        embeddings=[embedding],
        documents=[content],
        metadatas=[{
            "user_id": str(expense.user_id),
            "amount": expense.amount,
            "category": expense.category,
            "description": expense.description,
            "date": str(expense.date)
        }]
    )

def search_expenses(query, user_id, n_results=5, days=90):
    from datetime import datetime, timedelta
    cutoff = (datetime.utcnow() - timedelta(days=days)).isoformat()
    
    embedding = get_embedding(query)
    results = collection.query(
        query_embeddings=[embedding],
        n_results=n_results,
        where={
            "$and": [
                {"user_id": {"$eq": str(user_id)}},
                {"date": {"$gte": cutoff}}
            ]
        }
    )
    return results

def update_expense_embedding(expense):
    # delete old embedding
    try:
        collection.delete(ids=[str(expense.id)])
    except:
        pass
    # store new one
    store_expense(expense)

def delete_expense_embedding(expense_id):
    try:
        collection.delete(ids=[str(expense_id)])
    except Exception as e:
        print(f"ChromaDB delete failed: {e}")