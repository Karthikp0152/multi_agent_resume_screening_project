"""Pytest configuration and shared fixtures for testing."""

import pytest
from pathlib import Path
import json
import tempfile
import shutil


@pytest.fixture
def temp_dir():
    """Create a temporary directory for test files."""
    temp_path = tempfile.mkdtemp()
    yield Path(temp_path)
    shutil.rmtree(temp_path)


@pytest.fixture
def sample_resume_text():
    """Sample resume text for testing."""
    return """
    John Doe
    Software Engineer
    
    SKILLS
    Python, JavaScript, React, Node.js, Machine Learning, SQL, Docker, AWS
    
    EXPERIENCE
    Senior Software Engineer at Tech Corp (2020-2023)
    - Developed web applications using React and Node.js
    - Implemented machine learning models for data analysis
    - Managed cloud infrastructure on AWS
    
    Software Engineer at StartupXYZ (2018-2020)
    - Built RESTful APIs using Python and Flask
    - Worked with PostgreSQL databases
    - Deployed applications using Docker
    
    EDUCATION
    Bachelor of Science in Computer Science
    University of Technology (2014-2018)
    
    PROJECTS
    - E-commerce Platform: Built using React, Node.js, and MongoDB
    - ML Image Classifier: Developed using TensorFlow and Python
    """


@pytest.fixture
def sample_skills():
    """Sample skill list for testing."""
    return [
        "Python",
        "JavaScript",
        "React",
        "Node.js",
        "Machine Learning",
        "SQL",
        "Docker",
        "AWS"
    ]


@pytest.fixture
def sample_job_requirements():
    """Sample job requirements for testing."""
    return [
        "Python",
        "Machine Learning",
        "TensorFlow",
        "Docker",
        "AWS",
        "SQL"
    ]


@pytest.fixture
def skill_aliases():
    """Sample skill alias dictionary for testing."""
    return {
        "js": "JavaScript",
        "ml": "Machine Learning",
        "py": "Python",
        "react.js": "React",
        "nodejs": "Node.js"
    }


@pytest.fixture
def config_dir(temp_dir):
    """Create a temporary config directory with test configuration files."""
    config_path = temp_dir / "config"
    config_path.mkdir()
    
    # Create skill aliases file
    aliases = {
        "aliases": {
            "js": "JavaScript",
            "ml": "Machine Learning",
            "py": "Python"
        }
    }
    with open(config_path / "skill_aliases.json", "w") as f:
        json.dump(aliases, f)
    
    # Create job categories file
    categories = {
        "categories": [
            "INFORMATION-TECHNOLOGY",
            "ENGINEERING",
            "HEALTHCARE"
        ]
    }
    with open(config_path / "job_categories.json", "w") as f:
        json.dump(categories, f)
    
    return config_path


@pytest.fixture
def sample_resume_sections():
    """Sample resume sections for testing."""
    return {
        "skills": "Python, JavaScript, React, Machine Learning",
        "experience": "Software Engineer at Tech Corp. Developed ML models.",
        "education": "BS in Computer Science",
        "projects": "Built e-commerce platform using React and Node.js",
        "raw_text": "Full resume text here..."
    }


@pytest.fixture
def fixtures_dir():
    """Return path to test fixtures directory."""
    return Path(__file__).parent / "fixtures"


@pytest.fixture
def sample_csv_path(fixtures_dir):
    """Return path to sample CSV file."""
    return fixtures_dir / "sample_data" / "sample_resumes.csv"


@pytest.fixture
def sample_pdf_resumes(fixtures_dir):
    """Return paths to sample PDF resume files."""
    pdf_dir = fixtures_dir / "sample_resumes" / "pdf"
    return {
        "accountant": pdf_dir / "accountant_sample.txt",
        "it_developer": pdf_dir / "it_developer_sample.txt",
        "healthcare": pdf_dir / "healthcare_nurse_sample.txt"
    }


@pytest.fixture
def expected_outputs(fixtures_dir):
    """Return paths to expected output JSON files."""
    output_dir = fixtures_dir / "expected_outputs"
    return {
        "accountant": output_dir / "accountant_expected.json",
        "it_developer": output_dir / "it_developer_expected.json"
    }


@pytest.fixture
def job_requirements(fixtures_dir):
    """Return paths to job requirement JSON files."""
    req_dir = fixtures_dir / "job_requirements"
    return {
        "accountant": req_dir / "accountant_job.json",
        "software_developer": req_dir / "software_developer_job.json",
        "nurse": req_dir / "nurse_job.json"
    }


@pytest.fixture
def validation_mapping(fixtures_dir):
    """Return path to PDF-CSV validation mapping file."""
    return fixtures_dir / "validation_data" / "pdf_csv_mapping.json"


@pytest.fixture
def load_job_requirements(job_requirements):
    """Load job requirements from JSON files."""
    def _load(job_type):
        with open(job_requirements[job_type]) as f:
            return json.load(f)
    return _load


@pytest.fixture
def load_expected_output(expected_outputs):
    """Load expected output from JSON files."""
    def _load(resume_type):
        with open(expected_outputs[resume_type]) as f:
            return json.load(f)
    return _load
