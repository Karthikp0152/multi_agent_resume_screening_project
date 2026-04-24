"""
Unit tests for the FeatureGenerator component.

Tests cover vocabulary building, feature vector generation, feature matrix
creation, and support for both CSV and PDF data sources.
"""

import pytest
import numpy as np
from pathlib import Path

from src.feature_generator import FeatureGenerator
from src.models import (
    StructuredResume,
    ResumeSections,
    SkillSet,
    ResumeMetadata,
    ProcessorConfig
)
from src.resume_processor import ResumeProcessor


class TestFeatureGeneratorInitialization:
    """Test FeatureGenerator initialization."""
    
    def test_init_creates_empty_vocabulary(self):
        """Test that initialization creates empty vocabulary."""
        generator = FeatureGenerator()
        
        assert generator.vocabulary == []
        assert generator.vocabulary_index == {}
    
    def test_init_logging(self, caplog):
        """Test that initialization logs correctly."""
        import logging
        caplog.set_level(logging.INFO)
        
        generator = FeatureGenerator()
        
        assert "FeatureGenerator initialized" in caplog.text


class TestBuildVocabulary:
    """Test vocabulary building from resumes."""
    
    def test_build_vocabulary_from_single_resume(self):
        """Test building vocabulary from a single resume."""
        generator = FeatureGenerator()
        
        # Create sample resume
        resume = StructuredResume(
            resume_id="test_001",
            job_category="ENGINEER",
            sections=ResumeSections(
                skills="Python, Java",
                experience="",
                education="",
                projects="",
                raw_text=""
            ),
            skills=SkillSet(explicit_skills=["Python", "Java"], implicit_skills=[]),
            normalized_skills=["python", "java"],
            scores=None,
            metadata=ResumeMetadata(
                file_path="test.pdf",
                processed_date="2024-01-01",
                processing_time_ms=100
            )
        )
        
        vocabulary = generator.build_vocabulary([resume])
        
        assert len(vocabulary) == 2
        assert "python" in vocabulary
        assert "java" in vocabulary
        assert vocabulary == sorted(vocabulary)  # Should be sorted
    
    def test_build_vocabulary_from_multiple_resumes(self):
        """Test building vocabulary from multiple resumes."""
        generator = FeatureGenerator()
        
        # Create sample resumes
        resume1 = StructuredResume(
            resume_id="test_001",
            job_category="ENGINEER",
            sections=ResumeSections("", "", "", "", ""),
            skills=SkillSet([], []),
            normalized_skills=["python", "java", "sql"],
            scores=None,
            metadata=ResumeMetadata("test1.pdf", "2024-01-01", 100)
        )
        
        resume2 = StructuredResume(
            resume_id="test_002",
            job_category="ENGINEER",
            sections=ResumeSections("", "", "", "", ""),
            skills=SkillSet([], []),
            normalized_skills=["python", "javascript", "react"],
            scores=None,
            metadata=ResumeMetadata("test2.pdf", "2024-01-01", 100)
        )
        
        vocabulary = generator.build_vocabulary([resume1, resume2])
        
        # Should have unique skills from both resumes
        assert len(vocabulary) == 5
        assert set(vocabulary) == {"python", "java", "sql", "javascript", "react"}
        assert vocabulary == sorted(vocabulary)
    
    def test_build_vocabulary_removes_duplicates(self):
        """Test that vocabulary contains only unique skills."""
        generator = FeatureGenerator()
        
        resume1 = StructuredResume(
            resume_id="test_001",
            job_category="ENGINEER",
            sections=ResumeSections("", "", "", "", ""),
            skills=SkillSet([], []),
            normalized_skills=["python", "java", "python"],  # Duplicate
            scores=None,
            metadata=ResumeMetadata("test1.pdf", "2024-01-01", 100)
        )
        
        resume2 = StructuredResume(
            resume_id="test_002",
            job_category="ENGINEER",
            sections=ResumeSections("", "", "", "", ""),
            skills=SkillSet([], []),
            normalized_skills=["python", "java"],  # Same skills
            scores=None,
            metadata=ResumeMetadata("test2.pdf", "2024-01-01", 100)
        )
        
        vocabulary = generator.build_vocabulary([resume1, resume2])
        
        assert len(vocabulary) == 2
        assert set(vocabulary) == {"python", "java"}
    
    def test_build_vocabulary_creates_index(self):
        """Test that vocabulary index is created correctly."""
        generator = FeatureGenerator()
        
        resume = StructuredResume(
            resume_id="test_001",
            job_category="ENGINEER",
            sections=ResumeSections("", "", "", "", ""),
            skills=SkillSet([], []),
            normalized_skills=["python", "java", "sql"],
            scores=None,
            metadata=ResumeMetadata("test.pdf", "2024-01-01", 100)
        )
        
        vocabulary = generator.build_vocabulary([resume])
        
        # Check index mapping
        assert len(generator.vocabulary_index) == 3
        assert generator.vocabulary_index["java"] == 0  # Alphabetically first
        assert generator.vocabulary_index["python"] == 1
        assert generator.vocabulary_index["sql"] == 2
    
    def test_build_vocabulary_empty_list_raises_error(self):
        """Test that empty resume list raises ValueError."""
        generator = FeatureGenerator()
        
        with pytest.raises(ValueError, match="Cannot build vocabulary from empty resume list"):
            generator.build_vocabulary([])
    
    def test_build_vocabulary_no_skills_raises_error(self):
        """Test that resumes with no skills raise ValueError."""
        generator = FeatureGenerator()
        
        resume = StructuredResume(
            resume_id="test_001",
            job_category="ENGINEER",
            sections=ResumeSections("", "", "", "", ""),
            skills=SkillSet([], []),
            normalized_skills=[],  # No skills
            scores=None,
            metadata=ResumeMetadata("test.pdf", "2024-01-01", 100)
        )
        
        with pytest.raises(ValueError, match="No skills found in provided resumes"):
            generator.build_vocabulary([resume])


