"""
Core domain models for the Legal Research Engine.
Includes Users, Courts, Judges, Cases, Acts, Sections, and Precedents.
"""
import uuid
from datetime import datetime, date
from typing import List, Optional
from sqlalchemy import String, Integer, Text, ForeignKey, Date, DateTime, func, CheckConstraint, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy import JSON

JSONVariant = JSONB().with_variant(JSON(), "sqlite")

from app.db.base_class import Base

class User(Base):
    __tablename__ = "users"
    
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(50), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), nullable=False)
    
    __table_args__ = (
        CheckConstraint("role IN ('Lawyer', 'Judge', 'Admin')", name="check_user_role"),
    )

class Court(Base):
    __tablename__ = "courts"
    
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    jurisdiction: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

class Judge(Base):
    __tablename__ = "judges"
    
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    appointed_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)

class Case(Base):
    __tablename__ = "cases"
    
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title: Mapped[str] = mapped_column(String(500), nullable=False, index=True)
    case_number: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    decision_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    court_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("courts.id"), nullable=False, index=True)
    status: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    summary: Mapped[Optional[dict]] = mapped_column(JSONVariant, nullable=True)

class CaseJudge(Base):
    __tablename__ = "case_judges"
    
    case_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("cases.id"), primary_key=True, index=True)
    judge_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("judges.id"), primary_key=True, index=True)
    role: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

class Act(Base):
    __tablename__ = "acts"
    
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    enactment_year: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

class Section(Base):
    __tablename__ = "sections"
    
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    act_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("acts.id"), nullable=False, index=True)
    section_number: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    __table_args__ = (
        UniqueConstraint('act_id', 'section_number', name='uix_act_section'),
    )

class CaseSection(Base):
    __tablename__ = "case_sections"
    
    case_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("cases.id"), primary_key=True, index=True)
    section_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("sections.id"), primary_key=True, index=True)

class Precedent(Base):
    __tablename__ = "precedents"
    
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    citation_string: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    title: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

class CasePrecedent(Base):
    __tablename__ = "case_precedents"
    
    case_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("cases.id"), primary_key=True, index=True)
    precedent_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("precedents.id"), primary_key=True, index=True)
    context: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
