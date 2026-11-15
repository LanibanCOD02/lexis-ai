from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from sqlalchemy import delete, or_, and_, func
from typing import List, Dict, Any
import uuid
import json
import logging

from app.db.session import get_db
from app.models.core import Case, User
from app.models.rag import Chunk, Document, LegalPrinciple, Embedding, CaseCitation
from app.rag.generator import GeminiGenerator
from app.rag.embedder import DocumentEmbedder
from app.rag.faiss_index import VectorStore
from app.api.endpoints.auth import get_current_user
import re

router = APIRouter()
logger = logging.getLogger(__name__)

async def get_case_chunks(case_id: uuid.UUID, db: AsyncSession) -> List[Dict[str, Any]]:
    # Retrieve all chunks belonging to documents of this case
    stmt = (
        select(Chunk)
        .join(Document)
        .where(Document.case_id == case_id)
        .order_by(Chunk.chunk_index)
    )
    result = await db.execute(stmt)
    chunks = result.scalars().all()
    
    if not chunks:
        raise HTTPException(status_code=404, detail="No chunks found for this case.")
        
    return [
        {
            "id": str(c.id),
            "content": c.content,
            "page_number": c.chunk_index + 1,
        }
        for c in chunks
    ]

@router.get("/")
async def get_all_cases(db: AsyncSession = Depends(get_db)):
    stmt = select(Case).limit(10)
    result = await db.execute(stmt)
    cases = result.scalars().all()
    return [
        {
            "id": str(c.id),
            "title": c.title,
            "case_number": c.case_number
        }
        for c in cases
    ]

