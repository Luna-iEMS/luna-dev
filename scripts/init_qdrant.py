import qdrant_client
from qdrant_client.http import models as qm

print("🔗 Connecting to Qdrant at luna_qdrant:6333 ...")
c = qdrant_client.QdrantClient(host="luna_qdrant", port=6333)

print("🧠 Creating collection 'luna_chunks' (dim=384, cosine)...")
c.recreate_collection(
    collection_name="luna_chunks",
    vectors_config=qm.VectorParams(size=384, distance=qm.Distance.COSINE)
)
print("✅ Collection created successfully.")
