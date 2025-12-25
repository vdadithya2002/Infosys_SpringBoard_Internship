import pandas as pd
import numpy as np
import faiss
import ast
from sentence_transformers import SentenceTransformer

# -----------------------------
# 1. Load dataset with metadata
# -----------------------------
df = pd.read_csv("merged_with_embeddings.csv")

# Convert embedding strings back to lists
df["embedding_vector"] = df["embedding_vector"].apply(ast.literal_eval)

embeddings = np.vstack(df["embedding_vector"].values).astype("float32")

# -----------------------------
# 2. Load FAISS vector database
# -----------------------------
index = faiss.read_index("youtube_embeddings.index")

print("FAISS index loaded. Total vectors:", index.ntotal)

# -----------------------------
# 3. Load embedding model
# -----------------------------
model = SentenceTransformer("all-MiniLM-L6-v2")

TITLE_COL = "title_clean" if "title_clean" in df.columns else "title"
CHANNEL_COL = "channel_title"


# -----------------------------
# 4. Semantic search function
# -----------------------------
def fetch_top_5_videos(user_query, top_k=5):
    # Step 1: Convert query to embedding
    query_embedding = model.encode(
        [user_query],
        normalize_embeddings=True
    ).astype("float32")

    # Step 2: Similarity search on vector DB
    distances, indices = index.search(query_embedding, top_k)

    # Step 3: Prepare results
    results = []
    for rank, idx in enumerate(indices[0]):
        video = df.iloc[idx]

        similarity_score = 1 / (1 + distances[0][rank])  # Convert L2 distance → similarity

        results.append({
            "video_id": video["id"],
            "title": video[TITLE_COL],
            "channel_name": video[CHANNEL_COL],
            "similarity_score": round(similarity_score, 4)
        })

    return results

# -----------------------------
# 5. Accept user query (CLI)
# -----------------------------
if __name__ == "__main__":
    user_query = input("Enter your search query: ")
    top_videos = fetch_top_5_videos(user_query)

    print("\nTop 5 Relevant Videos:\n")
    for i, video in enumerate(top_videos, 1):
        print(f"{i}.")
        print("   Video ID       :", video["video_id"])
        print("   Title          :", video["title"])
        print("   Channel Name   :", video["channel_name"])
        print("   Similarity     :", video["similarity_score"])
        print("-" * 50)
