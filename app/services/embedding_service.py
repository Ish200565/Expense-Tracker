from fastembed import TextEmbedding

model = TextEmbedding("BAAI/bge-small-en-v1.5")

def get_embedding(text):
    embeddings = list(model.embed([text]))
    return embeddings[0].tolist()