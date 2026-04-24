"""
Scoring Engine for the Smart Resume Screening System.

This module implements ATS (keyword-based) and semantic (embedding-based) scoring
to evaluate resume-job requirement matches.
"""

from typing import List
import logging
from src.models import Scores

logger = logging.getLogger(__name__)


# Custom exceptions
class EmbeddingError(Exception):
    """Raised when sentence embedding generation fails."""
    pass


class ScoringEngine:
    """Calculate ATS and semantic similarity scores for resume-job matching.
    
    This class provides dual scoring mechanisms:
    - ATS Score: Traditional keyword matching using set intersection (0-100)
    - Semantic Score: Embedding-based cosine similarity (0-1)
    
    Attributes:
        model: Sentence transformer model for generating embeddings
        embedding_model_name: Name of the sentence transformer model
    """
    
    def __init__(self, embedding_model: str = "all-MiniLM-L6-v2"):
        """Initialize ScoringEngine with sentence transformer model.
        
        Args:
            embedding_model: Name of the sentence-transformers model to use
                           (default: "all-MiniLM-L6-v2")
        
        Raises:
            EmbeddingError: If model fails to load
        """
        self.embedding_model_name = embedding_model
        self.model = None
        
        try:
            from sentence_transformers import SentenceTransformer
            self.model = SentenceTransformer(embedding_model)
            logger.info(f"Loaded sentence transformer model: {embedding_model}")
        except Exception as e:
            logger.error(f"Failed to load embedding model: {e}")
            raise EmbeddingError(f"Failed to load embedding model '{embedding_model}': {e}")
    
    def calculate_ats_score(self, resume_skills: List[str], job_requirements: List[str]) -> float:
        """Calculate keyword match percentage using set intersection.
        
        ATS (Applicant Tracking System) score measures the percentage of job requirements
        that are exactly matched by resume skills (case-insensitive).
        
        Args:
            resume_skills: List of skills from the resume
            job_requirements: List of required skills for the job
        
        Returns:
            ATS score as a percentage (0-100). Returns 0.0 if job_requirements is empty.
        
        Example:
            >>> engine = ScoringEngine()
            >>> engine.calculate_ats_score(["Python", "Java"], ["python", "java", "c++"])
            66.67  # 2 out of 3 requirements matched
        """
        # Handle empty skill sets
        if not resume_skills or not job_requirements:
            logger.warning("Empty skill set provided for ATS score calculation")
            return 0.0
        
        # Convert to lowercase sets for case-insensitive matching
        resume_set = set(skill.lower() for skill in resume_skills)
        job_set = set(req.lower() for req in job_requirements)
        
        # Calculate intersection
        matches = len(resume_set.intersection(job_set))
        total_required = len(job_set)
        
        # Calculate percentage
        ats_score = (matches / total_required * 100) if total_required > 0 else 0.0
        
        logger.debug(f"ATS Score: {ats_score:.2f}% ({matches}/{total_required} matches)")
        return ats_score
    
    def calculate_semantic_score(self, resume_skills: List[str], job_requirements: List[str]) -> float:
        """Calculate cosine similarity using sentence embeddings.
        
        Semantic score measures conceptual similarity between resume skills and job
        requirements using transformer-based embeddings, capturing related skills
        beyond exact keyword matches.
        
        Args:
            resume_skills: List of skills from the resume
            job_requirements: List of required skills for the job
        
        Returns:
            Semantic similarity score (0-1). Returns 0.0 if either list is empty.
        
        Raises:
            EmbeddingError: If embedding generation fails
        
        Example:
            >>> engine = ScoringEngine()
            >>> engine.calculate_semantic_score(["Python", "ML"], ["Machine Learning", "AI"])
            0.85  # High similarity despite different keywords
        """
        # Handle empty skill sets
        if not resume_skills or not job_requirements:
            logger.warning("Empty skill set provided for semantic score calculation")
            return 0.0
        
        try:
            from sklearn.metrics.pairwise import cosine_similarity
            
            # Convert skill lists to comma-separated strings
            resume_text = ", ".join(resume_skills)
            job_text = ", ".join(job_requirements)
            
            # Generate embeddings
            resume_embedding = self.model.encode([resume_text])
            job_embedding = self.model.encode([job_text])
            
            # Calculate cosine similarity
            similarity = cosine_similarity(resume_embedding, job_embedding)[0][0]
            semantic_score = float(similarity)
            
            logger.debug(f"Semantic Score: {semantic_score:.4f}")
            return semantic_score
            
        except Exception as e:
            logger.error(f"Embedding generation failed: {e}")
            raise EmbeddingError(f"Failed to calculate semantic score: {e}")
    
    def calculate_both_scores(self, resume_skills: List[str], job_requirements: List[str]) -> Scores:
        """Calculate both ATS and semantic scores.
        
        This method computes both scoring metrics and handles embedding failures
        gracefully by falling back to ATS-only scoring.
        
        Args:
            resume_skills: List of skills from the resume
            job_requirements: List of required skills for the job
        
        Returns:
            Scores dataclass containing both ats_score and semantic_score.
            If embedding fails, semantic_score will be 0.0.
        
        Example:
            >>> engine = ScoringEngine()
            >>> scores = engine.calculate_both_scores(["Python", "Java"], ["python", "ML"])
            >>> print(f"ATS: {scores.ats_score}, Semantic: {scores.semantic_score}")
            ATS: 50.0, Semantic: 0.72
        """
        # Calculate ATS score (always works)
        ats_score = self.calculate_ats_score(resume_skills, job_requirements)
        
        # Try to calculate semantic score with fallback
        try:
            semantic_score = self.calculate_semantic_score(resume_skills, job_requirements)
        except EmbeddingError as e:
            logger.warning(f"Falling back to ATS-only scoring due to embedding error: {e}")
            semantic_score = 0.0
        
        return Scores(ats_score=ats_score, semantic_score=semantic_score)
