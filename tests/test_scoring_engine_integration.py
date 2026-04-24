"""
Integration tests for ScoringEngine with real sentence-transformers model.

These tests require the sentence-transformers library and will download
the model on first run. They verify the actual behavior with real embeddings.
"""

import pytest
from src.scoring_engine import ScoringEngine, EmbeddingError
from src.models import Scores


@pytest.mark.integration
class TestScoringEngineIntegration:
    """Integration tests with real sentence-transformers model."""
    
    @pytest.fixture(scope="class")
    def engine(self):
        """Create a real ScoringEngine instance (may download model)."""
        try:
            return ScoringEngine()
        except Exception as e:
            pytest.skip(f"Could not load sentence-transformers model: {e}")
    
    def test_real_ats_score_calculation(self, engine):
        """Test ATS score with real data."""
        resume_skills = ["Python", "Machine Learning", "TensorFlow", "Docker"]
        job_requirements = ["python", "machine learning", "kubernetes"]
        
        score = engine.calculate_ats_score(resume_skills, job_requirements)
        
        # Should match 2 out of 3 requirements (python, machine learning)
        assert score == pytest.approx(66.67, rel=0.01)
    
    def test_real_semantic_score_calculation(self, engine):
        """Test semantic score with real embeddings."""
        resume_skills = ["Python", "Machine Learning", "Deep Learning"]
        job_requirements = ["ML", "AI", "Neural Networks"]
        
        score = engine.calculate_semantic_score(resume_skills, job_requirements)
        
        # Should have high semantic similarity despite different keywords
        assert 0.0 <= score <= 1.0
        assert score > 0.5  # Expect reasonably high similarity
    
    def test_real_both_scores(self, engine):
        """Test both scores with real data."""
        resume_skills = ["JavaScript", "React", "Node.js", "MongoDB"]
        job_requirements = ["javascript", "react", "postgresql"]
        
        scores = engine.calculate_both_scores(resume_skills, job_requirements)
        
        assert isinstance(scores, Scores)
        assert scores.ats_score == pytest.approx(66.67, rel=0.01)  # 2/3 match
        assert 0.0 <= scores.semantic_score <= 1.0
    
    def test_real_semantic_similarity_related_skills(self, engine):
        """Test that semantically related skills have higher similarity."""
        # Very similar skills
        similar_resume = ["Python", "Machine Learning"]
        similar_job = ["Python", "ML"]
        
        # Unrelated skills
        different_resume = ["Python", "Machine Learning"]
        different_job = ["Cooking", "Gardening"]
        
        similar_score = engine.calculate_semantic_score(similar_resume, similar_job)
        different_score = engine.calculate_semantic_score(different_resume, different_job)
        
        # Similar skills should have higher semantic score
        assert similar_score > different_score
    
    def test_real_empty_skills_handling(self, engine):
        """Test that empty skills are handled correctly with real model."""
        scores = engine.calculate_both_scores([], ["Python", "Java"])
        
        assert scores.ats_score == 0.0
        assert scores.semantic_score == 0.0
    
    def test_real_perfect_match(self, engine):
        """Test perfect match scenario with real model."""
        skills = ["Python", "Java", "SQL"]
        requirements = ["python", "java", "sql"]
        
        scores = engine.calculate_both_scores(skills, requirements)
        
        assert scores.ats_score == 100.0
        assert scores.semantic_score > 0.9  # Should be very high