class TestGenerateFeatureVector:
    """Test feature vector generation."""
    
    def test_generate_feature_vector_all_present(self):
        """Test feature vector when all skills are present."""
        generator = FeatureGenerator()
        generator.vocabulary = ["java", "python", "sql"]
        generator.vocabulary_index = {"java": 0, "python": 1, "sql": 2}
        
        skills = ["python", "java", "sql"]
        vector = generator.generate_feature_vector(skills, generator.vocabulary)
        
        assert vector.shape == (3,)
        assert np.array_equal(vector, np.array([1, 1, 1]))
        assert vector.dtype == np.int8
    
    def test_generate_feature_vector_partial_match(self):
        """Test feature vector with partial skill match."""
        generator = FeatureGenerator()
        generator.vocabulary = ["java", "python", "sql"]
        generator.vocabulary_index = {"java": 0, "python": 1, "sql": 2}
        
        skills = ["python", "sql"]  # Missing java
        vector = generator.generate_feature_vector(skills, generator.vocabulary)
        
        assert vector.shape == (3,)
        assert np.array_equal(vector, np.array([0, 1, 1]))
    
    def test_generate_feature_vector_no_match(self):
        """Test feature vector when no skills match."""
        generator = FeatureGenerator()
        generator.vocabulary = ["java", "python", "sql"]
        generator.vocabulary_index = {"java": 0, "python": 1, "sql": 2}
        
        skills = ["javascript", "react"]  # None in vocabulary
        vector = generator.generate_feature_vector(skills, generator.vocabulary)
        
        assert vector.shape == (3,)
        assert np.array_equal(vector, np.array([0, 0, 0]))
    
    def test_generate_feature_vector_empty_skills(self):
        """Test feature vector with empty skills list."""
        generator = FeatureGenerator()
        generator.vocabulary = ["java", "python", "sql"]
        generator.vocabulary_index = {"java": 0, "python": 1, "sql": 2}
        
        skills = []
        vector = generator.generate_feature_vector(skills, generator.vocabulary)
        
        assert vector.shape == (3,)
        assert np.array_equal(vector, np.array([0, 0, 0]))
    
    def test_generate_feature_vector_with_extra_skills(self):
        """Test that extra skills not in vocabulary are ignored."""
        generator = FeatureGenerator()
        generator.vocabulary = ["java", "python"]
        generator.vocabulary_index = {"java": 0, "python": 1}
        
        skills = ["python", "javascript", "java", "react"]
        vector = generator.generate_feature_vector(skills, generator.vocabulary)
        
        assert vector.shape == (2,)
        assert np.array_equal(vector, np.array([1, 1]))
    
    def test_generate_feature_vector_without_building_vocabulary_raises_error(self):
        """Test that generating vector without vocabulary raises error."""
        generator = FeatureGenerator()
        
        with pytest.raises(ValueError, match="Vocabulary not built"):
            generator.generate_feature_vector(["python"], [])
    
    def test_generate_feature_vector_with_provided_vocabulary(self):
        """Test generating vector with externally provided vocabulary."""
        generator = FeatureGenerator()
        
        # Don't build vocabulary, provide it directly
        external_vocab = ["java", "python", "sql"]
        skills = ["python", "sql"]
        
        vector = generator.generate_feature_vector(skills, external_vocab)
        
        assert vector.shape == (3,)
        assert np.array_equal(vector, np.array([0, 1, 1]))


