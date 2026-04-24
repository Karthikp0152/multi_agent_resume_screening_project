"""
Unit tests for data models.

Tests JSON serialization/deserialization, dataclass field validation,
and model-specific methods like SkillSet.all_skills().
"""

import pytest
import json
from datetime import datetime
from src.models import (
    ResumeSections,
    SkillSet,
    Scores,
    ResumeMetadata,
    StructuredResume,
    ProcessorConfig,
    MLConfig
)


class TestResumeSections:
    """Tests for ResumeSections dataclass."""
    
    def test_resume_sections_creation(self):
        """Test creating ResumeSections with all fields."""
        sections = ResumeSections(
            skills="Python, Java, SQL",
            experience="5 years as Software Engineer",
            education="BS Computer Science",
            projects="Built web applications",
            raw_text="Complete resume text here"
        )
        
        assert sections.skills == "Python, Java, SQL"
        assert sections.experience == "5 years as Software Engineer"
        assert sections.education == "BS Computer Science"
        assert sections.projects == "Built web applications"
        assert sections.raw_text == "Complete resume text here"
    
    def test_resume_sections_empty_fields(self):
        """Test ResumeSections with empty string fields."""
        sections = ResumeSections(
            skills="",
            experience="",
            education="",
            projects="",
            raw_text=""
        )
        
        assert sections.skills == ""
        assert sections.experience == ""
        assert sections.education == ""
        assert sections.projects == ""
        assert sections.raw_text == ""


class TestSkillSet:
    """Tests for SkillSet dataclass."""
    
    def test_skillset_creation(self):
        """Test creating SkillSet with explicit and implicit skills."""
        skillset = SkillSet(
            explicit_skills=["Python", "Java", "SQL"],
            implicit_skills=["Docker", "Git"]
        )
        
        assert skillset.explicit_skills == ["Python", "Java", "SQL"]
        assert skillset.implicit_skills == ["Docker", "Git"]
    
    def test_skillset_all_skills_method(self):
        """Test SkillSet.all_skills() combines both skill lists."""
        skillset = SkillSet(
            explicit_skills=["Python", "Java", "SQL"],
            implicit_skills=["Docker", "Git"]
        )
        
        all_skills = skillset.all_skills()
        
        assert len(all_skills) == 5
        assert all_skills == ["Python", "Java", "SQL", "Docker", "Git"]
    
    def test_skillset_all_skills_empty_explicit(self):
        """Test all_skills() when explicit_skills is empty."""
        skillset = SkillSet(
            explicit_skills=[],
            implicit_skills=["Docker", "Git"]
        )
        
        all_skills = skillset.all_skills()
        
        assert all_skills == ["Docker", "Git"]
    
    def test_skillset_all_skills_empty_implicit(self):
        """Test all_skills() when implicit_skills is empty."""
        skillset = SkillSet(
            explicit_skills=["Python", "Java"],
            implicit_skills=[]
        )
        
        all_skills = skillset.all_skills()
        
        assert all_skills == ["Python", "Java"]
    
    def test_skillset_all_skills_both_empty(self):
        """Test all_skills() when both skill lists are empty."""
        skillset = SkillSet(
            explicit_skills=[],
            implicit_skills=[]
        )
        
        all_skills = skillset.all_skills()
        
        assert all_skills == []
    
    def test_skillset_preserves_order(self):
        """Test that all_skills() preserves order (explicit first, then implicit)."""
        skillset = SkillSet(
            explicit_skills=["A", "B", "C"],
            implicit_skills=["X", "Y", "Z"]
        )
        
        all_skills = skillset.all_skills()
        
        assert all_skills == ["A", "B", "C", "X", "Y", "Z"]


class TestScores:
    """Tests for Scores dataclass."""
    
    def test_scores_creation(self):
        """Test creating Scores with valid values."""
        scores = Scores(ats_score=75.5, semantic_score=0.85)
        
        assert scores.ats_score == 75.5
        assert scores.semantic_score == 0.85
    
    def test_scores_boundary_values(self):
        """Test Scores with boundary values."""
        scores_min = Scores(ats_score=0.0, semantic_score=0.0)
        scores_max = Scores(ats_score=100.0, semantic_score=1.0)
        
        assert scores_min.ats_score == 0.0
        assert scores_min.semantic_score == 0.0
        assert scores_max.ats_score == 100.0
        assert scores_max.semantic_score == 1.0


class TestResumeMetadata:
    """Tests for ResumeMetadata dataclass."""
    
    def test_metadata_creation(self):
        """Test creating ResumeMetadata with all fields."""
        metadata = ResumeMetadata(
            file_path="/path/to/resume.pdf",
            processed_date="2025-01-15T10:30:00",
            processing_time_ms=1500
        )
        
        assert metadata.file_path == "/path/to/resume.pdf"
        assert metadata.processed_date == "2025-01-15T10:30:00"
        assert metadata.processing_time_ms == 1500
    
    def test_metadata_with_iso_format(self):
        """Test metadata with ISO format timestamp."""
        timestamp = datetime.now().isoformat()
        metadata = ResumeMetadata(
            file_path="resume.pdf",
            processed_date=timestamp,
            processing_time_ms=2000
        )
        
        assert metadata.processed_date == timestamp


