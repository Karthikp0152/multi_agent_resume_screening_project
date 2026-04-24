"""
Data models for the Smart Resume Screening System.

This module defines all dataclasses used throughout the resume processing pipeline,
including resume sections, skill sets, scores, metadata, and configuration models.
"""

from dataclasses import dataclass, asdict
from typing import List, Optional, Dict, Any
from datetime import datetime
import json


@dataclass
class ResumeSections:
    """Represents the parsed sections of a resume.
    
    Attributes:
        skills: Text content from the Skills section
        experience: Text content from the Experience section
        education: Text content from the Education section
        projects: Text content from the Projects section
        raw_text: Complete unprocessed resume text
    """
    skills: str
    experience: str
    education: str
    projects: str
    raw_text: str


@dataclass
class SkillSet:
    """Represents extracted skills from a resume.
    
    Attributes:
        explicit_skills: Skills directly listed in the Skills section
        implicit_skills: Skills inferred from Experience or Projects sections
    """
    explicit_skills: List[str]
    implicit_skills: List[str]
    
    def all_skills(self) -> List[str]:
        """Combine explicit and implicit skills into a single list.
        
        Returns:
            Combined list of all skills
        """
        return self.explicit_skills + self.implicit_skills


@dataclass
class Scores:
    """Represents scoring metrics for a resume.
    
    Attributes:
        ats_score: Keyword match score (0-100)
        semantic_score: Semantic similarity score (0-1)
    """
    ats_score: float
    semantic_score: float


@dataclass
class ResumeMetadata:
    """Metadata about resume processing.
    
    Attributes:
        file_path: Path to the original resume file
        processed_date: ISO format timestamp of when resume was processed
        processing_time_ms: Time taken to process the resume in milliseconds
    """
    file_path: str
    processed_date: str
    processing_time_ms: int


@dataclass
class StructuredResume:
    """Complete structured representation of a processed resume.
    
    Attributes:
        resume_id: Unique identifier for the resume
        job_category: Job category classification
        sections: Parsed resume sections
        skills: Extracted skill set
        normalized_skills: List of normalized skill names
        scores: Optional scoring metrics
        metadata: Processing metadata
    """
    resume_id: str
    job_category: str
    sections: ResumeSections
    skills: SkillSet
    normalized_skills: List[str]
    scores: Optional[Scores]
    metadata: ResumeMetadata
    
    def to_json(self) -> dict:
        """Convert StructuredResume to JSON-serializable dictionary.
        
        Returns:
            Dictionary representation suitable for JSON serialization
        """
        return {
            "resume_id": self.resume_id,
            "job_category": self.job_category,
            "sections": asdict(self.sections),
            "skills": asdict(self.skills),
            "normalized_skills": self.normalized_skills,
            "scores": asdict(self.scores) if self.scores else None,
            "metadata": asdict(self.metadata)
        }
    
    @classmethod
    def from_json(cls, data: dict) -> 'StructuredResume':
        """Create StructuredResume from JSON dictionary.
        
        Args:
            data: Dictionary containing resume data
            
        Returns:
            StructuredResume instance
        """
        return cls(
            resume_id=data["resume_id"],
            job_category=data["job_category"],
            sections=ResumeSections(**data["sections"]),
            skills=SkillSet(**data["skills"]),
            normalized_skills=data["normalized_skills"],
            scores=Scores(**data["scores"]) if data.get("scores") else None,
            metadata=ResumeMetadata(**data["metadata"])
        )


@dataclass
class ProcessorConfig:
    """Configuration for the resume processor.
    
    Attributes:
        pdf_extractor: PDF extraction library to use ("pdfplumber" or "pypdf")
        nlp_model: spaCy model name for NLP processing
        embedding_model: Sentence transformer model for semantic embeddings
        fuzzy_threshold: Minimum similarity score for fuzzy matching (0-100)
        alias_dict_path: Path to skill alias dictionary JSON file
    """
    pdf_extractor: str = "pdfplumber"
    nlp_model: str = "en_core_web_sm"
    embedding_model: str = "all-MiniLM-L6-v2"
    fuzzy_threshold: int = 85
    alias_dict_path: str = "config/skill_aliases.json"


