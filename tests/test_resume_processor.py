"""
Unit tests for ResumeProcessor component.
"""

import pytest
import tempfile
import csv
from pathlib import Path
from src.resume_processor import ResumeProcessor
from src.models import ProcessorConfig


@pytest.fixture
def processor_config():
    """Create a test processor configuration."""
    return ProcessorConfig(
        pdf_extractor="pdfplumber",
        nlp_model="en_core_web_sm",
        embedding_model="all-MiniLM-L6-v2",
        fuzzy_threshold=85,
        alias_dict_path="config/skill_aliases.json"
    )


@pytest.fixture
def processor(processor_config):
    """Create a ResumeProcessor instance for testing."""
    return ResumeProcessor(processor_config)


def test_processor_initialization(processor):
    """Test that processor initializes all components correctly."""
    assert processor.text_extractor is not None
    assert processor.section_parser is not None
    assert processor.skill_extractor is not None
    assert processor.skill_normalizer is not None
    assert processor.scoring_engine is not None


def test_load_from_csv_valid_file(processor):
    """Test loading resume data from a valid CSV file."""
    # Create a temporary CSV file
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['ID', 'Resume_str', 'Resume_html', 'Category'])
        writer.writeheader()
        writer.writerow({
            'ID': '12345',
            'Resume_str': 'Test resume with Python and Java skills',
            'Resume_html': '<p>Test resume</p>',
            'Category': 'SOFTWARE_ENGINEER'
        })
        csv_path = f.name
    
    try:
        # Load CSV data
        data = processor.load_from_csv(csv_path)
        
        # Verify data
        assert len(data) == 1
        assert data[0]['ID'] == '12345'
        assert 'Python' in data[0]['Resume_str']
        assert data[0]['Category'] == 'SOFTWARE_ENGINEER'
    finally:
        # Clean up
        Path(csv_path).unlink()


def test_load_from_csv_missing_file(processor):
    """Test that loading from non-existent CSV raises FileNotFoundError."""
    with pytest.raises(FileNotFoundError):
        processor.load_from_csv('nonexistent.csv')


def test_load_from_csv_missing_columns(processor):
    """Test that CSV with missing columns raises ValueError."""
    # Create a CSV with missing columns
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['ID', 'Resume_str'])  # Missing columns
        writer.writeheader()
        writer.writerow({'ID': '12345', 'Resume_str': 'Test'})
        csv_path = f.name
    
    try:
        with pytest.raises(ValueError, match="CSV missing required columns"):
            processor.load_from_csv(csv_path)
    finally:
        Path(csv_path).unlink()


def test_process_csv_data(processor):
    """Test processing resume data from CSV."""
    # Create a temporary CSV file
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['ID', 'Resume_str', 'Resume_html', 'Category'])
        writer.writeheader()
        writer.writerow({
            'ID': '12345',
            'Resume_str': '''
            SKILLS
            Python, Java, Machine Learning
            
            EXPERIENCE
            Software Engineer at Tech Corp
            Developed ML models using Python
            ''',
            'Resume_html': '<p>Test</p>',
            'Category': 'SOFTWARE_ENGINEER'
        })
        csv_path = f.name
    
    try:
        # Process CSV data
        resumes = processor.process_csv_data(csv_path)
        
        # Verify results
        assert len(resumes) == 1
        resume = resumes[0]
        
        assert resume.resume_id == '12345'
        assert resume.job_category == 'SOFTWARE_ENGINEER'
        assert resume.sections is not None
        assert resume.skills is not None
        assert len(resume.normalized_skills) > 0
        assert resume.metadata is not None
        assert resume.metadata.processing_time_ms > 0
    finally:
        Path(csv_path).unlink()


def test_validate_csv_extraction(processor):
    """Test CSV extraction validation."""
    # This test requires a real PDF file, so we'll create a mock scenario
    # In a real test, you would use actual PDF files
    csv_text = "Test resume with Python and Java skills in software engineering"
    
    # For this test, we'll just verify the method signature works
    # A full integration test would use real PDF files
    result = processor.validate_csv_extraction(
        pdf_path="archive/data/data/ACCOUNTANT/10554236.pdf",  # Use a real file from archive
        csv_resume_str=csv_text,
        resume_id="test_123"
    )
    
    # Verify result structure
    assert 'resume_id' in result
    assert 'pdf_length' in result
    assert 'csv_length' in result
    assert 'length_ratio' in result
    assert 'text_similarity' in result
    assert 'extraction_success' in result


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
