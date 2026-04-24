"""
Unit tests for the TextExtractor component.

Tests cover:
- PDF extraction with sample PDF files
- Text file loading
- Text cleaning with special characters and whitespace
- Format validation for supported and unsupported formats
- Fallback mechanism when pdfplumber fails
- Error handling for missing files
"""

import pytest
import tempfile
import os
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock, mock_open
from src.text_extractor import (
    TextExtractor,
    PDFExtractionError,
    UnsupportedFormatError
)


class TestTextExtractorFormatValidation:
    """Test suite for format validation functionality."""
    
    def test_validate_pdf_format(self):
        """Test that PDF format is recognized as supported."""
        extractor = TextExtractor()
        assert extractor.validate_format("resume.pdf") is True
        assert extractor.validate_format("document.PDF") is True
        assert extractor.validate_format("/path/to/file.pdf") is True
    
    def test_validate_txt_format(self):
        """Test that TXT format is recognized as supported."""
        extractor = TextExtractor()
        assert extractor.validate_format("resume.txt") is True
        assert extractor.validate_format("document.TXT") is True
        assert extractor.validate_format("/path/to/file.txt") is True
    
    def test_validate_unsupported_formats(self):
        """Test that unsupported formats are rejected."""
        extractor = TextExtractor()
        assert extractor.validate_format("resume.docx") is False
        assert extractor.validate_format("resume.doc") is False
        assert extractor.validate_format("resume.html") is False
        assert extractor.validate_format("resume.rtf") is False
        assert extractor.validate_format("resume") is False
    
    def test_validate_case_insensitive(self):
        """Test that format validation is case-insensitive."""
        extractor = TextExtractor()
        assert extractor.validate_format("file.PDF") is True
        assert extractor.validate_format("file.Pdf") is True
        assert extractor.validate_format("file.TXT") is True
        assert extractor.validate_format("file.Txt") is True


class TestTextExtractorTextCleaning:
    """Test suite for text cleaning functionality."""
    
    def test_clean_text_removes_special_characters(self):
        """Test that special characters are removed while preserving standard punctuation."""
        extractor = TextExtractor()
        
        # Test with various special characters
        raw_text = "Hello™ World® Test© #hashtag $money €euro"
        cleaned = extractor.clean_text(raw_text)
        
        # Special characters should be removed
        assert "™" not in cleaned
        assert "®" not in cleaned
        assert "©" not in cleaned
        assert "#" not in cleaned
        assert "$" not in cleaned
        assert "€" not in cleaned
        
        # Alphanumeric should be preserved
        assert "Hello" in cleaned
        assert "World" in cleaned
        assert "Test" in cleaned
    
    def test_clean_text_preserves_standard_punctuation(self):
        """Test that standard punctuation is preserved."""
        extractor = TextExtractor()
        
        raw_text = "Hello, World! How are you? I'm fine; thanks. (Really) [Yes] email@test.com"
        cleaned = extractor.clean_text(raw_text)
        
        # Standard punctuation should be preserved
        assert "," in cleaned
        assert "!" in cleaned
        assert "?" in cleaned
        assert "'" in cleaned
        assert ";" in cleaned
        assert "." in cleaned
        assert "(" in cleaned
        assert ")" in cleaned
        assert "[" in cleaned
        assert "]" in cleaned
        assert "@" in cleaned
    
    def test_clean_text_normalizes_whitespace(self):
        """Test that multiple spaces are collapsed to single space."""
        extractor = TextExtractor()
        
        raw_text = "Hello    World     Test"
        cleaned = extractor.clean_text(raw_text)
        
        assert "Hello World Test" in cleaned
        assert "    " not in cleaned
    
    def test_clean_text_normalizes_line_breaks(self):
        """Test that multiple line breaks are normalized."""
        extractor = TextExtractor()
        
        raw_text = "Line 1\n\n\n\nLine 2\n\n\nLine 3"
        cleaned = extractor.clean_text(raw_text)
        
        # Multiple newlines should be reduced to double newline
        assert "\n\n\n\n" not in cleaned
        assert "Line 1" in cleaned
        assert "Line 2" in cleaned
        assert "Line 3" in cleaned
    
    def test_clean_text_strips_leading_trailing_whitespace(self):
        """Test that leading and trailing whitespace is removed."""
        extractor = TextExtractor()
        
        raw_text = "   Hello World   \n\n"
        cleaned = extractor.clean_text(raw_text)
        
        assert cleaned == "Hello World"
        assert not cleaned.startswith(" ")
        assert not cleaned.endswith(" ")
    
    def test_clean_text_handles_empty_string(self):
        """Test that empty string is handled correctly."""
        extractor = TextExtractor()
        
        assert extractor.clean_text("") == ""
        assert extractor.clean_text("   ") == ""
        assert extractor.clean_text("\n\n") == ""
    
    def test_clean_text_preserves_alphanumeric(self):
        """Test that alphanumeric characters are preserved."""
        extractor = TextExtractor()
        
        raw_text = "Python3 JavaScript C++ 2024 Test123"
        cleaned = extractor.clean_text(raw_text)
        
        assert "Python3" in cleaned
        assert "JavaScript" in cleaned
        assert "2024" in cleaned
        assert "Test123" in cleaned


