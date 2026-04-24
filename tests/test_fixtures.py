"""Tests to validate test fixtures and sample data."""

import pytest
import json
import pandas as pd
from pathlib import Path


class TestFixturesExist:
    """Test that all fixture files exist and are accessible."""
    
    def test_fixtures_directory_exists(self, fixtures_dir):
        """Test that fixtures directory exists."""
        assert fixtures_dir.exists()
        assert fixtures_dir.is_dir()
    
    def test_sample_csv_exists(self, sample_csv_path):
        """Test that sample CSV file exists."""
        assert sample_csv_path.exists()
        assert sample_csv_path.is_file()
    
    def test_sample_pdf_resumes_exist(self, sample_pdf_resumes):
        """Test that all sample PDF resume files exist."""
        for resume_type, path in sample_pdf_resumes.items():
            assert path.exists(), f"Missing {resume_type} resume at {path}"
            assert path.is_file()
    
    def test_expected_outputs_exist(self, expected_outputs):
        """Test that expected output files exist."""
        for output_type, path in expected_outputs.items():
            assert path.exists(), f"Missing expected output for {output_type} at {path}"
            assert path.is_file()
    
    def test_job_requirements_exist(self, job_requirements):
        """Test that job requirement files exist."""
        for job_type, path in job_requirements.items():
            assert path.exists(), f"Missing job requirements for {job_type} at {path}"
            assert path.is_file()
    
    def test_validation_mapping_exists(self, validation_mapping):
        """Test that validation mapping file exists."""
        assert validation_mapping.exists()
        assert validation_mapping.is_file()


class TestCSVData:
    """Test sample CSV data structure and content."""
    
    def test_csv_loads_successfully(self, sample_csv_path):
        """Test that CSV file loads without errors."""
        df = pd.read_csv(sample_csv_path)
        assert df is not None
        assert len(df) > 0
    
    def test_csv_has_required_columns(self, sample_csv_path):
        """Test that CSV has all required columns."""
        df = pd.read_csv(sample_csv_path)
        required_columns = ["ID", "Resume_str", "Resume_html", "Category"]
        for col in required_columns:
            assert col in df.columns, f"Missing required column: {col}"
    
    def test_csv_has_expected_entries(self, sample_csv_path):
        """Test that CSV has expected number of entries."""
        df = pd.read_csv(sample_csv_path)
        assert len(df) == 5, "Expected 5 sample resume entries"
    
    def test_csv_categories_are_valid(self, sample_csv_path):
        """Test that all categories in CSV are valid."""
        df = pd.read_csv(sample_csv_path)
        valid_categories = [
            "ACCOUNTANT", "INFORMATION-TECHNOLOGY", "HEALTHCARE",
            "ENGINEERING", "SALES"
        ]
        for category in df["Category"]:
            assert category in valid_categories, f"Invalid category: {category}"
    
    def test_csv_ids_are_unique(self, sample_csv_path):
        """Test that all IDs in CSV are unique."""
        df = pd.read_csv(sample_csv_path)
        assert len(df["ID"]) == len(df["ID"].unique()), "Duplicate IDs found"
    
    def test_csv_resume_str_not_empty(self, sample_csv_path):
        """Test that Resume_str column has content."""
        df = pd.read_csv(sample_csv_path)
        for idx, resume_str in enumerate(df["Resume_str"]):
            assert resume_str and len(resume_str) > 0, f"Empty Resume_str at index {idx}"


class TestPDFResumes:
    """Test sample PDF resume files."""
    
    def test_pdf_resumes_have_content(self, sample_pdf_resumes):
        """Test that all PDF resume files have content."""
        for resume_type, path in sample_pdf_resumes.items():
            content = path.read_text()
            assert len(content) > 100, f"{resume_type} resume is too short"
    
    def test_pdf_resumes_have_skills_section(self, sample_pdf_resumes):
        """Test that PDF resumes contain SKILLS section."""
        for resume_type, path in sample_pdf_resumes.items():
            content = path.read_text().upper()
            assert "SKILL" in content, f"{resume_type} resume missing SKILLS section"
    
    def test_pdf_resumes_have_experience_section(self, sample_pdf_resumes):
        """Test that PDF resumes contain EXPERIENCE section."""
        for resume_type, path in sample_pdf_resumes.items():
            content = path.read_text().upper()
            assert "EXPERIENCE" in content, f"{resume_type} resume missing EXPERIENCE section"
    
    def test_pdf_resumes_have_education_section(self, sample_pdf_resumes):
        """Test that PDF resumes contain EDUCATION section."""
        for resume_type, path in sample_pdf_resumes.items():
            content = path.read_text().upper()
            assert "EDUCATION" in content, f"{resume_type} resume missing EDUCATION section"


class TestExpectedOutputs:
    """Test expected output JSON files."""
    
    def test_expected_outputs_are_valid_json(self, expected_outputs):
        """Test that expected output files are valid JSON."""
        for output_type, path in expected_outputs.items():
            with open(path) as f:
                data = json.load(f)
                assert data is not None, f"Failed to load {output_type} expected output"
    
    def test_expected_outputs_have_required_fields(self, expected_outputs):
        """Test that expected outputs have all required fields."""
        required_fields = [
            "resume_id", "job_category", "sections", "skills",
            "normalized_skills", "metadata"
        ]
        for output_type, path in expected_outputs.items():
            with open(path) as f:
                data = json.load(f)
                for field in required_fields:
                    assert field in data, f"Missing field '{field}' in {output_type}"
    
    def test_expected_outputs_sections_structure(self, expected_outputs):
        """Test that sections have correct structure."""
        section_fields = ["skills", "experience", "education", "projects", "raw_text"]
        for output_type, path in expected_outputs.items():
            with open(path) as f:
                data = json.load(f)
                sections = data["sections"]
                for field in section_fields:
                    assert field in sections, f"Missing section '{field}' in {output_type}"
    
    def test_expected_outputs_skills_structure(self, expected_outputs):
        """Test that skills have correct structure."""
        for output_type, path in expected_outputs.items():
            with open(path) as f:
                data = json.load(f)
                skills = data["skills"]
                assert "explicit_skills" in skills
                assert "implicit_skills" in skills
                assert isinstance(skills["explicit_skills"], list)
                assert isinstance(skills["implicit_skills"], list)


