import os
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams

def init_qdrant_collections():
    """
    Initializes Qdrant collections required by the AI Engine.
    This should be run once during infrastructure setup.
    """
    host = os.getenv("QDRANT_HOST", "localhost")
    port = int(os.getenv("QDRANT_PORT", "6333"))
    
    print(f"Connecting to Qdrant at {host}:{port}...")
    client = QdrantClient(host=host, port=port)
    
    collections = [
        {
            "name": "crime_cases",
            "size": 384, # Adjust based on the embedding model Dev 2 uses (e.g. all-MiniLM-L6-v2)
            "distance": Distance.COSINE
        }
    ]
    
    for coll in collections:
        name = coll["name"]
        if not client.collection_exists(name):
            print(f"Creating collection: {name}")
            client.create_collection(
                collection_name=name,
                vectors_config=VectorParams(size=coll["size"], distance=coll["distance"])
            )
            print(f"Collection '{name}' created successfully.")
        else:
            print(f"Collection '{name}' already exists.")

if __name__ == "__main__":
    init_qdrant_collections()