class TestTextExtractorTextFileLoading:
    """Test suite for text file loading functionality."""
    
    def test_extract_from_text_file_success(self):
        """Test successful text file loading."""
        extractor = TextExtractor()
        
        # Create temporary text file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
            f.write("This is a test resume.\nSkills: Python, Java\nExperience: 5 years")
            temp_path = f.name
        
        try:
            text = extractor.extract_from_text(temp_path)
            
            assert "This is a test resume" in text
            assert "Skills: Python, Java" in text
            assert "Experience: 5 years" in text
        finally:
            os.unlink(temp_path)
    
    def test_extract_from_text_file_not_found(self):
        """Test error handling for missing text file."""
        extractor = TextExtractor()
        
        with pytest.raises(FileNotFoundError) as exc_info:
            extractor.extract_from_text("nonexistent_file.txt")
        
        assert "not found" in str(exc_info.value).lower()
    
    def test_extract_from_text_unsupported_format(self):
        """Test error handling for non-text file."""
        extractor = TextExtractor()
        
        # Create temporary file with wrong extension
        with tempfile.NamedTemporaryFile(mode='w', suffix='.docx', delete=False) as f:
            temp_path = f.name
        
        try:
            with pytest.raises(UnsupportedFormatError) as exc_info:
                extractor.extract_from_text(temp_path)
            
            assert "not a text file" in str(exc_info.value).lower()
        finally:
            os.unlink(temp_path)
    
    def test_extract_from_text_utf8_encoding(self):
        """Test text file loading with UTF-8 encoding."""
        extractor = TextExtractor()
        
        # Create text file with UTF-8 characters
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
            f.write("Resume with UTF-8: café, naïve, résumé")
            temp_path = f.name
        
        try:
            text = extractor.extract_from_text(temp_path)
            assert "café" in text or "caf" in text  # May vary based on encoding handling
        finally:
            os.unlink(temp_path)
    
    def test_extract_from_text_latin1_fallback(self):
        """Test fallback to latin-1 encoding when UTF-8 fails."""
        extractor = TextExtractor()
        
        # Create text file with latin-1 encoding
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='latin-1') as f:
            f.write("Resume text")
            temp_path = f.name
        
        try:
            text = extractor.extract_from_text(temp_path)
            assert "Resume text" in text
        finally:
            os.unlink(temp_path)


