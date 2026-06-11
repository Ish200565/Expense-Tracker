from sentence_transformers import SentenceTransformer 

model=SentenceTransformer("all-MiniLM-L6-v2")

def get_embedding(content):
    return model.encode(content).tolist()