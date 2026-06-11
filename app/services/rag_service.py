import chromadb
import os


from app.services.embedding_service import get_embedding


BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
CHROMA_PATH = os.path.join(BASE_DIR, "chroma_db")

client =chromadb.PersistentClient(path=CHROMA_PATH)
collection=client.get_or_create_collection(name="expenses")


def store_expense(expense):
    content=f"{expense.category} amount {expense.amount} "
    embedding = get_embedding(content)
    collection.add(
        ids=[str(expense.id)],
        embeddings=[embedding],
        documents=[content],
        metadatas=[{
            "user_id": str(expense.user_id),
            "amount": expense.amount,
            "category": expense.category,
            "date": str(expense.date)
        }]
    )

def search_expenses(query, user_id, n_results=5):
    embedding = get_embedding(query)
    results = collection.query(
        query_embeddings=[embedding],
        n_results=n_results,
        where={"user_id": str(user_id)}
    )
    return results