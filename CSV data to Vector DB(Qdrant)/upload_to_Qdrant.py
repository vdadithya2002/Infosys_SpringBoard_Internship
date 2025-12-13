import os
from dotenv import load_dotenv
import pandas as pd
import ast
import uuid
from qdrant_client import QdrantClient
from qdrant_client.http import models as rest

# Load .env variables
load_dotenv()

QDRANT_URL = os.getenv("QDRANT_URL")
CSV_PATH = "final_with_embeddings.csv"   # same folder as script
COLLECTION_NAME = "youtube_videos"

def parse_embedding(s):
    try:
        return list(map(float, ast.literal_eval(s)))
    except:
        return None

# Load CSV
df = pd.read_csv(CSV_PATH)

# Connect to LOCAL Qdrant
client = QdrantClient(url=QDRANT_URL)

# Detect vector dimension
dim = len(parse_embedding(df["embedding"][0]))

# Create collection
client.recreate_collection(
    collection_name=COLLECTION_NAME,
    vectors_config=rest.VectorParams(size=dim, distance=rest.Distance.COSINE)
)

# Prepare points
points = []
for i, row in df.iterrows():
    emb = parse_embedding(row["embedding"])
    if emb is None:
        continue

    payload = {
        "video_id": row["id"],
        "title": row["title"],
        "channel_title": row["channel_title"],
        "viewCount": row["viewCount"],
        "duration_seconds": row["duration_seconds"],
        "transcript": row["transcript"]
    }

    points.append(
        rest.PointStruct(
            id=str(uuid.uuid4()),  # safe for Qdrant
            vector=emb,
            payload=payload
        )
    )

# Upload points
client.upsert(collection_name=COLLECTION_NAME, points=points)

print("Upload Complete! Data successfully uploaded to LOCAL Qdrant.")
