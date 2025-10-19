from fastapi import APIRouter
from pydantic import BaseModel
from services import rag

router = APIRouter(prefix="/api/v1/rag", tags=["RAG (Retrieval-Augmented Generation)"])

class AskBody(BaseModel):
    question: str
    top_k: int | None = 6

@router.post("/ask")
def rag_ask(body: AskBody):
    """
    Beantwortet eine Frage mithilfe des RAG-Moduls (Retriever + LLM).
    """
    try:
        result = rag.ask(body.question, top_k=body.top_k or 6)
        return {"status": "ok", "data": result}
    except Exception as e:
        return {"status": "error", "message": str(e)}