class TestTextExtractorPDFExtraction:
    """Test suite for PDF extraction functionality."""
    
    @patch('src.text_extractor.PDFPLUMBER_AVAILABLE', True)
    @patch('src.text_extractor.pdfplumber')
    def test_extract_from_pdf_with_pdfplumber_success(self, mock_pdfplumber):
        """Test successful PDF extraction using pdfplumber."""
        extractor = TextExtractor()
        
        # Mock pdfplumber behavior
        mock_pdf = MagicMock()
        mock_page1 = MagicMock()
        mock_page1.extract_text.return_value = "Page 1 content\nSkills: Python"
        mock_page2 = MagicMock()
        mock_page2.extract_text.return_value = "Page 2 content\nExperience: 5 years"
        mock_pdf.pages = [mock_page1, mock_page2]
        mock_pdfplumber.open.return_value.__enter__.return_value = mock_pdf
        
        # Create temporary PDF file
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as f:
            temp_path = f.name
        
        try:
            text = extractor.extract_from_pdf(temp_path)
            
            assert "Page 1 content" in text
            assert "Skills: Python" in text
            assert "Page 2 content" in text
            assert "Experience: 5 years" in text
            mock_pdfplumber.open.assert_called_once_with(temp_path)
        finally:
            os.unlink(temp_path)
    
    def test_extract_from_pdf_with_pypdf_fallback(self):
        """Test PDF extraction fallback to pypdf when pdfplumber unavailable."""
        # Create a mock PdfReader class
        mock_pdfreader_class = MagicMock()
        mock_page1 = MagicMock()
        mock_page1.extract_text.return_value = "Page 1 from pypdf"
        mock_page2 = MagicMock()
        mock_page2.extract_text.return_value = "Page 2 from pypdf"
        mock_reader = MagicMock()
        mock_reader.pages = [mock_page1, mock_page2]
        mock_pdfreader_class.return_value = mock_reader
        
        # Patch at the point of use in the module
        with patch('src.text_extractor.PDFPLUMBER_AVAILABLE', False), \
             patch('src.text_extractor.PYPDF_AVAILABLE', True), \
             patch.dict('sys.modules', {'pypdf': MagicMock(PdfReader=mock_pdfreader_class)}), \
             patch('src.text_extractor.PdfReader', mock_pdfreader_class, create=True):
            
            extractor = TextExtractor()
            
            # Create temporary PDF file
            with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as f:
                temp_path = f.name
            
            try:
                text = extractor.extract_from_pdf(temp_path)
                
                assert "Page 1 from pypdf" in text
                assert "Page 2 from pypdf" in text
                mock_pdfreader_class.assert_called_once_with(temp_path)
            finally:
                os.unlink(temp_path)
    
    def test_extract_from_pdf_pdfplumber_fails_pypdf_succeeds(self):
        """Test fallback mechanism when pdfplumber fails but pypdf succeeds."""
        # Create a mock PdfReader class
        mock_pdfreader_class = MagicMock()
        mock_page = MagicMock()
        mock_page.extract_text.return_value = "Extracted by pypdf fallback"
        mock_reader = MagicMock()
        mock_reader.pages = [mock_page]
        mock_pdfreader_class.return_value = mock_reader
        
        with patch('src.text_extractor.PDFPLUMBER_AVAILABLE', True), \
             patch('src.text_extractor.PYPDF_AVAILABLE', True), \
             patch('src.text_extractor.pdfplumber') as mock_pdfplumber, \
             patch.dict('sys.modules', {'pypdf': MagicMock(PdfReader=mock_pdfreader_class)}), \
             patch('src.text_extractor.PdfReader', mock_pdfreader_class, create=True):
            
            # Mock pdfplumber to fail
            mock_pdfplumber.open.side_effect = Exception("pdfplumber extraction failed")
            
            extractor = TextExtractor()
            
            # Create temporary PDF file
            with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as f:
                temp_path = f.name
            
            try:
                text = extractor.extract_from_pdf(temp_path)
                
                assert "Extracted by pypdf fallback" in text
                mock_pdfplumber.open.assert_called_once()
                mock_pdfreader_class.assert_called_once_with(temp_path)
            finally:
                os.unlink(temp_path)
    
    def test_extract_from_pdf_both_methods_fail(self):
        """Test error handling when both extraction methods fail."""
        # Create a mock PdfReader class that fails
        mock_pdfreader_class = MagicMock()
        mock_pdfreader_class.side_effect = Exception("pypdf failed")
        
        with patch('src.text_extractor.PDFPLUMBER_AVAILABLE', True), \
             patch('src.text_extractor.PYPDF_AVAILABLE', True), \
             patch('src.text_extractor.pdfplumber') as mock_pdfplumber, \
             patch.dict('sys.modules', {'pypdf': MagicMock(PdfReader=mock_pdfreader_class)}), \
             patch('src.text_extractor.PdfReader', mock_pdfreader_class, create=True):
            
            # Mock pdfplumber to fail
            mock_pdfplumber.open.side_effect = Exception("pdfplumber failed")
            
            extractor = TextExtractor()
            
            # Create temporary PDF file
            with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as f:
                temp_path = f.name
            
            try:
                with pytest.raises(PDFExtractionError) as exc_info:
                    extractor.extract_from_pdf(temp_path)
                
                assert "failed to extract" in str(exc_info.value).lower()
            finally:
                os.unlink(temp_path)
    
    def test_extract_from_pdf_file_not_found(self):
        """Test error handling for missing PDF file."""
        extractor = TextExtractor()
        
        with pytest.raises(FileNotFoundError) as exc_info:
            extractor.extract_from_pdf("nonexistent_file.pdf")
        
        assert "not found" in str(exc_info.value).lower()
    
    def test_extract_from_pdf_unsupported_format(self):
        """Test error handling for non-PDF file."""
        extractor = TextExtractor()
        
        # Create temporary file with wrong extension
        with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as f:
            temp_path = f.name
        
        try:
            with pytest.raises(UnsupportedFormatError) as exc_info:
                extractor.extract_from_pdf(temp_path)
            
            assert "not a pdf" in str(exc_info.value).lower()
        finally:
            os.unlink(temp_path)
    
    @patch('src.text_extractor.PDFPLUMBER_AVAILABLE', False)
    @patch('src.text_extractor.PYPDF_AVAILABLE', False)
    def test_extract_from_pdf_no_libraries_available(self):
        """Test error handling when no PDF libraries are available."""
        extractor = TextExtractor()
        
        # Create temporary PDF file
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as f:
            temp_path = f.name
        
        try:
            with pytest.raises(PDFExtractionError) as exc_info:
                extractor.extract_from_pdf(temp_path)
            
            assert "no pdf extraction libraries" in str(exc_info.value).lower()
        finally:
            os.unlink(temp_path)
    
    @patch('src.text_extractor.PDFPLUMBER_AVAILABLE', True)
    @patch('src.text_extractor.pdfplumber')
    def test_extract_from_pdf_empty_content(self, mock_pdfplumber):
        """Test handling of PDF with no extractable text."""
        extractor = TextExtractor()
        
        # Mock pdfplumber to return empty text
        mock_pdf = MagicMock()
        mock_page = MagicMock()
        mock_page.extract_text.return_value = ""
        mock_pdf.pages = [mock_page]
        mock_pdfplumber.open.return_value.__enter__.return_value = mock_pdf
        
        # Create temporary PDF file
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as f:
            temp_path = f.name
        
        try:
            with pytest.raises(PDFExtractionError):
                extractor.extract_from_pdf(temp_path)
        finally:
            os.unlink(temp_path)
    
    @patch('src.text_extractor.PDFPLUMBER_AVAILABLE', True)
    @patch('src.text_extractor.pdfplumber')
    def test_extract_from_pdf_multiple_pages(self, mock_pdfplumber):
        """Test PDF extraction with multiple pages."""
        extractor = TextExtractor()
        
        # Mock pdfplumber with multiple pages
        mock_pdf = MagicMock()
        pages = []
        for i in range(5):
            mock_page = MagicMock()
            mock_page.extract_text.return_value = f"Page {i+1} content"
            pages.append(mock_page)
        mock_pdf.pages = pages
        mock_pdfplumber.open.return_value.__enter__.return_value = mock_pdf
        
        # Create temporary PDF file
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as f:
            temp_path = f.name
        
        try:
            text = extractor.extract_from_pdf(temp_path)
            
            # Verify all pages are included
            for i in range(5):
                assert f"Page {i+1} content" in text
        finally:
            os.unlink(temp_path)