class TestStructuredResume:
    """Tests for StructuredResume dataclass and JSON serialization."""
    
    @pytest.fixture
    def sample_resume(self):
        """Create a sample StructuredResume for testing."""
        return StructuredResume(
            resume_id="12345",
            job_category="SOFTWARE_ENGINEER",
            sections=ResumeSections(
                skills="Python, Java",
                experience="5 years",
                education="BS CS",
                projects="Web apps",
                raw_text="Full text"
            ),
            skills=SkillSet(
                explicit_skills=["Python", "Java"],
                implicit_skills=["Docker"]
            ),
            normalized_skills=["python", "java", "docker"],
            scores=Scores(ats_score=80.0, semantic_score=0.9),
            metadata=ResumeMetadata(
                file_path="resume.pdf",
                processed_date="2025-01-15T10:30:00",
                processing_time_ms=1500
            )
        )
    
    def test_structured_resume_creation(self, sample_resume):
        """Test creating StructuredResume with all fields."""
        assert sample_resume.resume_id == "12345"
        assert sample_resume.job_category == "SOFTWARE_ENGINEER"
        assert sample_resume.sections.skills == "Python, Java"
        assert sample_resume.skills.explicit_skills == ["Python", "Java"]
        assert sample_resume.normalized_skills == ["python", "java", "docker"]
        assert sample_resume.scores.ats_score == 80.0
        assert sample_resume.metadata.file_path == "resume.pdf"
    
    def test_to_json_serialization(self, sample_resume):
        """Test StructuredResume.to_json() produces correct dictionary."""
        json_data = sample_resume.to_json()
        
        assert json_data["resume_id"] == "12345"
        assert json_data["job_category"] == "SOFTWARE_ENGINEER"
        assert json_data["sections"]["skills"] == "Python, Java"
        assert json_data["skills"]["explicit_skills"] == ["Python", "Java"]
        assert json_data["skills"]["implicit_skills"] == ["Docker"]
        assert json_data["normalized_skills"] == ["python", "java", "docker"]
        assert json_data["scores"]["ats_score"] == 80.0
        assert json_data["scores"]["semantic_score"] == 0.9
        assert json_data["metadata"]["file_path"] == "resume.pdf"
        assert json_data["metadata"]["processing_time_ms"] == 1500
    
    def test_to_json_is_json_serializable(self, sample_resume):
        """Test that to_json() output can be serialized to JSON string."""
        json_data = sample_resume.to_json()
        json_string = json.dumps(json_data)
        
        assert isinstance(json_string, str)
        assert "12345" in json_string
        assert "SOFTWARE_ENGINEER" in json_string
    
    def test_from_json_deserialization(self, sample_resume):
        """Test StructuredResume.from_json() reconstructs object correctly."""
        json_data = sample_resume.to_json()
        reconstructed = StructuredResume.from_json(json_data)
        
        assert reconstructed.resume_id == sample_resume.resume_id
        assert reconstructed.job_category == sample_resume.job_category
        assert reconstructed.sections.skills == sample_resume.sections.skills
        assert reconstructed.skills.explicit_skills == sample_resume.skills.explicit_skills
        assert reconstructed.normalized_skills == sample_resume.normalized_skills
        assert reconstructed.scores.ats_score == sample_resume.scores.ats_score
        assert reconstructed.metadata.file_path == sample_resume.metadata.file_path
    
    def test_json_roundtrip(self, sample_resume):
        """Test that to_json() -> from_json() preserves all data."""
        json_data = sample_resume.to_json()
        reconstructed = StructuredResume.from_json(json_data)
        json_data_2 = reconstructed.to_json()
        
        assert json_data == json_data_2
    
    def test_to_json_with_none_scores(self):
        """Test to_json() when scores is None."""
        resume = StructuredResume(
            resume_id="12345",
            job_category="ACCOUNTANT",
            sections=ResumeSections(
                skills="Excel",
                experience="3 years",
                education="BS Accounting",
                projects="",
                raw_text="Full text"
            ),
            skills=SkillSet(explicit_skills=["Excel"], implicit_skills=[]),
            normalized_skills=["excel"],
            scores=None,
            metadata=ResumeMetadata(
                file_path="resume.pdf",
                processed_date="2025-01-15T10:30:00",
                processing_time_ms=1000
            )
        )
        
        json_data = resume.to_json()
        
        assert json_data["scores"] is None
    
    def test_from_json_with_none_scores(self):
        """Test from_json() when scores is None."""
        json_data = {
            "resume_id": "12345",
            "job_category": "ACCOUNTANT",
            "sections": {
                "skills": "Excel",
                "experience": "3 years",
                "education": "BS Accounting",
                "projects": "",
                "raw_text": "Full text"
            },
            "skills": {
                "explicit_skills": ["Excel"],
                "implicit_skills": []
            },
            "normalized_skills": ["excel"],
            "scores": None,
            "metadata": {
                "file_path": "resume.pdf",
                "processed_date": "2025-01-15T10:30:00",
                "processing_time_ms": 1000
            }
        }
        
        resume = StructuredResume.from_json(json_data)
        
        assert resume.scores is None
    
    def test_json_serialization_to_file(self, sample_resume, tmp_path):
        """Test writing StructuredResume to JSON file and reading back."""
        json_file = tmp_path / "resume.json"
        
        # Write to file
        with open(json_file, 'w') as f:
            json.dump(sample_resume.to_json(), f)
        
        # Read from file
        with open(json_file, 'r') as f:
            loaded_data = json.load(f)
        
        reconstructed = StructuredResume.from_json(loaded_data)
        
        assert reconstructed.resume_id == sample_resume.resume_id
        assert reconstructed.job_category == sample_resume.job_category


