from fastapi import APIRouter, UploadFile, Form, File
from typing import List
from services import rag
from tika import parser

router = APIRouter()

@router.post("/doc")
async def ingest_doc(
    files: List[UploadFile] = File(...),
    kind: str = Form("document"),
    source: str = Form("upload"),
):
    """Nimmt eine oder mehrere Dateien auf."""
    results = []
    for file in files:
        data = await file.read()
        title = file.filename
        parsed = parser.from_buffer(data)
        text = parsed.get("content") or ""
        chunks = rag.chunk_text(text)
        item_id, sha = rag.ingest_bytes(data, title, kind, source)
        count = rag.index_chunks(item_id, chunks)
        results.append({"item_id": item_id, "chunks": count, "sha256": sha})
    return {"status": "ok", "message": "ingested", "data": results}

