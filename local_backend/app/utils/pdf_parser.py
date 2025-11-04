"""
PDF parsing utility
"""
import io
from typing import Optional
import logging

logger = logging.getLogger(__name__)

# Try multiple PDF libraries
PDF_LIBRARY = None

try:
    import pdfplumber
    PDF_LIBRARY = "pdfplumber"
    logger.info("Using pdfplumber for PDF parsing")
except ImportError:
    try:
        import PyPDF2
        PDF_LIBRARY = "pypdf2"
        logger.info("Using PyPDF2 for PDF parsing")
    except ImportError:
        logger.error("No PDF library available! Install pdfplumber or PyPDF2")


def extract_text_from_pdf(file_content: bytes) -> Optional[str]:
    """
    Extract text from PDF file
    
    Args:
        file_content: PDF file as bytes
        
    Returns:
        Extracted text or None if failed
    """
    if PDF_LIBRARY is None:
        logger.error("No PDF library available")
        return None
    
    try:
        if PDF_LIBRARY == "pdfplumber":
            with pdfplumber.open(io.BytesIO(file_content)) as pdf:
                text_parts = []
                for page in pdf.pages:
                    text = page.extract_text()
                    if text:
                        text_parts.append(text)
                
                return "\n\n".join(text_parts)
        
        elif PDF_LIBRARY == "pypdf2":
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(file_content))
            text_parts = []
            
            for page in pdf_reader.pages:
                text = page.extract_text()
                if text:
                    text_parts.append(text)
            
            return "\n\n".join(text_parts)
    
    except Exception as e:
        logger.error(f"Failed to extract PDF text: {e}")
        return None


def extract_text_from_file(filename: str, content: bytes) -> Optional[str]:
    """
    Extract text from various file formats
    
    Args:
        filename: Original filename
        content: File content as bytes
        
    Returns:
        Extracted text or None if failed
    """
    ext = filename.lower().split('.')[-1]
    
    if ext == 'pdf':
        return extract_text_from_pdf(content)
    
    elif ext in ['txt', 'md', 'markdown']:
        try:
            return content.decode('utf-8')
        except UnicodeDecodeError:
            try:
                return content.decode('latin-1')
            except Exception as e:
                logger.error(f"Failed to decode text file: {e}")
                return None
    
    else:
        logger.warning(f"Unsupported file format: {ext}")
        return None
