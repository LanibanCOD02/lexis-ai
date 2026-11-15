"""
Recursive Character Text Splitter module.
Splits cleaned text into overlapping chunks optimized for the embedding model.
"""
from typing import List, Dict, Any
from langchain_text_splitters import RecursiveCharacterTextSplitter

# Assuming 1 token ~= 4 characters. 800 tokens = 3200 characters.
CHUNK_SIZE = 3200
CHUNK_OVERLAP = 600

class DocumentChunker:
    """
    Chunks cleaned document text into overlapping segments.
    """
    def __init__(self, chunk_size: int = CHUNK_SIZE, chunk_overlap: int = CHUNK_OVERLAP):
        """
        Initializes the RecursiveCharacterTextSplitter.
        """
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\n\n", "\n", ".", " ", ""]
        )

    def chunk_pages(self, cleaned_pages: List[Dict[str, Any]], document_metadata: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Splits a list of cleaned pages into overlapping chunks and injects metadata.
        
        Args:
            cleaned_pages (List[Dict]): List containing page_number and text.
            document_metadata (Dict): Metadata (Case ID, Court, etc.) to attach to each chunk.
            
        Returns:
            List[Dict[str, Any]]: The finalized chunk payloads ready for embedding.
        """
        chunks = []
        global_chunk_index = 0
        
        for page in cleaned_pages:
            text = page.get("text", "")
            page_num = page.get("page_number", 0)
            
            if not text.strip():
                continue
                
            split_texts = self.splitter.split_text(text)
            
            for split in split_texts:
                # Inject metadata directly into the chunk context to improve semantic retrieval
                metadata_header = (
                    f"Case: {document_metadata.get('case_title', 'Unknown')}, "
                    f"Court: {document_metadata.get('court_name', 'Unknown')}, "
                    f"Page: {page_num}\n---\n"
                )
                
                final_content = metadata_header + split
                
                chunks.append({
                    "chunk_index": global_chunk_index,
                    "page_number": page_num,
                    "content": final_content,
                    # Approximate token count (chars / 4)
                    "token_count": len(final_content) // 4
                })
                global_chunk_index += 1
                
        return chunks
