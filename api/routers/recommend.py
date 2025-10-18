from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import requests
from qdrant_client import QdrantClient
from qdrant_client.models import Filter


router = APIRouter(prefix="/api/v1/recommend", tags=["recommend"])


class RecommendRequest(BaseModel):
    query: str
    top_k: int = 5
    collection: str = "documents"


class RecommendedItem(BaseModel):
    id: str
    text: str
    score: float
    source: Optional[str] = None


class RecommendResponse(BaseModel):
    items: List[RecommendedItem]


def get_embedding_ollama(text: str):
    """Embedding über Ollama erzeugen"""
    try:
        response = requests.post(
            "http://ollama:11434/api/embed",
            json={"model": "nomic-embed-text", "input": text},
            timeout=20
        )
        response.raise_for_status()
        data = response.json()
        embedding = data.get("embeddings", [None])[0]
        if not embedding:
            raise ValueError("Leeres Embedding empfangen.")
        return embedding
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ollama error: {str(e)}")


@router.post("/", response_model=RecommendResponse)
def recommend(req: RecommendRequest):
    """Suche ähnliche Dokumente in Qdrant basierend auf Textquery"""
    qdrant = QdrantClient(host="qdrant", port=6333)

    vector = get_embedding_ollama(req.query)
    if not vector:
        raise HTTPException(status_code=500, detail="Keine Embedding-Daten empfangen")

    try:
        results = qdrant.search(
            collection_name=req.collection,
            query_vector=vector,
            limit=req.top_k,
            query_filter=Filter(must=[])
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Qdrant error: {str(e)}")

    items = []
    for hit in results:
        payload = hit.payload or {}
        items.append(RecommendedItem(
            id=str(payload.get("id", hit.id)),
            text=payload.get("text", "[kein Inhalt]"),
            score=round(hit.score, 4),
            source=payload.get("source")
        ))

    return RecommendResponse(items=items)