@router.post("/{case_id}/summarize")
async def summarize_case(case_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    case = await db.get(Case, case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found.")
        
    chunks_data = await get_case_chunks(case_id, db)
    
    for c in chunks_data:
        c["case_title"] = case.title
        c["court_name"] = "Unknown"
        
    generator = GeminiGenerator()
    summary_text = await generator.generate_case_summary(chunks_data)
    
    try:
        summary_json = json.loads(summary_text)
    except Exception as e:
        logger.error(f"Failed to parse summary JSON: {e}\n{summary_text}")
        raise HTTPException(status_code=500, detail="Failed to parse LLM summary output as JSON.")
        
    case.summary = summary_json
    await db.commit()
    await db.refresh(case)
    
    return summary_json

@router.get("/{case_id}/summary")
async def get_case_summary(case_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    case = await db.get(Case, case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found.")
    
    if not case.summary:
        raise HTTPException(status_code=404, detail="Summary not generated for this case.")
        
    return case.summary

@router.post("/{case_id}/principles/extract")
async def extract_principles(case_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    case = await db.get(Case, case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found.")
        
    stmt = select(Chunk).join(Document).where(Document.case_id == case_id)
    result = await db.execute(stmt)
    chunks = result.scalars().all()
    
    if not chunks:
        raise HTTPException(status_code=404, detail="No chunks found for this case.")
        
    chunk_map = {str(c.id): c.chunk_index + 1 for c in chunks}
    chunks_data = [
        {
            "id": str(c.id),
            "content": c.content,
            "page_number": chunk_map[str(c.id)],
            "case_title": case.title,
            "court_name": "Unknown"
        }
        for c in chunks
    ]
    
    generator = GeminiGenerator(is_lightweight=True)
    principles_text = await generator.extract_legal_principles(chunks_data)
    
    try:
        principles_json = json.loads(principles_text)
    except Exception as e:
        logger.error(f"Failed to parse principles JSON: {e}\n{principles_text}")
        raise HTTPException(status_code=500, detail="Failed to parse LLM principle output as JSON.")
        
    if not isinstance(principles_json, list):
        principles_json = []

    await db.execute(delete(LegalPrinciple).where(LegalPrinciple.case_id == case_id))
    
    saved_principles = []
    for p in principles_json:
        chunk_id_str = p.get("supporting_chunk_id")
        page_num = p.get("page_number")
        
        if chunk_id_str and chunk_id_str in chunk_map:
            page_num = chunk_map[chunk_id_str]
        elif chunk_id_str and chunk_id_str not in chunk_map:
            chunk_id_str = None
            
        lp = LegalPrinciple(
            case_id=case_id,
            principle_title=p.get("principle_title", "Unknown"),
            principle_text=p.get("principle_text", "Unknown"),
            confidence_score=float(p.get("confidence_score", 0.0)),
            supporting_chunk_id=uuid.UUID(chunk_id_str) if chunk_id_str else None,
            page_number=page_num,
            generated_by="Gemini 3.5 Flash-Lite"
        )
        db.add(lp)
        saved_principles.append(lp)
        
    await db.commit()
    
    return [
        {
            "id": str(lp.id),
            "principle_title": lp.principle_title,
            "principle_text": lp.principle_text,
            "confidence_score": lp.confidence_score,
            "supporting_chunk_id": str(lp.supporting_chunk_id) if lp.supporting_chunk_id else None,
            "page_number": lp.page_number
        }
        for lp in saved_principles
    ]

@router.get("/{case_id}/principles")
async def get_case_principles(case_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    stmt = select(LegalPrinciple).where(LegalPrinciple.case_id == case_id)
    result = await db.execute(stmt)
    principles = result.scalars().all()
    
    return [
        {
            "id": str(lp.id),
            "principle_title": lp.principle_title,
            "principle_text": lp.principle_text,
            "confidence_score": lp.confidence_score,
            "supporting_chunk_id": str(lp.supporting_chunk_id) if lp.supporting_chunk_id else None,
            "page_number": lp.page_number
        }
        for lp in principles
    ]

@router.get("/{case_id}/similar")
async def get_similar_cases(
    case_id: uuid.UUID, 
    limit: int = 5, 
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Find judgments semantically similar to the currently selected case.
    """
    limit = min(limit, 10)
    
    # Verify the requested case exists
    case = await db.get(Case, case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found.")
        
    # Get the first 3 chunks to represent this case
    chunks_data = await get_case_chunks(case_id, db)
    representative_chunks = chunks_data[:3]
    
    if not representative_chunks:
        return {"case_id": str(case_id), "similar_cases": [], "message": "No sufficiently similar cases found."}
        
    # Concatenate text, removing the `Page: X\n---\n` metadata
    combined_text = ""
    for c in representative_chunks:
        content = c["content"]
        # Remove header like "Page: 48\n---\n"
        content = re.sub(r"Page:\s*\d+\s*\n---\n", "", content)
        combined_text += content + "\n\n"
        
    combined_text = combined_text.strip()
    if not combined_text:
         return {"case_id": str(case_id), "similar_cases": [], "message": "No sufficiently similar cases found."}

    # Embed the representative text
    embedder = DocumentEmbedder()
    query_chunk = [{"content": combined_text}]
    query_vector = embedder.embed_chunks(query_chunk)[0]["embedding"]
    
    # Query FAISS
    vstore = VectorStore()
    try:
        results = vstore.search(query_vector, top_k=50)
    except Exception as e:
        logger.error(f"FAISS search failed: {e}")
        return {"case_id": str(case_id), "similar_cases": [], "message": "No sufficiently similar cases found."}
        
    if not results:
        return {"case_id": str(case_id), "similar_cases": [], "message": "No sufficiently similar cases found."}
        
    # Extract distances and fetch metadata
    vector_ids = [vid for vid, dist in results]
    distance_map = {vid: dist for vid, dist in results}
    
    stmt = (
        select(Embedding)
        .where(Embedding.faiss_vector_id.in_(vector_ids))
        .options(
            selectinload(Embedding.chunk)
            .selectinload(Chunk.document)
            .selectinload(Document.case)
        )
    )
    result = await db.execute(stmt)
    embeddings = result.scalars().all()
    
    case_groups = {}
    
    # Process and group by case_id, excluding current case
    for emb in embeddings:
        chunk = emb.chunk
        document = chunk.document
        result_case = document.case
        
        if result_case.id == case_id:
            continue
            
        dist = distance_map[emb.faiss_vector_id]
        
        # Deduplication using minimum distance
        if result_case.id not in case_groups or dist < case_groups[result_case.id]["distance"]:
            # Extract page number for excerpt display
            page_match = re.search(r"Page:\s*(\d+)", chunk.content)
            page_num = int(page_match.group(1)) if page_match else 1
            
            # Clean excerpt for presentation
            clean_excerpt = re.sub(r"Page:\s*\d+\s*\n---\n", "", chunk.content)
            
            case_groups[result_case.id] = {
                "case": result_case,
                "distance": dist,
                "chunk": chunk,
                "page_number": page_num,
                "excerpt": clean_excerpt
            }
            
    # Rank by distance
    sorted_cases = sorted(case_groups.values(), key=lambda x: x["distance"])
    
    similar_cases = []
    for item in sorted_cases[:limit]:
        dist = item["distance"]
        sim_score = max(0.0, 1.0 - (dist / 2.0))
        
        similar_cases.append({
            "case_id": str(item["case"].id),
            "case_title": item["case"].title,
            "court": "Supreme Court", # Fixed to standard court display for MVP
            "judgment_date": item["case"].decision_date.isoformat() if item["case"].decision_date else "Unknown",
            "similarity_score": round(sim_score, 2),
            "distance": round(dist, 4),
            "matched_chunks": [
                {
                    "chunk_id": str(item["chunk"].id),
                    "page_number": item["page_number"],
                    "excerpt": item["excerpt"]
                }
            ]
        })
        
    return {
        "case_id": str(case_id),
        "case_title": case.title,
        "similar_cases": similar_cases,
        "message": "No sufficiently similar cases found." if not similar_cases else ""
    }


@router.post("/{case_id}/citations/extract")
async def extract_case_citations(case_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    case = await db.get(Case, case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found.")
        
    chunks_data = await get_case_chunks(case_id, db)
    
    # Extract using the light model per instructions
    generator = GeminiGenerator(is_lightweight=True)
    citations_text = await generator.extract_citations(chunks_data)
    
    try:
        citations_json = json.loads(citations_text)
    except Exception as e:
        logger.error(f"Failed to parse citations JSON: {e}\n{citations_text}")
        raise HTTPException(status_code=500, detail="Failed to parse LLM citation output as JSON.")
        
    if not isinstance(citations_json, list):
        citations_json = []

    # Map chunk text for validation
    chunk_text_map = {str(c["id"]): c["content"] for c in chunks_data}
    
    stats = {
        "extracted": len(citations_json),
        "resolved": 0,
        "unresolved": 0,
        "rejected": 0,
        "case_id": str(case_id)
    }
    
    saved_citations = []
    
    for c_data in citations_json:
        chunk_id_str = c_data.get("source_chunk_id")
        citation_text = c_data.get("citation_text", "")
        target_title = c_data.get("target_case_title", "Unknown")
        
        # 1. VALIDATION: Check if citation_text is actually in the chunk (normalized)
        if not chunk_id_str or chunk_id_str not in chunk_text_map:
            stats["rejected"] += 1
            continue
            
        source_text = chunk_text_map[chunk_id_str]
        
        # Normalize whitespace and punctuation for validation
        def normalize(t):
            t = re.sub(r'\s+', '', t)
            t = re.sub(r'[^a-zA-Z0-9]', '', t)
            return t.lower()
            
        if normalize(citation_text) not in normalize(source_text):
            stats["rejected"] += 1
            continue
            
        # 2. RESOLUTION: Find target case
        # Simple resolution by exact title or case_number (we can do basic ilike)
        target_case_id = None
        if target_title and target_title != "Unknown":
            stmt = select(Case).where(
                or_(
                    func.lower(Case.title) == target_title.lower(),
                    Case.title.ilike(f"%{target_title}%")
                )
            ).limit(1)
            result = await db.execute(stmt)
            target_case = result.scalar_one_or_none()
            if target_case:
                target_case_id = target_case.id
                
        # 3. DEDUPLICATION: Check if this exact relationship already exists
        check_stmt = select(CaseCitation).where(
            and_(
                CaseCitation.source_case_id == case_id,
                CaseCitation.source_chunk_id == uuid.UUID(chunk_id_str),
                CaseCitation.citation_text == citation_text
            )
        )
        if target_case_id:
            check_stmt = check_stmt.where(CaseCitation.target_case_id == target_case_id)
            
        existing = await db.execute(check_stmt)
        if existing.scalar_one_or_none():
            # Already have this exact citation
            stats["extracted"] -= 1
            continue
            
        new_cit = CaseCitation(
            source_case_id=case_id,
            target_case_id=target_case_id,
            target_case_title=target_title,
            source_chunk_id=uuid.UUID(chunk_id_str),
            citation_text=citation_text,
            page_number=c_data.get("page_number"),
            relationship_type=c_data.get("relationship_type", "cited"),
            confidence_score=float(c_data.get("confidence_score", 0.0))
        )
        db.add(new_cit)
        
        if target_case_id:
            stats["resolved"] += 1
        else:
            stats["unresolved"] += 1
            
    await db.commit()
    
    return stats


@router.get("/{case_id}/citations")
async def get_case_citations(case_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    case = await db.get(Case, case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found.")
        
    stmt = select(CaseCitation).where(CaseCitation.source_case_id == case_id)
    result = await db.execute(stmt)
    citations = result.scalars().all()
    
    resolved = []
    unresolved = []
    
    for cit in citations:
        cit_dict = {
            "id": str(cit.id),
            "target_case_id": str(cit.target_case_id) if cit.target_case_id else None,
            "target_case_title": cit.target_case_title,
            "source_chunk_id": str(cit.source_chunk_id),
            "citation_text": cit.citation_text,
            "page_number": cit.page_number,
            "relationship_type": cit.relationship_type,
            "confidence_score": cit.confidence_score
        }
        if cit.target_case_id:
            resolved.append(cit_dict)
        else:
            unresolved.append(cit_dict)
            
    return {
        "resolved": resolved,
        "unresolved": unresolved
    }


@router.get("/{case_id}/cited-by")
async def get_case_cited_by(case_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    case = await db.get(Case, case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found.")
        
    # Find all CaseCitations where target_case_id == this case
    stmt = select(CaseCitation).where(CaseCitation.target_case_id == case_id)
    result = await db.execute(stmt)
    citations = result.scalars().all()
    
    # We need the source cases for these citations
    cited_by_cases = []
    for cit in citations:
        source_case = await db.get(Case, cit.source_case_id)
        if source_case:
            cited_by_cases.append({
                "id": str(cit.id),
                "source_case_id": str(cit.source_case_id),
                "source_case_title": source_case.title,
                "source_chunk_id": str(cit.source_chunk_id),
                "citation_text": cit.citation_text,
                "page_number": cit.page_number,
                "relationship_type": cit.relationship_type,
                "confidence_score": cit.confidence_score
            })
            
    return cited_by_cases
