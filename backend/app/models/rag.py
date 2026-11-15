"""
RAG pipeline and application telemetry models.
Includes Documents, Chunks, Embeddings, Chat Sessions, and Audits.
"""
import uuid
from datetime import datetime
from typing import Optional
from sqlalchemy import String, Integer, Text, ForeignKey, DateTime, Float, CheckConstraint, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB

from app.db.base_class import Base

# SQLAlchemy does not have a native cross-DB JSONB except via dialects.
# We will use JSON which maps correctly in SQLite and Postgres, 
# or explicit JSONB for Postgres if required. Using JSON as standard fallback.
JSONVariant = JSONB().with_variant(JSON(), "sqlite")

class Document(Base):
    __tablename__ = "documents"
    
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    case_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("cases.id"), nullable=False, index=True)
    file_path: Mapped[str] = mapped_column(String(500), nullable=False)
    checksum: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    document_type: Mapped[str] = mapped_column(String(50), nullable=False)
    
    case: Mapped["Case"] = relationship("Case", foreign_keys=[case_id])

class Chunk(Base):
    __tablename__ = "chunks"
    
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("documents.id"), nullable=False, index=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    chunk_index: Mapped[int] = mapped_column(Integer, nullable=False)
    token_count: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    
    document: Mapped["Document"] = relationship("Document", foreign_keys=[document_id])

class Embedding(Base):
    __tablename__ = "embeddings"
    
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    chunk_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("chunks.id"), nullable=False, index=True)
    model_used: Mapped[str] = mapped_column(String(100), nullable=False)
    faiss_vector_id: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    generated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    
    chunk: Mapped["Chunk"] = relationship("Chunk", foreign_keys=[chunk_id])

class LegalPrinciple(Base):
    __tablename__ = "legal_principles"
    
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    case_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("cases.id"), nullable=False, index=True)
    principle_title: Mapped[str] = mapped_column(String(255), nullable=False)
    principle_text: Mapped[str] = mapped_column(Text, nullable=False)
    confidence_score: Mapped[float] = mapped_column(Float, nullable=False)
    supporting_chunk_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("chunks.id"), nullable=True)
    page_number: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    generated_by: Mapped[str] = mapped_column(String(100), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

class CaseCitation(Base):
    __tablename__ = "case_citations"
    
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    source_case_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("cases.id"), nullable=False, index=True)
    target_case_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("cases.id"), nullable=True, index=True)
    target_case_title: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    source_chunk_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("chunks.id"), nullable=False, index=True)
    citation_text: Mapped[str] = mapped_column(Text, nullable=False)
    page_number: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    relationship_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    confidence_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

class CitationReference(Base):
    __tablename__ = "citation_references"
    
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    chunk_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("chunks.id"), nullable=False, index=True)
    page_number: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    start_offset: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    end_offset: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    snippet: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

class ChatSession(Base):
    __tablename__ = "chat_sessions"
    
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    title: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

class ChatMessage(Base):
    __tablename__ = "chat_messages"
    
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("chat_sessions.id"), nullable=False, index=True)
    sender_type: Mapped[str] = mapped_column(String(50), nullable=False)
    message_text: Mapped[str] = mapped_column(Text, nullable=False)
    sent_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    citations_json: Mapped[Optional[dict]] = mapped_column(JSONVariant, nullable=True)
    
    __table_args__ = (
        CheckConstraint("sender_type IN ('User', 'AI')", name="check_sender_type"),
    )

class SearchHistory(Base):
    __tablename__ = "search_history"
    
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True, index=True)
    query_text: Mapped[str] = mapped_column(Text, nullable=False)
    filters_json: Mapped[Optional[dict]] = mapped_column(JSONVariant, nullable=True)
    executed_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False, index=True)

class Feedback(Base):
    __tablename__ = "feedback"
    
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    entity_type: Mapped[str] = mapped_column(String(50), nullable=False)
    entity_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False, index=True)
    rating: Mapped[int] = mapped_column(Integer, nullable=False)
    comments: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

class UploadedDocument(Base):
    __tablename__ = "uploaded_documents"
    
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    uploaded_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

class AuditLog(Base):
    __tablename__ = "audit_logs"
    
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True, index=True)
    action: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    resource: Mapped[str] = mapped_column(String(255), nullable=False)
    details: Mapped[Optional[dict]] = mapped_column(JSONVariant, nullable=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False, index=True)

class PromptLog(Base):
    __tablename__ = "prompt_logs"
    
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    prompt_text: Mapped[str] = mapped_column(Text, nullable=False)
    response_text: Mapped[str] = mapped_column(Text, nullable=False)
    model_name: Mapped[str] = mapped_column(String(100), nullable=False)
    token_count_input: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    token_count_output: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    operation: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    latency_ms: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    success: Mapped[Optional[bool]] = mapped_column(Integer, nullable=True) # use integer for boolean compatibility across db types
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
