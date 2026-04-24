"""
Skill Extractor component for the Smart Resume Screening System.

This module implements NLP-based skill extraction using spaCy for Named Entity Recognition
and noun phrase extraction. It extracts both explicit skills (from Skills section) and
implicit skills (from Experience and Projects sections).
"""

import logging
from typing import List
import spacy
from spacy.language import Language

from src.models import ResumeSections, SkillSet

# Configure logging
logger = logging.getLogger(__name__)


# Custom exceptions
class ModelLoadError(Exception):
    """Raised when spaCy model fails to load."""
    pass


class SkillExtractionError(Exception):
    """Raised when skill extraction process fails."""
    pass


class SkillExtractor:
    """Extract skills from resume sections using NLP.
    
    This class uses spaCy for Named Entity Recognition (NER) and noun phrase
    extraction to identify skills from resume text. It distinguishes between
    explicit skills (directly listed in Skills section) and implicit skills
    (inferred from Experience and Projects sections).
    
    Attributes:
        nlp: Loaded spaCy language model
        nlp_model: Name of the spaCy model being used
    """
    
    def __init__(self, nlp_model: str = "en_core_web_sm"):
        """Initialize SkillExtractor with spaCy model.
        
        Args:
            nlp_model: Name of the spaCy model to load (default: en_core_web_sm)
            
        Raises:
            ModelLoadError: If spaCy model fails to load
        """
        self.nlp_model = nlp_model
        try:
            logger.info(f"Loading spaCy model: {nlp_model}")
            self.nlp: Language = spacy.load(nlp_model)
            logger.info(f"Successfully loaded spaCy model: {nlp_model}")
        except OSError as e:
            error_msg = (
                f"Failed to load spaCy model '{nlp_model}'. "
                f"Please install it using: python -m spacy download {nlp_model}"
            )
            logger.error(error_msg)
            raise ModelLoadError(error_msg) from e
        except Exception as e:
            error_msg = f"Unexpected error loading spaCy model '{nlp_model}': {str(e)}"
            logger.error(error_msg)
            raise ModelLoadError(error_msg) from e
    
    def extract_explicit_skills(self, skills_section: str) -> List[str]:
        """Extract skills from the Skills section using NER and noun phrases.
        
        This method processes the Skills section to identify skill entities using:
        1. Named Entity Recognition (NER) to identify skill-related entities
        2. Noun phrase extraction to capture multi-word skills
        3. Token-based extraction for single-word skills
        
        Args:
            skills_section: Text content from the Skills section
            
        Returns:
            List of extracted skill strings
            
        Raises:
            SkillExtractionError: If extraction process fails
        """
        if not skills_section or not skills_section.strip():
            logger.debug("Empty skills section provided, returning empty list")
            return []
        
        try:
            logger.debug(f"Extracting explicit skills from text: {skills_section[:100]}...")
            doc = self.nlp(skills_section)
            skills = []
            
            # Extract noun phrases (captures multi-word skills like "Machine Learning")
            for chunk in doc.noun_chunks:
                skill = chunk.text.strip()
                if skill and len(skill) > 1:  # Filter out single characters
                    skills.append(skill)
                    logger.debug(f"Extracted noun phrase skill: {skill}")
            
            # Extract named entities (captures technology names, tools, etc.)
            for ent in doc.ents:
                # Focus on entities that could be skills (ORG, PRODUCT, etc.)
                if ent.label_ in ["ORG", "PRODUCT", "GPE", "NORP"]:
                    skill = ent.text.strip()
                    if skill and skill not in skills:
                        skills.append(skill)
                        logger.debug(f"Extracted entity skill: {skill} ({ent.label_})")
            
            # Extract individual tokens that look like skills (nouns, proper nouns)
            for token in doc:
                if token.pos_ in ["NOUN", "PROPN"] and not token.is_stop:
                    skill = token.text.strip()
                    if skill and len(skill) > 1 and skill not in skills:
                        skills.append(skill)
                        logger.debug(f"Extracted token skill: {skill}")
            
            logger.info(f"Extracted {len(skills)} explicit skills")
            return skills
            
        except Exception as e:
            error_msg = f"Failed to extract explicit skills: {str(e)}"
            logger.error(error_msg)
            raise SkillExtractionError(error_msg) from e
    
    def extract_implicit_skills(self, experience: str, projects: str) -> List[str]:
        """Infer skills from Experience and Projects sections using NER.
        
        This method analyzes work experience and project descriptions to identify
        implicit skills that may not be explicitly listed in the Skills section.
        It uses NER to identify technology mentions, tools, and methodologies.
        
        Args:
            experience: Text content from the Experience section
            projects: Text content from the Projects section
            
        Returns:
            List of inferred skill strings
            
        Raises:
            SkillExtractionError: If extraction process fails
        """
        # Combine experience and projects text
        combined_text = f"{experience}\n{projects}".strip()
        
        if not combined_text:
            logger.debug("Empty experience and projects sections, returning empty list")
            return []
        
        try:
            logger.debug(f"Extracting implicit skills from combined text: {combined_text[:100]}...")
            doc = self.nlp(combined_text)
            skills = []
            
            # Extract named entities that represent technologies, tools, methodologies
            for ent in doc.ents:
                # Focus on entities likely to be skills in work context
                if ent.label_ in ["ORG", "PRODUCT", "GPE", "NORP"]:
                    skill = ent.text.strip()
                    if skill and skill not in skills:
                        skills.append(skill)
                        logger.debug(f"Extracted implicit entity skill: {skill} ({ent.label_})")
            
            # Extract noun phrases that could represent skills or technologies
            for chunk in doc.noun_chunks:
                skill = chunk.text.strip()
                # Filter for skill-like phrases (avoid generic phrases)
                if skill and len(skill) > 2 and skill not in skills:
                    # Check if the phrase contains technical-sounding words
                    if any(token.pos_ in ["NOUN", "PROPN"] for token in chunk):
                        skills.append(skill)
                        logger.debug(f"Extracted implicit noun phrase skill: {skill}")
            
            logger.info(f"Extracted {len(skills)} implicit skills")
            return skills
            
        except Exception as e:
            error_msg = f"Failed to extract implicit skills: {str(e)}"
            logger.error(error_msg)
            raise SkillExtractionError(error_msg) from e
    
    def extract_all_skills(self, sections: ResumeSections) -> SkillSet:
        """Extract both explicit and implicit skills from resume sections.
        
        This is the main entry point for skill extraction. It processes all
        relevant resume sections and returns a SkillSet with separated
        explicit and implicit skills.
        
        Args:
            sections: ResumeSections dataclass containing all resume sections
            
        Returns:
            SkillSet dataclass with explicit_skills and implicit_skills lists
            
        Raises:
            SkillExtractionError: If extraction process fails
        """
        try:
            logger.info("Starting skill extraction from resume sections")
            
            # Extract explicit skills from Skills section
            explicit_skills = self.extract_explicit_skills(sections.skills)
            
            # Extract implicit skills from Experience and Projects sections
            implicit_skills = self.extract_implicit_skills(
                sections.experience,
                sections.projects
            )
            
            # Create and return SkillSet
            skill_set = SkillSet(
                explicit_skills=explicit_skills,
                implicit_skills=implicit_skills
            )
            
            logger.info(
                f"Skill extraction complete: {len(explicit_skills)} explicit, "
                f"{len(implicit_skills)} implicit, {len(skill_set.all_skills())} total"
            )
            
            return skill_set
            
        except SkillExtractionError:
            # Re-raise SkillExtractionError as-is
            raise
        except Exception as e:
            error_msg = f"Failed to extract all skills: {str(e)}"
            logger.error(error_msg)
            raise SkillExtractionError(error_msg) from e