class TestJobRequirements:
    """Test job requirement JSON files."""
    
    def test_job_requirements_are_valid_json(self, job_requirements):
        """Test that job requirement files are valid JSON."""
        for job_type, path in job_requirements.items():
            with open(path) as f:
                data = json.load(f)
                assert data is not None, f"Failed to load {job_type} job requirements"
    
    def test_job_requirements_have_required_fields(self, job_requirements):
        """Test that job requirements have all required fields."""
        required_fields = [
            "job_title", "job_category", "required_skills",
            "preferred_skills", "experience_years", "education"
        ]
        for job_type, path in job_requirements.items():
            with open(path) as f:
                data = json.load(f)
                for field in required_fields:
                    assert field in data, f"Missing field '{field}' in {job_type}"
    
    def test_job_requirements_skills_are_lists(self, job_requirements):
        """Test that required and preferred skills are lists."""
        for job_type, path in job_requirements.items():
            with open(path) as f:
                data = json.load(f)
                assert isinstance(data["required_skills"], list)
                assert isinstance(data["preferred_skills"], list)
                assert len(data["required_skills"]) > 0, f"No required skills in {job_type}"
    
    def test_job_requirements_categories_are_valid(self, job_requirements):
        """Test that job categories are valid."""
        valid_categories = [
            "ACCOUNTANT", "INFORMATION-TECHNOLOGY", "HEALTHCARE"
        ]
        for job_type, path in job_requirements.items():
            with open(path) as f:
                data = json.load(f)
                category = data["job_category"]
                assert category in valid_categories, f"Invalid category in {job_type}: {category}"


class TestValidationMapping:
    """Test validation mapping file."""
    
    def test_validation_mapping_is_valid_json(self, validation_mapping):
        """Test that validation mapping is valid JSON."""
        with open(validation_mapping) as f:
            data = json.load(f)
            assert data is not None
    
    def test_validation_mapping_has_mappings(self, validation_mapping):
        """Test that validation mapping has mappings array."""
        with open(validation_mapping) as f:
            data = json.load(f)
            assert "mappings" in data
            assert isinstance(data["mappings"], list)
            assert len(data["mappings"]) > 0
    
    def test_validation_mapping_entries_have_required_fields(self, validation_mapping):
        """Test that each mapping entry has required fields."""
        required_fields = ["csv_id", "pdf_file", "job_category"]
        with open(validation_mapping) as f:
            data = json.load(f)
            for entry in data["mappings"]:
                for field in required_fields:
                    assert field in entry, f"Missing field '{field}' in mapping entry"
    
    def test_validation_mapping_has_criteria(self, validation_mapping):
        """Test that validation mapping has validation criteria."""
        with open(validation_mapping) as f:
            data = json.load(f)
            assert "validation_criteria" in data
            criteria = data["validation_criteria"]
            assert "skill_overlap_threshold" in criteria
            assert "category_match_required" in criteria
            assert "min_skills_extracted" in criteria


class TestFixtureHelpers:
    """Test fixture helper functions."""
    
    def test_load_job_requirements_helper(self, load_job_requirements):
        """Test that load_job_requirements helper works."""
        accountant_req = load_job_requirements("accountant")
        assert accountant_req is not None
        assert "required_skills" in accountant_req
    
    def test_load_expected_output_helper(self, load_expected_output):
        """Test that load_expected_output helper works."""
        accountant_output = load_expected_output("accountant")
        assert accountant_output is not None
        assert "resume_id" in accountant_output


class TestDataConsistency:
    """Test consistency between different fixture files."""
    
    def test_csv_ids_match_expected_outputs(self, sample_csv_path, expected_outputs):
        """Test that CSV IDs match expected output resume IDs."""
        df = pd.read_csv(sample_csv_path)
        csv_ids = set(df["ID"])
        
        for output_type, path in expected_outputs.items():
            with open(path) as f:
                data = json.load(f)
                resume_id = data["resume_id"]
                assert resume_id in csv_ids, f"Resume ID {resume_id} not found in CSV"
    
    def test_validation_mapping_references_valid_csv_ids(self, validation_mapping, sample_csv_path):
        """Test that validation mapping references valid CSV IDs."""
        df = pd.read_csv(sample_csv_path)
        csv_ids = set(df["ID"])
        
        with open(validation_mapping) as f:
            data = json.load(f)
            for entry in data["mappings"]:
                csv_id = entry["csv_id"]
                assert csv_id in csv_ids, f"Validation mapping references invalid CSV ID: {csv_id}"
    
    def test_validation_mapping_references_existing_pdf_files(self, validation_mapping, fixtures_dir):
        """Test that validation mapping references existing PDF files."""
        with open(validation_mapping) as f:
            data = json.load(f)
            for entry in data["mappings"]:
                pdf_file = Path(entry["pdf_file"])
                assert pdf_file.exists(), f"Validation mapping references non-existent PDF: {pdf_file}"