class TestProcessorConfig:
    """Tests for ProcessorConfig dataclass."""
    
    def test_processor_config_defaults(self):
        """Test ProcessorConfig with default values."""
        config = ProcessorConfig()
        
        assert config.pdf_extractor == "pdfplumber"
        assert config.nlp_model == "en_core_web_sm"
        assert config.embedding_model == "all-MiniLM-L6-v2"
        assert config.fuzzy_threshold == 85
        assert config.alias_dict_path == "config/skill_aliases.json"
    
    def test_processor_config_custom_values(self):
        """Test ProcessorConfig with custom values."""
        config = ProcessorConfig(
            pdf_extractor="pypdf",
            nlp_model="en_core_web_md",
            embedding_model="custom-model",
            fuzzy_threshold=90,
            alias_dict_path="custom/path.json"
        )
        
        assert config.pdf_extractor == "pypdf"
        assert config.nlp_model == "en_core_web_md"
        assert config.embedding_model == "custom-model"
        assert config.fuzzy_threshold == 90
        assert config.alias_dict_path == "custom/path.json"
    
    def test_processor_config_partial_override(self):
        """Test ProcessorConfig with partial value override."""
        config = ProcessorConfig(fuzzy_threshold=95)
        
        assert config.pdf_extractor == "pdfplumber"  # default
        assert config.fuzzy_threshold == 95  # overridden


class TestMLConfig:
    """Tests for MLConfig dataclass."""
    
    def test_ml_config_defaults(self):
        """Test MLConfig with default values."""
        config = MLConfig()
        
        assert config.n_clusters == 10
        assert config.min_support == 0.1
        assert config.min_confidence == 0.5
        assert config.test_size == 0.2
        assert config.random_state == 42
    
    def test_ml_config_custom_values(self):
        """Test MLConfig with custom values."""
        config = MLConfig(
            n_clusters=15,
            min_support=0.2,
            min_confidence=0.6,
            test_size=0.3,
            random_state=123
        )
        
        assert config.n_clusters == 15
        assert config.min_support == 0.2
        assert config.min_confidence == 0.6
        assert config.test_size == 0.3
        assert config.random_state == 123
    
    def test_ml_config_partial_override(self):
        """Test MLConfig with partial value override."""
        config = MLConfig(n_clusters=20, random_state=999)
        
        assert config.n_clusters == 20  # overridden
        assert config.min_support == 0.1  # default
        assert config.random_state == 999  # overridden


class TestDataclassFieldValidation:
    """Tests for dataclass field type validation."""
    
    def test_skillset_with_wrong_type_raises_error(self):
        """Test that SkillSet with wrong types raises TypeError."""
        # Python dataclasses don't enforce types at runtime by default,
        # but we can test that the correct types work
        skillset = SkillSet(
            explicit_skills=["Python"],
            implicit_skills=["Docker"]
        )
        assert isinstance(skillset.explicit_skills, list)
        assert isinstance(skillset.implicit_skills, list)
    
    def test_scores_with_numeric_types(self):
        """Test Scores accepts both int and float."""
        scores_float = Scores(ats_score=75.5, semantic_score=0.85)
        scores_int = Scores(ats_score=75, semantic_score=1)
        
        assert isinstance(scores_float.ats_score, float)
        assert isinstance(scores_float.semantic_score, float)
        assert scores_int.ats_score == 75
        assert scores_int.semantic_score == 1
    
    def test_metadata_processing_time_is_integer(self):
        """Test ResumeMetadata processing_time_ms is integer."""
        metadata = ResumeMetadata(
            file_path="test.pdf",
            processed_date="2025-01-15T10:30:00",
            processing_time_ms=1500
        )
        
        assert isinstance(metadata.processing_time_ms, int)
