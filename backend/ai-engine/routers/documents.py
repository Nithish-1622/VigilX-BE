"""
VigilX AI Engine - Document Processing & OCR Module
Maps to Project Implementation Phases:
- Phase 1: Multi-Modal Input & Real-Time Processing (Features 1.1 to 1.4)
- Phase 2: Intelligent FIR Parsing & Information Extraction (Features 2.1 to 2.8)

Responsible for bulk PDF/Image uploads, Tesseract/PDFPlumber OCR, extracting text,
and pushing FastEmbed vector embeddings to Qdrant.
"""
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse
import io
import os
import uuid

router = APIRouter(prefix="/ai/documents", tags=["Documents"])

from typing import List

@router.post("/upload")
async def upload_documents(file: UploadFile = File(...), fir_id: str = Form(None)):
    files = [file]
    """
    Endpoint for uploading case documents (PDF/Images) in bulk, extracting text via OCR,
    and pushing the embeddings to Qdrant vector store.
    """
    try:
        from qdrant_client import QdrantClient
        from qdrant_client.models import PointStruct
        from fastembed import TextEmbedding
        
        qdrant_url = os.environ.get("QDRANT_HOST")
        qdrant_api_key = os.environ.get("QDRANT_API_KEY")
        
        client = None
        embedding_model = None
        if qdrant_url and qdrant_api_key:
            client = QdrantClient(url=qdrant_url, api_key=qdrant_api_key)
            embedding_model = TextEmbedding(model_name="BAAI/bge-small-en-v1.5")
            
        results = []
        for file in files:
            content = await file.read()
            extracted_text = ""
            
            # Determine file type and extract text
            if file.content_type == 'application/pdf':
                import pdfplumber
                with pdfplumber.open(io.BytesIO(content)) as pdf:
                    extracted_text = "\n".join(page.extract_text() or "" for page in pdf.pages)
            elif file.content_type in ['image/jpeg', 'image/png']:
                import pytesseract
                from PIL import Image
                img = Image.open(io.BytesIO(content))
                extracted_text = pytesseract.image_to_string(img)
            else:
                results.append({"filename": file.filename, "status": "failed", "reason": "Unsupported format"})
                continue

            if not extracted_text.strip():
                results.append({"filename": file.filename, "status": "warning", "message": "No text extracted"})
                continue
            try:
                if client and embedding_model:
                    embeddings = list(embedding_model.embed([extracted_text]))
                    doc_id = str(uuid.uuid4())
                    client.upsert(
                        collection_name="vigilx_cases",
                        points=[
                            PointStruct(id=doc_id, vector=embeddings[0].tolist(), payload={"text": extracted_text[:500], "fir_id": fir_id})
                        ]
                    )
                results.append({"filename": file.filename, "status": "success", "extracted_text_preview": extracted_text[:200] + "..."})
            except Exception as inner_e:
                results.append({"filename": file.filename, "status": "success (DB Offline)", "extracted_text_preview": extracted_text[:200] + "...", "warning": str(inner_e)})
        return {"status": "completed", "results": results}
            
    except ImportError as e:
        raise HTTPException(status_code=500, detail=f"Missing dependency for OCR/PDF: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Document processing failed: {e}")
