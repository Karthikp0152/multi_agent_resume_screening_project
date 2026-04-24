"""
Text extraction module for the Smart Resume Screening System.

This module provides the TextExtractor class for converting PDF and text files
to clean, normalized text suitable for downstream processing.
"""

import re
import logging
from pathlib import Path
from typing import Optional

# PDF extraction libraries
try:
    import pdfplumber
    PDFPLUMBER_AVAILABLE = True
except ImportError:
    PDFPLUMBER_AVAILABLE = False

try:
    from pypdf import PdfReader
    PYPDF_AVAILABLE = True
except ImportError:
    PYPDF_AVAILABLE = False


# Custom exceptions
class PDFExtractionError(Exception):
    """Raised when PDF text extraction fails."""
    pass


class UnsupportedFormatError(Exception):
    """Raised when file format is not supported."""
    pass


logger = logging.getLogger(__name__)


class TextExtractor:
    """Extracts and cleans text from PDF and text files.
    
    This class handles text extraction from multiple file formats with fallback
    mechanisms and comprehensive text cleaning capabilities.
    
    Attributes:
        SUPPORTED_FORMATS: Set of supported file extensions
    """
    
    SUPPORTED_FORMATS = {'.pdf', '.txt'}
    
    def __init__(self):
        """Initialize the TextExtractor."""
        if not PDFPLUMBER_AVAILABLE and not PYPDF_AVAILABLE:
            logger.warning("No PDF extraction libraries available. PDF processing will fail.")
    
    def validate_format(self, file_path: str) -> bool:
        """Check if file format is supported.
        
        Args:
            file_path: Path to the file to validate
            
        Returns:
            True if format is supported, False otherwise
        """
        path = Path(file_path)
        return path.suffix.lower() in self.SUPPORTED_FORMATS
    
    def extract_from_pdf(self, pdf_path: str) -> str:
        """Extract text from PDF using pdfplumber with pypdf fallback.
        
        Attempts to extract text using pdfplumber first for better layout
        preservation. If pdfplumber fails or is unavailable, falls back to pypdf.
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            Extracted text from the PDF
            
        Raises:
            FileNotFoundError: If the PDF file does not exist
            PDFExtractionError: If text extraction fails with all methods
            UnsupportedFormatError: If file is not a PDF
        """
        path = Path(pdf_path)
        
        # Check file exists
        if not path.exists():
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
        
        # Check file format
        if path.suffix.lower() != '.pdf':
            raise UnsupportedFormatError(
                f"File is not a PDF: {pdf_path}. Supported formats: {self.SUPPORTED_FORMATS}"
            )
        
        text = None
        
        # Try pdfplumber first (primary method)
        if PDFPLUMBER_AVAILABLE:
            try:
                logger.debug(f"Attempting PDF extraction with pdfplumber: {pdf_path}")
                with pdfplumber.open(pdf_path) as pdf:
                    text_parts = []
                    for page in pdf.pages:
                        page_text = page.extract_text()
                        if page_text:
                            text_parts.append(page_text)
                    text = "\n".join(text_parts)
                
                if text and text.strip():
                    logger.info(f"Successfully extracted text with pdfplumber: {pdf_path}")
                    return text
                else:
                    logger.warning(f"pdfplumber extracted empty text from: {pdf_path}")
            except Exception as e:
                logger.warning(f"pdfplumber extraction failed for {pdf_path}: {e}")
        
        # Fallback to pypdf
        if PYPDF_AVAILABLE:
            try:
                logger.debug(f"Attempting PDF extraction with pypdf: {pdf_path}")
                reader = PdfReader(pdf_path)
                text_parts = []
                for page in reader.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text_parts.append(page_text)
                text = "\n".join(text_parts)
                
                if text and text.strip():
                    logger.info(f"Successfully extracted text with pypdf: {pdf_path}")
                    return text
                else:
                    logger.warning(f"pypdf extracted empty text from: {pdf_path}")
            except Exception as e:
                logger.error(f"pypdf extraction failed for {pdf_path}: {e}")
        
        # If we get here, all extraction methods failed
        if not PDFPLUMBER_AVAILABLE and not PYPDF_AVAILABLE:
            raise PDFExtractionError(
                "No PDF extraction libraries available. Install pdfplumber or pypdf."
            )
        
        raise PDFExtractionError(
            f"Failed to extract text from PDF: {pdf_path}. "
            "The file may be corrupted, encrypted, or contain only images."
        )
    
    def extract_from_text(self, text_path: str) -> str:
        """Load text from plain text file.
        
        Args:
            text_path: Path to the text file
            
        Returns:
            Content of the text file
            
        Raises:
            FileNotFoundError: If the text file does not exist
            UnsupportedFormatError: If file is not a text file
        """
        path = Path(text_path)
        
        # Check file exists
        if not path.exists():
            raise FileNotFoundError(f"Text file not found: {text_path}")
        
        # Check file format
        if path.suffix.lower() != '.txt':
            raise UnsupportedFormatError(
                f"File is not a text file: {text_path}. Supported formats: {self.SUPPORTED_FORMATS}"
            )
        
        try:
            logger.debug(f"Reading text file: {text_path}")
            with open(text_path, 'r', encoding='utf-8') as f:
                text = f.read()
            logger.info(f"Successfully read text file: {text_path}")
            return text
        except UnicodeDecodeError:
            # Try with different encoding
            logger.warning(f"UTF-8 decoding failed, trying latin-1 for: {text_path}")
            try:
                with open(text_path, 'r', encoding='latin-1') as f:
                    text = f.read()
                logger.info(f"Successfully read text file with latin-1: {text_path}")
                return text
            except Exception as e:
                raise PDFExtractionError(f"Failed to read text file {text_path}: {e}")
        except Exception as e:
            raise PDFExtractionError(f"Failed to read text file {text_path}: {e}")
    
    def clean_text(self, raw_text: str) -> str:
        """Remove special characters and normalize whitespace.
        
        Applies regex-based cleaning to remove non-alphanumeric characters
        (except standard punctuation) and normalizes whitespace by collapsing
        multiple spaces and normalizing line breaks.
        
        Args:
            raw_text: Raw text to clean
            
        Returns:
            Cleaned and normalized text
        """
        if not raw_text:
            return ""
        
        # Remove special characters, keep alphanumeric and standard punctuation
        # Standard punctuation: . , ! ? ; : - ' " ( ) [ ] / @
        text = re.sub(r'[^a-zA-Z0-9\s.,!?;:\-\'"()\[\]/@]+', ' ', raw_text)
        
        # Normalize line breaks (convert multiple newlines to single newline)
        text = re.sub(r'\n\s*\n+', '\n\n', text)
        
        # Collapse multiple spaces into single space
        text = re.sub(r'[ \t]+', ' ', text)
        
        # Remove leading/trailing whitespace from each line
        lines = [line.strip() for line in text.split('\n')]
        text = '\n'.join(lines)
        
        # Remove leading/trailing whitespace from entire text
        text = text.strip()
        
        return text