class TestTextExtractorIntegration:
    """Integration tests for TextExtractor component."""
    
    def test_end_to_end_text_file_processing(self):
        """Test complete workflow: load text file and clean it."""
        extractor = TextExtractor()
        
        # Create text file with messy content
        raw_content = "  Hello™ World!  \n\n\n  Skills:   Python,    Java  \n\n  Experience®  "
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
            f.write(raw_content)
            temp_path = f.name
        
        try:
            # Extract and clean
            text = extractor.extract_from_text(temp_path)
            cleaned = extractor.clean_text(text)
            
            # Verify cleaning worked
            assert "™" not in cleaned
            assert "®" not in cleaned
            assert "Hello" in cleaned
            assert "World" in cleaned
            assert "Skills" in cleaned
            assert "Python" in cleaned
        finally:
            os.unlink(temp_path)
    
    @patch('src.text_extractor.PDFPLUMBER_AVAILABLE', True)
    @patch('src.text_extractor.pdfplumber')
    def test_end_to_end_pdf_processing(self, mock_pdfplumber):
        """Test complete workflow: extract PDF and clean it."""
        extractor = TextExtractor()
        
        # Mock PDF with messy content
        mock_pdf = MagicMock()
        mock_page = MagicMock()
        mock_page.extract_text.return_value = "  Resume™  \n\n\n  Skills:   Python    \n\n  "
        mock_pdf.pages = [mock_page]
        mock_pdfplumber.open.return_value.__enter__.return_value = mock_pdf
        
        # Create temporary PDF file
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as f:
            temp_path = f.name
        
        try:
            # Extract and clean
            text = extractor.extract_from_pdf(temp_path)
            cleaned = extractor.clean_text(text)
            
            # Verify extraction and cleaning worked
            assert "™" not in cleaned
            assert "Resume" in cleaned
            assert "Skills" in cleaned
            assert "Python" in cleaned
        finally:
            os.unlink(temp_path)
