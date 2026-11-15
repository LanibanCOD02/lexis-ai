import uuid
import re
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.db.session import get_db
from app.models.rag import Chunk, Document
from app.models.core import Case, User
from app.api.endpoints.auth import get_current_user

router = APIRouter()

def extract_page_number_from_content(content: str) -> int:
    """Fallback to extract page number from content header if structured field is unavailable."""
    match = re.search(r"Page:\s*(\d+)", content)
    if match:
        return int(match.group(1))
    return 1 # Default to 1 if not found

@router.get("/{chunk_id}")
async def get_citation(
    chunk_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Retrieves the source citation details for a given chunk.
    """
    stmt = (
        select(Chunk, Document, Case)
        .join(Document, Chunk.document_id == Document.id)
        .join(Case, Document.case_id == Case.id)
        .where(Chunk.id == chunk_id)
    )
    result = await db.execute(stmt)
    row = result.first()
    
    if not row:
        raise HTTPException(status_code=404, detail="Citation chunk not found.")
        
    chunk, document, case = row
    
    # Check if Chunk has a structured page_number attribute (it does not currently in schema)
    if hasattr(chunk, "page_number") and chunk.page_number is not None:
        page_number = chunk.page_number
    else:
        page_number = extract_page_number_from_content(chunk.content)

    return {
        "chunk_id": str(chunk.id),
        "document_id": str(document.id),
        "case_id": str(case.id),
        "document_name": document.file_path.split("/")[-1].split("\\")[-1], # Safe extraction of filename
        "page_number": page_number,
        "content": chunk.content,
        "source_type": "judgment"
    }
