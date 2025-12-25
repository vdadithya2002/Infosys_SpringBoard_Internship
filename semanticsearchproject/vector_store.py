import pandas as pd
import numpy as np
import ast
import faiss


# Load embedded CSV
df = pd.read_csv("merged_with_embeddings.csv")

# Convert embedding_vector from string -> list -> numpy array
df["embedding_vector"] = df["embedding_vector"].apply(ast.literal_eval)

embeddings = np.vstack(df["embedding_vector"].values).astype("float32")

print("Embeddings shape:", embeddings.shape)


# Dimension of embeddings (384 for all-MiniLM-L6-v2)
dimension = embeddings.shape[1]

# Create FAISS index (L2 distance)
index = faiss.IndexFlatL2(dimension)

# Add embeddings to index
index.add(embeddings)

print("Total vectors stored in FAISS index:", index.ntotal)


faiss.write_index(index, "youtube_embeddings.index")
