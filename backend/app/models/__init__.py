"""
Model registry for Alembic.
Import all models here so Alembic can discover them.
"""
from app.db.base_class import Base

from app.models.core import User, Court, Judge, Case, CaseJudge, Act, Section, CaseSection, Precedent, CasePrecedent
from app.models.rag import Document, Chunk, Embedding, LegalPrinciple, CitationReference, ChatSession, ChatMessage, SearchHistory, Feedback, UploadedDocument, AuditLog, PromptLog
