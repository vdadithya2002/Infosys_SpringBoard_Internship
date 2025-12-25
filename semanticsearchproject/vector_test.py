from sentence_transformers import SentenceTransformer

model = SentenceTransformer("all-MiniLM-L6-v2")

def search(query, top_k=5):
    query_embedding = model.encode([query], normalize_embeddings=True)
    query_embedding = query_embedding.astype("float32")

    distances, indices = index.search(query_embedding, top_k)

    results = df.iloc[indices[0]][
        ["title", "publishedAt", "viewCount"]
    ]

    return results, distances
