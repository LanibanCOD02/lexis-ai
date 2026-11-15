"""
Text cleaning module for legal PDF extraction.
Removes headers, footers, watermarks, fixes line breaks, and applies Unicode normalization.
"""
import re
import unicodedata

def normalize_unicode(text: str) -> str:
    """Applies NFKC normalization to fix broken ligatures."""
    return unicodedata.normalize("NFKC", text)

def remove_page_numbers_and_watermarks(text: str) -> str:
    """Removes standard page number formats and REPORTABLE watermarks."""
    text = re.sub(r'(?i)page\s+\d+\s+of\s+\d+', '', text)
    text = re.sub(r'^\s*\d+\s*$', '', text, flags=re.MULTILINE)
    text = re.sub(r'(?i)\bREPORTABLE\b', '', text)
    return text

def fix_whitespace_and_paragraphs(text: str) -> str:
    """
    Consolidates multiple spaces and merges unnatural line breaks.
    If a line does not end with punctuation, it is merged with the next line.
    """
    # Merge broken lines that don't end in punctuation
    text = re.sub(r'(?<![.:!?])\n+', ' ', text)
    # Consolidate multiple spaces
    text = re.sub(r'[ \t]+', ' ', text)
    # Ensure actual paragraphs are separated properly
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()

def clean_extracted_text(raw_text: str) -> str:
    """
    Executes the full cleaning pipeline on raw extracted text.
    
    Args:
        raw_text (str): The raw text extracted from a document page.
        
    Returns:
        str: Cleaned, normalized text.
    """
    if not raw_text:
        return ""
    text = normalize_unicode(raw_text)
    text = remove_page_numbers_and_watermarks(text)
    text = fix_whitespace_and_paragraphs(text)
    return text
