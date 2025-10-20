from fastapi import APIRouter
from pydantic import BaseModel
from api.services import rag

router = APIRouter(prefix="/api/v1/rag", tags=["RAG"])

class AskBody(BaseModel):
    question: str
    top_k: int | None = 6

@router.post("/ask")
def rag_ask(body: AskBody):
    """Fragt die RAG-Engine ab und liefert eine KI-generierte Antwort."""
    try:
        result = rag.ask(body.question, top_k=body.top_k or 6)
        return {"status": "ok", "data": result}
    except Exception as e:
        return {"status": "error", "detail": str(e)}