class TestGenerateFeatureMatrix:
    """Test feature matrix generation."""
    
    def test_generate_feature_matrix_single_resume(self):
        """Test generating feature matrix from single resume."""
        generator = FeatureGenerator()
        
        resume = StructuredResume(
            resume_id="test_001",
            job_category="ENGINEER",
            sections=ResumeSections("", "", "", "", ""),
            skills=SkillSet([], []),
            normalized_skills=["python", "java"],
            scores=None,
            metadata=ResumeMetadata("test.pdf", "2024-01-01", 100)
        )
        
        matrix, vocabulary = generator.generate_feature_matrix([resume])
        
        assert matrix.shape == (1, 2)  # 1 resume, 2 skills
        assert len(vocabulary) == 2
        assert set(vocabulary) == {"python", "java"}
    
    def test_generate_feature_matrix_multiple_resumes(self):
        """Test generating feature matrix from multiple resumes."""
        generator = FeatureGenerator()
        
        resume1 = StructuredResume(
            resume_id="test_001",
            job_category="ENGINEER",
            sections=ResumeSections("", "", "", "", ""),
            skills=SkillSet([], []),
            normalized_skills=["python", "java"],
            scores=None,
            metadata=ResumeMetadata("test1.pdf", "2024-01-01", 100)
        )
        
        resume2 = StructuredResume(
            resume_id="test_002",
            job_category="ENGINEER",
            sections=ResumeSections("", "", "", "", ""),
            skills=SkillSet([], []),
            normalized_skills=["python", "sql"],
            scores=None,
            metadata=ResumeMetadata("test2.pdf", "2024-01-01", 100)
        )
        
        resume3 = StructuredResume(
            resume_id="test_003",
            job_category="ENGINEER",
            sections=ResumeSections("", "", "", "", ""),
            skills=SkillSet([], []),
            normalized_skills=["javascript", "react"],
            scores=None,
            metadata=ResumeMetadata("test3.pdf", "2024-01-01", 100)
        )
        
        matrix, vocabulary = generator.generate_feature_matrix([resume1, resume2, resume3])
        
        assert matrix.shape == (3, 5)  # 3 resumes, 5 unique skills
        assert len(vocabulary) == 5
        assert set(vocabulary) == {"python", "java", "sql", "javascript", "react"}
    
    def test_generate_feature_matrix_consistent_dimensionality(self):
        """Test that all feature vectors have consistent dimensionality."""
        generator = FeatureGenerator()
        
        resume1 = StructuredResume(
            resume_id="test_001",
            job_category="ENGINEER",
            sections=ResumeSections("", "", "", "", ""),
            skills=SkillSet([], []),
            normalized_skills=["python"],
            scores=None,
            metadata=ResumeMetadata("test1.pdf", "2024-01-01", 100)
        )
        
        resume2 = StructuredResume(
            resume_id="test_002",
            job_category="ENGINEER",
            sections=ResumeSections("", "", "", "", ""),
            skills=SkillSet([], []),
            normalized_skills=["python", "java", "sql", "javascript"],
            scores=None,
            metadata=ResumeMetadata("test2.pdf", "2024-01-01", 100)
        )
        
        matrix, vocabulary = generator.generate_feature_matrix([resume1, resume2])
        
        # Both resumes should have same number of features
        assert matrix.shape[0] == 2
        assert matrix.shape[1] == 4  # Total unique skills
        
        # Check each row has correct dimensionality
        assert matrix[0].shape == (4,)
        assert matrix[1].shape == (4,)
    
    def test_generate_feature_matrix_binary_values(self):
        """Test that feature matrix contains only binary values."""
        generator = FeatureGenerator()
        
        resume1 = StructuredResume(
            resume_id="test_001",
            job_category="ENGINEER",
            sections=ResumeSections("", "", "", "", ""),
            skills=SkillSet([], []),
            normalized_skills=["python", "java"],
            scores=None,
            metadata=ResumeMetadata("test1.pdf", "2024-01-01", 100)
        )
        
        resume2 = StructuredResume(
            resume_id="test_002",
            job_category="ENGINEER",
            sections=ResumeSections("", "", "", "", ""),
            skills=SkillSet([], []),
            normalized_skills=["sql"],
            scores=None,
            metadata=ResumeMetadata("test2.pdf", "2024-01-01", 100)
        )
        
        matrix, vocabulary = generator.generate_feature_matrix([resume1, resume2])
        
        # All values should be 0 or 1
        assert np.all((matrix == 0) | (matrix == 1))
    
    def test_generate_feature_matrix_empty_list_raises_error(self):
        """Test that empty resume list raises ValueError."""
        generator = FeatureGenerator()
        
        with pytest.raises(ValueError, match="Cannot generate feature matrix from empty resume list"):
            generator.generate_feature_matrix([])
    
    def test_generate_feature_matrix_builds_vocabulary_if_needed(self):
        """Test that feature matrix generation builds vocabulary if not already built."""
        generator = FeatureGenerator()
        
        # Vocabulary not built yet
        assert generator.vocabulary == []
        
        resume = StructuredResume(
            resume_id="test_001",
            job_category="ENGINEER",
            sections=ResumeSections("", "", "", "", ""),
            skills=SkillSet([], []),
            normalized_skills=["python", "java"],
            scores=None,
            metadata=ResumeMetadata("test.pdf", "2024-01-01", 100)
        )
        
        matrix, vocabulary = generator.generate_feature_matrix([resume])
        
        # Vocabulary should now be built
        assert len(generator.vocabulary) == 2
        assert generator.vocabulary == vocabulary