@dataclass
class MLConfig:
    """Configuration for machine learning components.
    
    Attributes:
        n_clusters: Number of clusters for K-Means clustering
        min_support: Minimum support threshold for Apriori algorithm
        min_confidence: Minimum confidence threshold for association rules
        test_size: Proportion of dataset for testing (0-1)
        random_state: Random seed for reproducibility
    """
    n_clusters: int = 10
    min_support: float = 0.1
    min_confidence: float = 0.5
    test_size: float = 0.2
    random_state: int = 42


@dataclass
class AssociationRule:
    """Represents an association rule between skill sets.
    
    Attributes:
        antecedents: Set of skills in the antecedent (if-part)
        consequents: Set of skills in the consequent (then-part)
        support: Proportion of transactions containing both antecedents and consequents
        confidence: Probability of consequents given antecedents
        lift: Ratio of observed support to expected support if independent
    """
    antecedents: frozenset
    consequents: frozenset
    support: float
    confidence: float
    lift: float


@dataclass
class ClassificationMetrics:
    """Metrics for classification model evaluation.
    
    Attributes:
        accuracy: Overall accuracy score (0-1)
        macro_f1: Macro-averaged F1 score (0-1)
        per_class_f1: Dictionary mapping class names to F1 scores
    """
    accuracy: float
    macro_f1: float
    per_class_f1: Dict[str, float]


@dataclass
class ClusteringMetrics:
    """Metrics for clustering evaluation.
    
    Attributes:
        silhouette_score: Silhouette coefficient (-1 to 1)
        n_clusters: Number of clusters
    """
    silhouette_score: float
    n_clusters: int


@dataclass
class ComparisonReport:
    """Comparison between baseline and proposed models.
    
    Attributes:
        baseline_metrics: Metrics for baseline model
        proposed_metrics: Metrics for proposed model
        accuracy_improvement: Difference in accuracy (proposed - baseline)
        f1_improvement: Difference in macro F1 (proposed - baseline)
    """
    baseline_metrics: 'ClassificationMetrics'
    proposed_metrics: 'ClassificationMetrics'
    accuracy_improvement: float
    f1_improvement: float


@dataclass
class FairnessReport:
    """Fairness analysis across job categories.
    
    Attributes:
        per_category_f1: Dictionary mapping categories to F1 scores
        mean_f1: Mean F1 score across all categories
        f1_variance: Variance in F1 scores across categories
        f1_std: Standard deviation of F1 scores
        flagged_categories: List of categories with significantly lower performance
        fairness_threshold: Threshold used for flagging (mean - std_dev)
    """
    per_category_f1: Dict[str, float]
    mean_f1: float
    f1_variance: float
    f1_std: float
    flagged_categories: List[str]
    fairness_threshold: float


@dataclass
class ExtractionValidationReport:
    """Validation of PDF extraction accuracy against CSV ground truth.
    
    Attributes:
        total_samples: Number of samples compared
        text_similarity_mean: Mean text similarity score
        text_similarity_std: Standard deviation of text similarity
        skill_overlap_mean: Mean skill overlap percentage
        skill_overlap_std: Standard deviation of skill overlap
        extraction_accuracy: Overall extraction accuracy metric
    """
    total_samples: int
    text_similarity_mean: float
    text_similarity_std: float
    skill_overlap_mean: float
    skill_overlap_std: float
    extraction_accuracy: float


@dataclass
class CrossSourceValidationReport:
    """Comparison of model performance on CSV vs PDF-derived features.
    
    Attributes:
        csv_accuracy: Model accuracy on CSV data
        pdf_accuracy: Model accuracy on PDF data
        accuracy_difference: Absolute difference between CSV and PDF accuracy
        csv_macro_f1: Macro F1 on CSV data
        pdf_macro_f1: Macro F1 on PDF data
        f1_difference: Absolute difference between CSV and PDF F1
        consistent_performance: Whether performance is consistent across sources
    """
    csv_accuracy: float
    pdf_accuracy: float
    accuracy_difference: float
    csv_macro_f1: float
    pdf_macro_f1: float
    f1_difference: float
    consistent_performance: bool
