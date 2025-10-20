from fastapi import APIRouter, UploadFile, File
from api.services import tika, embed, qdrant
import tempfile, shutil, os

router = APIRouter(prefix="/api/v1/ingest", tags=["Ingest"])

@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """Nimmt Datei entgegen, extrahiert Text via Tika und speichert Embeddings in Qdrant."""
    try:
        # Temporäre Datei speichern
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            shutil.copyfileobj(file.file, tmp)
            tmp_path = tmp.name

        # Text extrahieren (Bytes statt Pfad)
        with open(tmp_path, "rb") as f:
            file_bytes = f.read()
        text = tika.extract_text(file_bytes, file.filename)

        if not text or not text.strip():
            return {"status": "error", "detail": "Keine extrahierbaren Texte gefunden."}

        # Embeddings erzeugen
        vectors = embed.embed_texts([text])
        if not vectors or not isinstance(vectors, list) or vectors[0] is None:
            return {"status": "error", "detail": "Fehler beim Erzeugen der Embeddings."}

        # Qdrant initialisieren & speichern
        qdrant.ensure_collection(dim=len(vectors[0]))
        qdrant.upsert_vectors([text], vectors)

        os.unlink(tmp_path)
        return {"status": "ok", "filename": file.filename, "length": len(text)}

    except Exception as e:
        return {"status": "error", "detail": str(e)}