class TestConsistentDimensionality:
    """Test that feature vectors maintain consistent dimensionality across data sources."""
    
    def test_consistent_dimensionality_across_resumes(self):
        """Test that all resumes get same dimensionality regardless of skill count."""
        generator = FeatureGenerator()
        
        # Resume with many skills
        resume1 = StructuredResume(
            resume_id="test_001",
            job_category="ENGINEER",
            sections=ResumeSections("", "", "", "", ""),
            skills=SkillSet([], []),
            normalized_skills=["python", "java", "sql", "javascript", "react"],
            scores=None,
            metadata=ResumeMetadata("test1.pdf", "2024-01-01", 100)
        )
        
        # Resume with few skills
        resume2 = StructuredResume(
            resume_id="test_002",
            job_category="ENGINEER",
            sections=ResumeSections("", "", "", "", ""),
            skills=SkillSet([], []),
            normalized_skills=["python"],
            scores=None,
            metadata=ResumeMetadata("test2.pdf", "2024-01-01", 100)
        )
        
        # Resume with no overlapping skills
        resume3 = StructuredResume(
            resume_id="test_003",
            job_category="ENGINEER",
            sections=ResumeSections("", "", "", "", ""),
            skills=SkillSet([], []),
            normalized_skills=["c++", "rust"],
            scores=None,
            metadata=ResumeMetadata("test3.pdf", "2024-01-01", 100)
        )
        
        matrix, vocabulary = generator.generate_feature_matrix([resume1, resume2, resume3])
        
        # All rows should have same number of columns
        assert matrix.shape[0] == 3
        assert matrix.shape[1] == 7  # Total unique skills
        
        # Verify each resume has correct features
        vocab_index = {skill: idx for idx, skill in enumerate(vocabulary)}
        
        # Resume 1 should have 5 skills set to 1
        assert np.sum(matrix[0]) == 5
        
        # Resume 2 should have 1 skill set to 1
        assert np.sum(matrix[1]) == 1
        
        # Resume 3 should have 2 skills set to 1
        assert np.sum(matrix[2]) == 2


class TestEdgeCases:
    """Test edge cases and error handling."""
    
    def test_handle_unseen_skills_in_feature_vector(self):
        """Test that unseen skills are ignored in feature vector generation."""
        generator = FeatureGenerator()
        generator.vocabulary = ["python", "java"]
        generator.vocabulary_index = {"python": 0, "java": 1}
        
        # Skills include items not in vocabulary
        skills = ["python", "unknown_skill", "java", "another_unknown"]
        vector = generator.generate_feature_vector(skills, generator.vocabulary)
        
        # Should only set features for known skills
        assert np.array_equal(vector, np.array([1, 1]))
    
    def test_vocabulary_sorted_alphabetically(self):
        """Test that vocabulary is always sorted alphabetically."""
        generator = FeatureGenerator()
        
        resume = StructuredResume(
            resume_id="test_001",
            job_category="ENGINEER",
            sections=ResumeSections("", "", "", "", ""),
            skills=SkillSet([], []),
            normalized_skills=["zebra", "apple", "mango", "banana"],
            scores=None,
            metadata=ResumeMetadata("test.pdf", "2024-01-01", 100)
        )
        
        vocabulary = generator.build_vocabulary([resume])
        
        assert vocabulary == ["apple", "banana", "mango", "zebra"]
    
    def test_large_vocabulary(self):
        """Test handling of large vocabulary."""
        generator = FeatureGenerator()
        
        # Create resume with many skills
        large_skill_list = [f"skill_{i}" for i in range(1000)]
        
        resume = StructuredResume(
            resume_id="test_001",
            job_category="ENGINEER",
            sections=ResumeSections("", "", "", "", ""),
            skills=SkillSet([], []),
            normalized_skills=large_skill_list,
            scores=None,
            metadata=ResumeMetadata("test.pdf", "2024-01-01", 100)
        )
        
        matrix, vocabulary = generator.generate_feature_matrix([resume])
        
        assert len(vocabulary) == 1000
        assert matrix.shape == (1, 1000)
        assert np.sum(matrix[0]) == 1000  # All skills present
