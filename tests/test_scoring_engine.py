"""
Unit tests for the ScoringEngine class.

Tests cover ATS scoring, semantic scoring, error handling, and edge cases.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import numpy as np
from src.scoring_engine import ScoringEngine, EmbeddingError
from src.models import Scores


class TestScoringEngineInitialization:
    """Tests for ScoringEngine initialization."""
    
    def test_init_with_default_model(self):
        """Test initialization with default embedding model."""
        with patch('sentence_transformers.SentenceTransformer') as mock_st:
            engine = ScoringEngine()
            mock_st.assert_called_once_with("all-MiniLM-L6-v2")
            assert engine.embedding_model_name == "all-MiniLM-L6-v2"
    
    def test_init_with_custom_model(self):
        """Test initialization with custom embedding model."""
        with patch('sentence_transformers.SentenceTransformer') as mock_st:
            engine = ScoringEngine(embedding_model="custom-model")
            mock_st.assert_called_once_with("custom-model")
            assert engine.embedding_model_name == "custom-model"
    
    def test_init_model_load_failure(self):
        """Test initialization fails gracefully when model cannot be loaded."""
        with patch('sentence_transformers.SentenceTransformer', side_effect=Exception("Model not found")):
            with pytest.raises(EmbeddingError) as exc_info:
                ScoringEngine()
            assert "Failed to load embedding model" in str(exc_info.value)


class TestATSScoreCalculation:
    """Tests for ATS score calculation."""
    
    @pytest.fixture
    def engine(self):
        """Create a ScoringEngine instance with mocked model."""
        with patch('sentence_transformers.SentenceTransformer'):
            return ScoringEngine()
    
    def test_perfect_match(self, engine):
        """Test ATS score with a full keyword match."""
        resume_skills = ["Python", "Java", "SQL"]
        job_requirements = ["python", "java", "sql"]
        score = engine.calculate_ats_score(resume_skills, job_requirements)
        assert score == 100.0
    
    def test_partial_match(self, engine):
        """Test ATS score with partial keyword match."""
        resume_skills = ["Python", "Java"]
        job_requirements = ["python", "java", "c++"]
        score = engine.calculate_ats_score(resume_skills, job_requirements)
        assert score == pytest.approx(66.67, rel=0.01)
    
    def test_no_match(self, engine):
        """Test ATS score with no keyword matches."""
        resume_skills = ["Python", "Java"]
        job_requirements = ["Ruby", "Go"]
        score = engine.calculate_ats_score(resume_skills, job_requirements)
        assert score == 0.0
    
    def test_case_insensitive_matching(self, engine):
        """Test that ATS scoring is case-insensitive."""
        resume_skills = ["PYTHON", "JaVa", "sql"]
        job_requirements = ["python", "JAVA", "SQL"]
        score = engine.calculate_ats_score(resume_skills, job_requirements)
        assert score == 100.0
    
    def test_empty_resume_skills(self, engine):
        """Test ATS score returns 0.0 when resume skills are empty."""
        resume_skills = []
        job_requirements = ["Python", "Java"]
        score = engine.calculate_ats_score(resume_skills, job_requirements)
        assert score == 0.0
    
    def test_empty_job_requirements(self, engine):
        """Test ATS score returns 0.0 when job requirements are empty."""
        resume_skills = ["Python", "Java"]
        job_requirements = []
        score = engine.calculate_ats_score(resume_skills, job_requirements)
        assert score == 0.0
    
    def test_both_empty(self, engine):
        """Test ATS score returns 0.0 when both lists are empty."""
        score = engine.calculate_ats_score([], [])
        assert score == 0.0
    
    def test_extra_resume_skills(self, engine):
        """Test ATS score when resume has more skills than required."""
        resume_skills = ["Python", "Java", "C++", "Ruby", "Go"]
        job_requirements = ["python", "java"]
        score = engine.calculate_ats_score(resume_skills, job_requirements)
        assert score == 100.0
    
    def test_duplicate_skills(self, engine):
        """Test ATS score handles duplicate skills correctly."""
        resume_skills = ["Python", "Python", "Java"]
        job_requirements = ["python", "java", "java"]
        score = engine.calculate_ats_score(resume_skills, job_requirements)
        assert score == 100.0


class TestSemanticScoreCalculation:
    """Tests for semantic score calculation."""
    
    @pytest.fixture
    def engine(self):
        """Create a ScoringEngine instance with mocked model."""
        with patch('sentence_transformers.SentenceTransformer') as mock_st:
            mock_model = Mock()
            mock_st.return_value = mock_model
            engine = ScoringEngine()
            engine.model = mock_model
            return engine
    
    def test_semantic_score_calculation(self, engine):
        """Test semantic score calculation with mocked embeddings."""
        # Mock embeddings
        resume_embedding = np.array([[0.5, 0.5, 0.5]])
        job_embedding = np.array([[0.6, 0.6, 0.6]])
        
        engine.model.encode = Mock(side_effect=[resume_embedding, job_embedding])
        
        with patch('sklearn.metrics.pairwise.cosine_similarity') as mock_cosine:
            mock_cosine.return_value = np.array([[0.85]])
            
            resume_skills = ["Python", "Machine Learning"]
            job_requirements = ["ML", "AI"]
            score = engine.calculate_semantic_score(resume_skills, job_requirements)
            
            assert score == 0.85
            assert engine.model.encode.call_count == 2
    
    def test_semantic_score_empty_resume_skills(self, engine):
        """Test semantic score returns 0.0 when resume skills are empty."""
        score = engine.calculate_semantic_score([], ["Python", "Java"])
        assert score == 0.0
    
    def test_semantic_score_empty_job_requirements(self, engine):
        """Test semantic score returns 0.0 when job requirements are empty."""
        score = engine.calculate_semantic_score(["Python", "Java"], [])
        assert score == 0.0
    
    def test_semantic_score_both_empty(self, engine):
        """Test semantic score returns 0.0 when both lists are empty."""
        score = engine.calculate_semantic_score([], [])
        assert score == 0.0
    
    def test_semantic_score_embedding_failure(self, engine):
        """Test semantic score raises EmbeddingError on embedding failure."""
        engine.model.encode = Mock(side_effect=Exception("Encoding failed"))
        
        with pytest.raises(EmbeddingError) as exc_info:
            engine.calculate_semantic_score(["Python"], ["Java"])
        assert "Failed to calculate semantic score" in str(exc_info.value)
    
    def test_semantic_score_text_formatting(self, engine):
        """Test that skills are properly formatted as comma-separated text."""
        resume_embedding = np.array([[0.5, 0.5]])
        job_embedding = np.array([[0.6, 0.6]])
        
        engine.model.encode = Mock(side_effect=[resume_embedding, job_embedding])
        
        with patch('sklearn.metrics.pairwise.cosine_similarity', return_value=np.array([[0.9]])):
            resume_skills = ["Python", "Java", "SQL"]
            job_requirements = ["ML", "AI"]
            engine.calculate_semantic_score(resume_skills, job_requirements)
            
            # Verify encode was called with comma-separated strings
            calls = engine.model.encode.call_args_list
            assert calls[0][0][0] == ["Python, Java, SQL"]
            assert calls[1][0][0] == ["ML, AI"]


class TestCalculateBothScores:
    """Tests for calculate_both_scores method."""
    
    @pytest.fixture
    def engine(self):
        """Create a ScoringEngine instance with mocked model."""
        with patch('sentence_transformers.SentenceTransformer') as mock_st:
            mock_model = Mock()
            mock_st.return_value = mock_model
            engine = ScoringEngine()
            engine.model = mock_model
            return engine
    
    def test_both_scores_success(self, engine):
        """Test successful calculation of both scores."""
        # Mock semantic score calculation
        resume_embedding = np.array([[0.5, 0.5]])
        job_embedding = np.array([[0.6, 0.6]])
        engine.model.encode = Mock(side_effect=[resume_embedding, job_embedding])
        
        with patch('sklearn.metrics.pairwise.cosine_similarity', return_value=np.array([[0.75]])):
            resume_skills = ["Python", "Java"]
            job_requirements = ["python", "java", "c++"]
            
            scores = engine.calculate_both_scores(resume_skills, job_requirements)
            
            assert isinstance(scores, Scores)
            assert scores.ats_score == pytest.approx(66.67, rel=0.01)
            assert scores.semantic_score == 0.75
    
    def test_both_scores_with_empty_skills(self, engine):
        """Test both scores return 0.0 when skills are empty."""
        scores = engine.calculate_both_scores([], ["Python"])
        assert scores.ats_score == 0.0
        assert scores.semantic_score == 0.0
    
    def test_both_scores_embedding_fallback(self, engine):
        """Test fallback to ATS-only when embedding fails."""
        # Make semantic score fail
        engine.model.encode = Mock(side_effect=Exception("Encoding failed"))
        
        resume_skills = ["Python", "Java"]
        job_requirements = ["python", "java"]
        
        scores = engine.calculate_both_scores(resume_skills, job_requirements)
        
        # ATS score should still work
        assert scores.ats_score == 100.0
        # Semantic score should fallback to 0.0
        assert scores.semantic_score == 0.0
    
    def test_both_scores_perfect_match(self, engine):
        """Test both scores with perfect keyword match."""
        resume_embedding = np.array([[1.0, 0.0]])
        job_embedding = np.array([[1.0, 0.0]])
        engine.model.encode = Mock(side_effect=[resume_embedding, job_embedding])
        
        with patch('sklearn.metrics.pairwise.cosine_similarity', return_value=np.array([[1.0]])):
            resume_skills = ["Python", "Java", "SQL"]
            job_requirements = ["python", "java", "sql"]
            
            scores = engine.calculate_both_scores(resume_skills, job_requirements)
            
            assert scores.ats_score == 100.0
            assert scores.semantic_score == 1.0


class TestEdgeCases:
    """Tests for edge cases and boundary conditions."""
    
    @pytest.fixture
    def engine(self):
        """Create a ScoringEngine instance with mocked model."""
        with patch('sentence_transformers.SentenceTransformer') as mock_st:
            mock_model = Mock()
            mock_st.return_value = mock_model
            engine = ScoringEngine()
            engine.model = mock_model
            return engine
    
    def test_single_skill_match(self, engine):
        """Test scoring with single skill in both lists."""
        score = engine.calculate_ats_score(["Python"], ["python"])
        assert score == 100.0
    
    def test_single_skill_no_match(self, engine):
        """Test scoring with single skill that doesn't match."""
        score = engine.calculate_ats_score(["Python"], ["Java"])
        assert score == 0.0
    
    def test_whitespace_in_skills(self, engine):
        """Test that skills with whitespace are handled correctly."""
        resume_skills = ["Machine Learning", "Data Science"]
        job_requirements = ["machine learning", "data science"]
        score = engine.calculate_ats_score(resume_skills, job_requirements)
        assert score == 100.0
    
    def test_special_characters_in_skills(self, engine):
        """Test skills with special characters."""
        resume_skills = ["C++", "C#", ".NET"]
        job_requirements = ["c++", "c#", ".net"]
        score = engine.calculate_ats_score(resume_skills, job_requirements)
        assert score == 100.0
    
    def test_very_long_skill_lists(self, engine):
        """Test scoring with large skill lists."""
        resume_skills = [f"skill_{i}" for i in range(100)]
        job_requirements = [f"skill_{i}" for i in range(50)]
        score = engine.calculate_ats_score(resume_skills, job_requirements)
        assert score == 100.0
    
    def test_semantic_score_boundary_values(self, engine):
        """Test semantic score returns values in valid range [0, 1]."""
        resume_embedding = np.array([[0.5, 0.5]])
        job_embedding = np.array([[0.6, 0.6]])
        engine.model.encode = Mock(side_effect=[resume_embedding, job_embedding])
        
        with patch('sklearn.metrics.pairwise.cosine_similarity', return_value=np.array([[0.5]])):
            score = engine.calculate_semantic_score(["Python"], ["Java"])
            assert 0.0 <= score <= 1.0
