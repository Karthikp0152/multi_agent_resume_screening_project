"""
Skill Normalizer component for the Smart Resume Screening System.

This module provides the SkillNormalizer class that standardizes skill variations
to canonical forms using exact matching, fuzzy matching, and fallback logic.
"""

import json
from typing import Dict, List
from pathlib import Path
from rapidfuzz import process, fuzz


class SkillNormalizer:
    """Standardizes skill variations to canonical forms.
    
    The SkillNormalizer uses a three-step approach:
    1. Exact Match: Check if skill exists in alias dictionary
    2. Fuzzy Match: Use RapidFuzz to find closest canonical skill
    3. Fallback: Return original skill in lowercase if no match found
    
    Attributes:
        alias_dict: Dictionary mapping skill variations to canonical forms
        fuzzy_threshold: Minimum similarity score for fuzzy matching (0-100)
        canonical_skills: Set of unique canonical skill names for fuzzy matching
    """
    
    def __init__(self, alias_dict: Dict[str, str], fuzzy_threshold: int = 85):
        """Initialize with alias dictionary and fuzzy matching threshold.
        
        Args:
            alias_dict: Dictionary mapping skill variations to canonical forms
            fuzzy_threshold: Minimum similarity score for fuzzy matching (default: 85)
        """
        self.alias_dict = alias_dict
        self.fuzzy_threshold = fuzzy_threshold
        # Extract unique canonical skills for fuzzy matching
        self.canonical_skills = list(set(alias_dict.values()))
    
    def load_alias_dictionary(self, dict_path: str) -> Dict[str, str]:
        """Load skill alias mappings from JSON file.
        
        Args:
            dict_path: Path to JSON file containing skill aliases
            
        Returns:
            Dictionary mapping skill variations to canonical forms
            
        Raises:
            FileNotFoundError: If the dictionary file doesn't exist
            json.JSONDecodeError: If the file contains invalid JSON
        """
        path = Path(dict_path)
        if not path.exists():
            raise FileNotFoundError(f"Alias dictionary not found at: {dict_path}")
        
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Handle both direct dictionary and nested "aliases" key format
        if isinstance(data, dict) and "aliases" in data:
            return data["aliases"]
        return data
    
    def normalize_skill(self, skill: str) -> str:
        """Normalize a single skill to canonical form.
        
        Uses three-step normalization:
        1. Exact match in alias dictionary (case-insensitive)
        2. Fuzzy match against canonical skills using RapidFuzz
        3. Fallback to lowercase original skill
        
        Args:
            skill: Skill name to normalize
            
        Returns:
            Normalized canonical skill name
        """
        if not skill or not skill.strip():
            return ""
        
        # Clean the input skill
        skill_clean = skill.strip()
        skill_lower = skill_clean.lower()
        
        # Step 1: Exact match in alias dictionary
        if skill_lower in self.alias_dict:
            return self.alias_dict[skill_lower]
        
        # Step 2: Fuzzy match against canonical skills
        if self.canonical_skills:
            result = process.extractOne(
                skill_clean,
                self.canonical_skills,
                scorer=fuzz.ratio,
                score_cutoff=self.fuzzy_threshold
            )
            
            if result:
                # result is a tuple: (matched_string, score, index)
                return result[0]
        
        # Step 3: Fallback to lowercase original skill
        return skill_lower
    
    def normalize_skills(self, skills: List[str]) -> List[str]:
        """Normalize a list of skills.
        
        Args:
            skills: List of skill names to normalize
            
        Returns:
            List of normalized canonical skill names
        """
        return [self.normalize_skill(skill) for skill in skills]
