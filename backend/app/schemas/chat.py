from pydantic import BaseModel
from typing import List, Optional

class ChatRequest(BaseModel):
    query: str
    session_id: Optional[str] = None
    filters: Optional[dict] = None

class Citation(BaseModel):
    chunk_id: str
    text_snippet: str
    page_number: int
    case_title: str

class ChatResponse(BaseModel):
    answer: str
    citations: List[Citation]
