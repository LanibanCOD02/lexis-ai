from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks, Depends
from fastapi.responses import FileResponse
import os
import uuid
import shutil
import logging
import hashlib
from datetime import date

from app.rag.loader import PDFLoader
from app.rag.cleaner import clean_extracted_text
from app.rag.chunker import DocumentChunker
from app.rag.embedder import DocumentEmbedder
from app.rag.faiss_index import VectorStore
from app.db.session import AsyncSessionLocal, get_db
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.core import Case, Court, User
from app.models.rag import Document, Chunk, Embedding, UploadedDocument
from app.api.endpoints.auth import get_current_user

router = APIRouter()
logger = logging.getLogger(__name__)
UPLOAD_DIR = "storage/raw"

def get_file_checksum(file_path: str) -> str:
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

async def process_pdf_task(file_path: str, document_id: str, file_name: str, user_id: uuid.UUID, uploaded_doc_id: uuid.UUID):
    """Background task to run the complete RAG ingestion pipeline and save to SQL."""
    async with AsyncSessionLocal() as session:
        try:
            logger.info(f"Starting ingestion pipeline for {document_id}")
            
            # 1. Ensure a dummy Court exists for unknown PDFs
            result = await session.execute(select(Court).limit(1))
            court = result.scalars().first()
            if not court:
                court = Court(name="Unknown Court", jurisdiction="Unknown")
                session.add(court)
                await session.flush()

            # 2. Extract Text
            loader = PDFLoader(file_path)
            raw_pages = loader.extract_pages()
            
            cleaned_pages = []
            for page in raw_pages:
                cleaned_text = clean_extracted_text(page.get("raw_text", ""))
                cleaned_pages.append({"page_number": page["page_number"], "text": cleaned_text})
                
            # 3. Create Case & Document Records
            case = Case(
                title=f"Extracted from {file_name}",
                case_number=f"DOC-{document_id[:8].upper()}",
                decision_date=date.today(),
                court_id=court.id,
                status="Processed"
            )
            session.add(case)
            await session.flush()
            
            checksum = get_file_checksum(file_path)
            
            # Check if checksum exists to avoid duplicates
            existing = await session.execute(select(Document).where(Document.checksum == checksum))
            if existing.scalars().first():
                raise Exception("Document with this checksum already exists.")

            document_record = Document(
                id=uuid.UUID(document_id),
                case_id=case.id,
                file_path=file_path,
                checksum=checksum,
                document_type="PDF"
            )
            session.add(document_record)
            await session.flush()

            # 4. Chunk
            chunker = DocumentChunker()
            metadata = {"case_title": case.title, "court_name": court.name}
            raw_chunks = chunker.chunk_pages(cleaned_pages, metadata)
            
            db_chunks = []
            for i, chunk_data in enumerate(raw_chunks):
                db_chunk = Chunk(
                    document_id=document_record.id,
                    content=chunk_data["content"],
                    chunk_index=i,
                    token_count=len(chunk_data["content"].split()) # simple estimate
                )
                session.add(db_chunk)
                db_chunks.append(db_chunk)
            
            await session.flush()
            
            # 5. Embed
            embedder = DocumentEmbedder()
            # Prepare format for embedder
            chunks_for_embedder = [{"content": c.content, "metadata": metadata} for c in db_chunks]
            embedded_chunks = embedder.embed_chunks(chunks_for_embedder)
            
            # 6. Store Embeddings mapping
            vector_ids = []
            embeddings = []
            for i, c in enumerate(embedded_chunks):
                vec_id = str(uuid.uuid4())
                vector_ids.append(vec_id)
                embeddings.append(c["embedding"])
                
                db_embedding = Embedding(
                    chunk_id=db_chunks[i].id,
                    model_used="gemini-embedding",
                    faiss_vector_id=vec_id
                )
                session.add(db_embedding)
            
            await session.flush()

            # 7. Add to FAISS index
            vstore = VectorStore()
            vstore.add_vectors(embeddings, vector_ids)
            
            # 8. Update Upload Status
            result = await session.execute(select(UploadedDocument).where(UploadedDocument.id == uploaded_doc_id))
            uploaded_doc = result.scalars().first()
            if uploaded_doc:
                uploaded_doc.status = "Completed"
            
            await session.commit()
            logger.info(f"Successfully processed and indexed document {document_id}")
            
        except Exception as e:
            await session.rollback()
            logger.error(f"Error processing document {document_id}: {e}")
            try:
                result = await session.execute(select(UploadedDocument).where(UploadedDocument.id == uploaded_doc_id))
                uploaded_doc = result.scalars().first()
                if uploaded_doc:
                    uploaded_doc.status = "Failed"
                await session.commit()
            except Exception as inner_e:
                logger.error(f"Failed to update document status: {inner_e}")


@router.post("/upload")
async def upload_document(
    background_tasks: BackgroundTasks, 
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Accepts a PDF document and launches the asynchronous ingestion pipeline.
    """
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")
        
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    doc_id = str(uuid.uuid4())
    file_path = os.path.join(UPLOAD_DIR, f"{doc_id}_{file.filename}")
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    uploaded_doc = UploadedDocument(
        user_id=current_user.id,
        file_name=file.filename,
        status="Processing"
    )
    db.add(uploaded_doc)
    await db.commit()
    await db.refresh(uploaded_doc)
        
    background_tasks.add_task(process_pdf_task, file_path, doc_id, file.filename, current_user.id, uploaded_doc.id)
    
    return {"message": "Document uploaded successfully. Processing in background.", "document_id": doc_id, "upload_id": str(uploaded_doc.id)}

@router.get("/{document_id}/file")
async def get_document_file(
    document_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Returns the physical PDF file associated with a document_id.
    Ensures that path traversal is prevented by only using the trusted DB path.
    """
    stmt = select(Document).where(Document.id == document_id)
    result = await db.execute(stmt)
    document = result.scalars().first()
    
    if not document:
        raise HTTPException(status_code=404, detail="Document not found.")
        
    file_path = document.file_path
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File missing on server.")
        
    # Prevent path traversal implicitly: we only use the DB's absolute path or relative trusted path
    return FileResponse(file_path, media_type="application/pdf", filename=os.path.basename(file_path))
