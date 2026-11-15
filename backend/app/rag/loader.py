"""
PyMuPDF document loader.
Extracts raw text from PDF documents for RAG ingestion.
"""
import logging
from typing import List, Dict, Any
import fitz  # PyMuPDF

logger = logging.getLogger(__name__)

class PDFLoader:
    """
    Loads and extracts text from PDF documents using PyMuPDF.
    """
    def __init__(self, file_path: str):
        """
        Initialize the loader with a file path.
        
        Args:
            file_path (str): The absolute path to the PDF file.
        """
        self.file_path = file_path

    def extract_pages(self) -> List[Dict[str, Any]]:
        """
        Extracts text page by page.
        
        Returns:
            List[Dict[str, Any]]: A list of dictionaries containing page_number and raw_text.
        """
        extracted_data = []
        try:
            doc = fitz.open(self.file_path)
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                text = page.get_text("text")
                extracted_data.append({
                    "page_number": page_num + 1,
                    "raw_text": text
                })
            doc.close()
        except Exception as e:
            logger.error(f"Failed to extract text from {self.file_path}: {e}")
            raise
            
        return extracted_data
