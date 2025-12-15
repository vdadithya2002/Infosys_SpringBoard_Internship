from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

# 1. Load a free/open-source embedding model
model_name = "all-MiniLM-L6-v2"  # or "all-mpnet-base-v2"
model = SentenceTransformer(model_name)

# 2. Define some words/phrases
sentences = [
    "business",
    "entrepreneurship",
    "startup",
    "spirituality",
    "meditation",
    "cricket"
]

# 3. Generate embeddings (each will be a vector, e.g. 384 dimensions)
embeddings = model.encode(sentences)

# 4. Helper to print cosine similarity between any two
def show_similarity(i, j):
    v1 = embeddings[i].reshape(1, -1)
    v2 = embeddings[j].reshape(1, -1)
    sim = cosine_similarity(v1, v2)[0][0]
    print(f"Similarity('{sentences[i]}', '{sentences[j]}') = {sim:.4f}")

# 5. Check similar vs dissimilar words
# Expect high similarity:
show_similarity(0, 1)  # business vs entrepreneurship
show_similarity(1, 2)  # entrepreneurship vs startup

# Expect moderate/low similarity:
show_similarity(0, 3)  # business vs spirituality
show_similarity(3, 4)  # spirituality vs meditation (should still be high)
show_similarity(0, 5)  # business vs cricket (likely lower)


# Compute full cosine similarity matrix
sim_matrix = cosine_similarity(embeddings)

print("Cosine similarity matrix:")
print("Sentences:", sentences)
print(np.round(sim_matrix, 3))
