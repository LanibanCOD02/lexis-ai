from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from app.schemas.chat import ChatRequest, ChatResponse, Citation
from app.rag.embedder import DocumentEmbedder
from app.rag.faiss_index import VectorStore
from app.rag.generator import GeminiGenerator
from app.db.session import get_db
from app.models.rag import Embedding, Chunk, Document
from app.models.core import Case

router = APIRouter()

@router.post("/", response_model=ChatResponse)
async def chat_query(request: ChatRequest, db: AsyncSession = Depends(get_db)):
    """
    Accepts a legal query, performs semantic FAISS search, 
    retrieves SQL chunk data, and generates an LLM answer with strict legal citations.
    """
    # 1. Embed query
    embedder = DocumentEmbedder()
    query_chunk = [{"content": request.query}]
    query_vector = embedder.embed_chunks(query_chunk)[0]["embedding"]
    
    # 2. Search FAISS
    vstore = VectorStore()
    try:
        results = vstore.search(query_vector, top_k=5)
    except Exception as e:
        # E.g. FAISS index not initialized or empty
        return ChatResponse(answer="Insufficient evidence found in the index.", citations=[])
    
    if not results:
        return ChatResponse(answer="Insufficient evidence found in the index.", citations=[])
        
    vector_ids = [vid for vid, dist in results]
    
    # 3. Retrieve metadata from SQL using IDs
    retrieved_chunks = []
    
    # Query the Embeddings -> Chunk -> Document -> Case
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
    
    if not embeddings:
         return ChatResponse(answer="Insufficient evidence found in the index.", citations=[])
         
    for emb in embeddings:
        chunk = emb.chunk
        doc = chunk.document
        case = doc.case
        retrieved_chunks.append({
            "id": str(chunk.id),
            "case_title": case.title,
            "court_name": "Court",  # We don't eagerly load Court here, keeping it generic
            "page_number": chunk.chunk_index + 1,  # Approximate
            "content": chunk.content
        })
        
    if not retrieved_chunks:
        return ChatResponse(answer="Insufficient evidence found in the database.", citations=[])
        
    # 4. Generate Answer
    generator = GeminiGenerator()
    answer = await generator.generate_answer(request.query, retrieved_chunks)
    
    # 5. Extract citations dynamically based on Gemini response tags
    citations = []
    for chunk in retrieved_chunks:
        if f"[{chunk['id']}]" in answer:
            citations.append(Citation(
                chunk_id=chunk["id"],
                text_snippet=chunk["content"][:100],
                page_number=chunk["page_number"],
                case_title=chunk["case_title"]
            ))
            
    return ChatResponse(answer=answer, citations=citations)
