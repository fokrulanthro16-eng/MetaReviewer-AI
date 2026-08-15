"""
PDF and Document Parser Utility for MetaReviewer-AI.
Supports extracting clean plain text from uploaded PDF files using pdfplumber and pypdf fallbacks.
"""

import io
from typing import Tuple

def extract_text_from_pdf_bytes(pdf_bytes: bytes) -> Tuple[str, int]:
    """
    Extracts text from PDF byte content.
    Returns a tuple of (extracted_text, num_pages).
    """
    text_content = []
    num_pages = 0
    
    # Try pdfplumber first (better layout preservation for multi-column academic papers)
    try:
        import pdfplumber
        with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
            num_pages = len(pdf.pages)
            for page in pdf.pages:
                extracted = page.extract_text(layout=True) or page.extract_text()
                if extracted:
                    text_content.append(extracted)
        
        full_text = "\n\n".join(text_content).strip()
        if full_text:
            return full_text, num_pages
    except Exception:
        pass
    
    # Fallback to pypdf
    try:
        from pypdf import PdfReader
        reader = PdfReader(io.BytesIO(pdf_bytes))
        num_pages = len(reader.pages)
        for page in reader.pages:
            extracted = page.extract_text()
            if extracted:
                text_content.append(extracted)
        
        full_text = "\n\n".join(text_content).strip()
        return full_text, num_pages
    except Exception as e:
        raise ValueError(f"Failed to extract text from PDF: {str(e)}")

def extract_title_from_text(text: str, fallback_filename: str = "Research Paper") -> str:
    """
    Attempts to extract title from paper text (usually first non-empty lines).
    """
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    if lines:
        for line in lines[:5]:
            if len(line) > 10 and len(line) < 200:
                return line
    return fallback_filename
