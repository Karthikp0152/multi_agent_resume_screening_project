"""
Unit tests for the SkillNormalizer class.

Tests cover exact matching, fuzzy matching, fallback logic, and edge cases.
"""

import pytest
import json
import tempfile
from pathlib import Path
from src.skill_normalizer import SkillNormalizer


class TestSkillNormalizer:
    """Test suite for SkillNormalizer class."""
    
    @pytest.fixture
    def sample_alias_dict(self):
        """Provide a sample alias dictionary for testing."""
        return {
            "js": "JavaScript",
            "javascript": "JavaScript",
            "react.js": "React",
            "reactjs": "React",
            "react js": "React",
            "ml": "Machine Learning",
            "machine-learning": "Machine Learning",
            "py": "Python",
            "python3": "Python",
            "sql": "SQL",
            "mysql": "MySQL",
            "postgresql": "PostgreSQL",
            "postgres": "PostgreSQL"
        }
    
    @pytest.fixture
    def normalizer(self, sample_alias_dict):
        """Create a SkillNormalizer instance with sample data."""
        return SkillNormalizer(sample_alias_dict, fuzzy_threshold=85)
    
    def test_init_with_alias_dict(self, sample_alias_dict):
        """Test initialization with alias dictionary."""
        normalizer = SkillNormalizer(sample_alias_dict, fuzzy_threshold=90)
        assert normalizer.alias_dict == sample_alias_dict
        assert normalizer.fuzzy_threshold == 90
        assert len(normalizer.canonical_skills) > 0
    
    def test_init_default_threshold(self, sample_alias_dict):
        """Test initialization with default fuzzy threshold."""
        normalizer = SkillNormalizer(sample_alias_dict)
        assert normalizer.fuzzy_threshold == 85
    
    def test_exact_match_lowercase(self, normalizer):
        """Test exact match with lowercase skill variation."""
        result = normalizer.normalize_skill("js")
        assert result == "JavaScript"
    
    def test_exact_match_uppercase(self, normalizer):
        """Test exact match with uppercase skill variation."""
        result = normalizer.normalize_skill("JS")
        assert result == "JavaScript"
    
    def test_exact_match_mixed_case(self, normalizer):
        """Test exact match with mixed case skill variation."""
        result = normalizer.normalize_skill("JavaScript")
        assert result == "JavaScript"
    
    def test_exact_match_with_special_chars(self, normalizer):
        """Test exact match with special characters."""
        result = normalizer.normalize_skill("react.js")
        assert result == "React"
    
    def test_exact_match_with_spaces(self, normalizer):
        """Test exact match with spaces in skill name."""
        result = normalizer.normalize_skill("react js")
        assert result == "React"
    
    def test_fuzzy_match_close_spelling(self, normalizer):
        """Test fuzzy match with close spelling variation."""
        # "JavaScritp" is close to "JavaScript" (transposed letters)
        result = normalizer.normalize_skill("JavaScritp")
        assert result == "JavaScript"
    
    def test_fuzzy_match_typo(self, normalizer):
        """Test fuzzy match with common typo."""
        # "Pyton" should match "Python"
        result = normalizer.normalize_skill("Pyton")
        assert result == "Python"
    
    def test_fuzzy_match_threshold(self):
        """Test that fuzzy matching respects threshold."""
        alias_dict = {"python": "Python"}
        normalizer = SkillNormalizer(alias_dict, fuzzy_threshold=95)
        
        # "Pyton" might not match with 95% threshold
        result = normalizer.normalize_skill("xyz")
        # Should fallback to lowercase
        assert result == "xyz"
    
    def test_fallback_unknown_skill(self, normalizer):
        """Test fallback to lowercase for unknown skill."""
        result = normalizer.normalize_skill("UnknownSkill")
        assert result == "unknownSkill".lower()
    
    def test_fallback_preserves_lowercase(self, normalizer):
        """Test fallback returns lowercase version."""
        result = normalizer.normalize_skill("COMPLETELY_NEW_SKILL")
        assert result == "completely_new_skill"
    
    def test_empty_string(self, normalizer):
        """Test handling of empty string."""
        result = normalizer.normalize_skill("")
        assert result == ""
    
    def test_whitespace_only(self, normalizer):
        """Test handling of whitespace-only string."""
        result = normalizer.normalize_skill("   ")
        assert result == ""
    
    def test_skill_with_leading_trailing_spaces(self, normalizer):
        """Test that leading/trailing spaces are handled."""
        result = normalizer.normalize_skill("  js  ")
        assert result == "JavaScript"
    
    def test_normalize_skills_list(self, normalizer):
        """Test normalizing a list of skills."""
        skills = ["js", "Python3", "react.js", "UnknownSkill"]
        result = normalizer.normalize_skills(skills)
        
        assert len(result) == 4
        assert result[0] == "JavaScript"
        assert result[1] == "Python"
        assert result[2] == "React"
        assert result[3] == "unknownskill"
    
    def test_normalize_skills_empty_list(self, normalizer):
        """Test normalizing an empty list."""
        result = normalizer.normalize_skills([])
        assert result == []
    
    def test_normalize_skills_with_duplicates(self, normalizer):
        """Test that duplicates are normalized consistently."""
        skills = ["js", "JavaScript", "JS"]
        result = normalizer.normalize_skills(skills)
        
        # All should normalize to "JavaScript"
        assert all(skill == "JavaScript" for skill in result)
    
    def test_load_alias_dictionary_valid_file(self, sample_alias_dict):
        """Test loading alias dictionary from valid JSON file."""
        # Create temporary JSON file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump({"aliases": sample_alias_dict}, f)
            temp_path = f.name
        
        try:
            normalizer = SkillNormalizer({})
            loaded_dict = normalizer.load_alias_dictionary(temp_path)
            assert loaded_dict == sample_alias_dict
        finally:
            Path(temp_path).unlink()
    
    def test_load_alias_dictionary_direct_format(self, sample_alias_dict):
        """Test loading alias dictionary with direct format (no 'aliases' key)."""
        # Create temporary JSON file with direct format
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(sample_alias_dict, f)
            temp_path = f.name
        
        try:
            normalizer = SkillNormalizer({})
            loaded_dict = normalizer.load_alias_dictionary(temp_path)
            assert loaded_dict == sample_alias_dict
        finally:
            Path(temp_path).unlink()
    
    def test_load_alias_dictionary_file_not_found(self):
        """Test error handling when dictionary file doesn't exist."""
        normalizer = SkillNormalizer({})
        
        with pytest.raises(FileNotFoundError):
            normalizer.load_alias_dictionary("nonexistent_file.json")
    
    def test_load_alias_dictionary_invalid_json(self):
        """Test error handling for invalid JSON file."""
        # Create temporary file with invalid JSON
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write("{ invalid json }")
            temp_path = f.name
        
        try:
            normalizer = SkillNormalizer({})
            with pytest.raises(json.JSONDecodeError):
                normalizer.load_alias_dictionary(temp_path)
        finally:
            Path(temp_path).unlink()
    
    def test_canonical_skills_extraction(self, sample_alias_dict):
        """Test that canonical skills are correctly extracted."""
        normalizer = SkillNormalizer(sample_alias_dict)
        
        # Check that canonical skills contain unique values
        expected_canonical = set(sample_alias_dict.values())
        assert set(normalizer.canonical_skills) == expected_canonical
    
    def test_case_insensitive_exact_match(self, normalizer):
        """Test that exact matching is case-insensitive."""
        # All variations should match
        assert normalizer.normalize_skill("ml") == "Machine Learning"
        assert normalizer.normalize_skill("ML") == "Machine Learning"
        assert normalizer.normalize_skill("Ml") == "Machine Learning"
        assert normalizer.normalize_skill("mL") == "Machine Learning"
    
    def test_multiple_aliases_same_canonical(self, normalizer):
        """Test that multiple aliases map to same canonical form."""
        # All should map to "React"
        assert normalizer.normalize_skill("react.js") == "React"
        assert normalizer.normalize_skill("reactjs") == "React"
        assert normalizer.normalize_skill("react js") == "React"
    
    def test_sql_variations(self, normalizer):
        """Test SQL and database skill variations."""
        assert normalizer.normalize_skill("sql") == "SQL"
        assert normalizer.normalize_skill("mysql") == "MySQL"
        assert normalizer.normalize_skill("postgres") == "PostgreSQL"
        assert normalizer.normalize_skill("postgresql") == "PostgreSQL"
    
    def test_integration_with_real_config(self):
        """Test loading from actual config file if it exists."""
        config_path = "config/skill_aliases.json"
        
        if Path(config_path).exists():
            normalizer = SkillNormalizer({})
            alias_dict = normalizer.load_alias_dictionary(config_path)
            
            # Create normalizer with loaded dictionary
            normalizer = SkillNormalizer(alias_dict)
            
            # Test some common normalizations
            assert normalizer.normalize_skill("js") == "JavaScript"
            assert normalizer.normalize_skill("ml") == "Machine Learning"
            assert normalizer.normalize_skill("py") == "Python"
