"""
Unit tests for the SkillNormalizer component.

Tests cover:
- Exact alias dictionary matches
- Fuzzy matching with various similarity thresholds
- Handling of skills not in dictionary
- Case normalization
- Alias dictionary loading
- Edge cases and error handling

Requirements: 6.1, 6.2, 6.3, 6.4, 6.5
"""

import pytest
import json
import tempfile
from pathlib import Path
from src.skill_normalizer import SkillNormalizer


class TestSkillNormalizerInitialization:
    """Tests for SkillNormalizer initialization."""
    
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
            "machine learning": "Machine Learning",
            "py": "Python",
            "python3": "Python",
            "python": "Python",
            "sql": "SQL",
            "mysql": "MySQL",
            "postgresql": "PostgreSQL",
            "postgres": "PostgreSQL"
        }
    
    def test_init_with_alias_dict(self, sample_alias_dict):
        """Test initialization with alias dictionary."""
        normalizer = SkillNormalizer(sample_alias_dict, fuzzy_threshold=90)
        assert normalizer.alias_dict == sample_alias_dict
        assert normalizer.fuzzy_threshold == 90
        assert len(normalizer.canonical_skills) > 0
    
    def test_init_default_threshold(self, sample_alias_dict):
        """Test initialization with default fuzzy threshold of 85."""
        normalizer = SkillNormalizer(sample_alias_dict)
        assert normalizer.fuzzy_threshold == 85
    
    def test_canonical_skills_extraction(self, sample_alias_dict):
        """Test that canonical skills are correctly extracted from alias dict."""
        normalizer = SkillNormalizer(sample_alias_dict)
        
        # Check that canonical skills contain unique values
        expected_canonical = set(sample_alias_dict.values())
        assert set(normalizer.canonical_skills) == expected_canonical
    
    def test_init_with_empty_dict(self):
        """Test initialization with empty alias dictionary."""
        normalizer = SkillNormalizer({})
        assert normalizer.alias_dict == {}
        assert normalizer.canonical_skills == []
        assert normalizer.fuzzy_threshold == 85


class TestExactAliasMatching:
    """Tests for exact alias dictionary matches (Requirement 6.2)."""
    
    @pytest.fixture
    def normalizer(self):
        """Create a SkillNormalizer instance with sample data."""
        alias_dict = {
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
        return SkillNormalizer(alias_dict, fuzzy_threshold=85)
    
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
        """Test exact match with special characters (dots)."""
        result = normalizer.normalize_skill("react.js")
        assert result == "React"
    
    def test_exact_match_with_spaces(self, normalizer):
        """Test exact match with spaces in skill name."""
        result = normalizer.normalize_skill("react js")
        assert result == "React"
    
    def test_exact_match_with_hyphens(self, normalizer):
        """Test exact match with hyphens in skill name."""
        result = normalizer.normalize_skill("machine-learning")
        assert result == "Machine Learning"
    
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
    
    def test_skill_with_leading_trailing_spaces(self, normalizer):
        """Test that leading/trailing spaces are handled correctly."""
        result = normalizer.normalize_skill("  js  ")
        assert result == "JavaScript"
        
        result = normalizer.normalize_skill("  python3  ")
        assert result == "Python"


class TestFuzzyMatching:
    """Tests for fuzzy matching with various similarity thresholds (Requirement 6.3)."""
    
    @pytest.fixture
    def normalizer(self):
        """Create a SkillNormalizer instance for fuzzy matching tests."""
        alias_dict = {
            "python": "Python",
            "javascript": "JavaScript",
            "machine learning": "Machine Learning"
        }
        return SkillNormalizer(alias_dict, fuzzy_threshold=85)
    
    def test_fuzzy_match_close_spelling(self, normalizer):
        """Test fuzzy match with close spelling variation (transposed letters)."""
        # "JavaScritp" is close to "JavaScript" (transposed letters)
        result = normalizer.normalize_skill("JavaScritp")
        assert result == "JavaScript"
    
    def test_fuzzy_match_typo(self, normalizer):
        """Test fuzzy match with common typo."""
        # "Pyton" should match "Python"
        result = normalizer.normalize_skill("Pyton")
        assert result == "Python"
    
    def test_fuzzy_match_missing_character(self, normalizer):
        """Test fuzzy match with missing character."""
        # "Pythn" should match "Python"
        result = normalizer.normalize_skill("Pythn")
        assert result == "Python"
    
    def test_fuzzy_match_extra_character(self, normalizer):
        """Test fuzzy match with extra character."""
        # "Pythoon" should match "Python"
        result = normalizer.normalize_skill("Pythoon")
        assert result == "Python"
    
    def test_fuzzy_match_respects_threshold_high(self):
        """Test that fuzzy matching respects high threshold (95%)."""
        alias_dict = {"python": "Python"}
        normalizer = SkillNormalizer(alias_dict, fuzzy_threshold=95)
        
        # "xyz" should not match with 95% threshold
        result = normalizer.normalize_skill("xyz")
        # Should fallback to lowercase
        assert result == "xyz"
    
    def test_fuzzy_match_respects_threshold_low(self):
        """Test that fuzzy matching with lower threshold (70%) is more permissive."""
        alias_dict = {"python": "Python"}
        normalizer = SkillNormalizer(alias_dict, fuzzy_threshold=70)
        
        # "Pyth" might match with 70% threshold
        result = normalizer.normalize_skill("Pyth")
        # With lower threshold, should match
        assert result == "Python"
    
    def test_fuzzy_match_threshold_boundary(self):
        """Test fuzzy matching at exact threshold boundary."""
        alias_dict = {"python": "Python"}
        normalizer = SkillNormalizer(alias_dict, fuzzy_threshold=85)
        
        # Test a skill that's close to threshold
        result = normalizer.normalize_skill("Pyton")
        # Should match as it's above threshold
        assert result == "Python"
    
    def test_fuzzy_match_multi_word_skill(self, normalizer):
        """Test fuzzy matching with multi-word skills."""
        # "Machine Lerning" should match "Machine Learning"
        result = normalizer.normalize_skill("Machine Lerning")
        assert result == "Machine Learning"
    
    def test_fuzzy_match_case_variation(self, normalizer):
        """Test fuzzy matching handles case variations."""
        # "PYTHON" should match "Python"
        result = normalizer.normalize_skill("PYTHON")
        assert result == "Python"


class TestSkillsNotInDictionary:
    """Tests for handling of skills not in dictionary (Requirement 6.4)."""
    
    @pytest.fixture
    def normalizer(self):
        """Create a SkillNormalizer instance with limited dictionary."""
        alias_dict = {
            "js": "JavaScript",
            "py": "Python"
        }
        return SkillNormalizer(alias_dict, fuzzy_threshold=85)
    
    def test_fallback_unknown_skill(self, normalizer):
        """Test fallback to lowercase for completely unknown skill."""
        result = normalizer.normalize_skill("UnknownSkill")
        assert result == "unknownskill"
    
    def test_fallback_preserves_lowercase(self, normalizer):
        """Test fallback returns lowercase version."""
        result = normalizer.normalize_skill("COMPLETELY_NEW_SKILL")
        assert result == "completely_new_skill"
    
    def test_fallback_with_special_characters(self, normalizer):
        """Test fallback with special characters."""
        result = normalizer.normalize_skill("New-Skill.v2")
        assert result == "new-skill.v2"
    
    def test_fallback_with_numbers(self, normalizer):
        """Test fallback with numbers in skill name."""
        result = normalizer.normalize_skill("Python3.11")
        # Should fallback to lowercase since exact match not found
        assert result == "python3.11"
    
    def test_unknown_skill_not_fuzzy_matched(self):
        """Test that completely different skills don't fuzzy match."""
        alias_dict = {"python": "Python"}
        normalizer = SkillNormalizer(alias_dict, fuzzy_threshold=85)
        
        # "Cooking" should not match "Python"
        result = normalizer.normalize_skill("Cooking")
        assert result == "cooking"


class TestCaseNormalization:
    """Tests for case normalization (Requirement 6.4)."""
    
    @pytest.fixture
    def normalizer(self):
        """Create a SkillNormalizer instance."""
        alias_dict = {
            "python": "Python",
            "javascript": "JavaScript",
            "sql": "SQL"
        }
        return SkillNormalizer(alias_dict, fuzzy_threshold=85)
    
    def test_lowercase_input(self, normalizer):
        """Test normalization of lowercase input."""
        result = normalizer.normalize_skill("python")
        assert result == "Python"
    
    def test_uppercase_input(self, normalizer):
        """Test normalization of uppercase input."""
        result = normalizer.normalize_skill("PYTHON")
        assert result == "Python"
    
    def test_mixed_case_input(self, normalizer):
        """Test normalization of mixed case input."""
        result = normalizer.normalize_skill("PyThOn")
        assert result == "Python"
    
    def test_title_case_input(self, normalizer):
        """Test normalization of title case input."""
        result = normalizer.normalize_skill("Javascript")
        assert result == "JavaScript"
    
    def test_case_normalization_fallback(self, normalizer):
        """Test that fallback always returns lowercase."""
        result = normalizer.normalize_skill("UnknownSkill")
        assert result == "unknownskill"
        assert result.islower()


class TestAliasDictionaryLoading:
    """Tests for alias dictionary loading (Requirement 6.5)."""
    
    def test_load_alias_dictionary_valid_file_nested_format(self):
        """Test loading alias dictionary from valid JSON file with 'aliases' key."""
        sample_dict = {
            "js": "JavaScript",
            "py": "Python"
        }
        
        # Create temporary JSON file with nested format
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump({"aliases": sample_dict}, f)
            temp_path = f.name
        
        try:
            normalizer = SkillNormalizer({})
            loaded_dict = normalizer.load_alias_dictionary(temp_path)
            assert loaded_dict == sample_dict
        finally:
            Path(temp_path).unlink()
    
    def test_load_alias_dictionary_direct_format(self):
        """Test loading alias dictionary with direct format (no 'aliases' key)."""
        sample_dict = {
            "js": "JavaScript",
            "py": "Python"
        }
        
        # Create temporary JSON file with direct format
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(sample_dict, f)
            temp_path = f.name
        
        try:
            normalizer = SkillNormalizer({})
            loaded_dict = normalizer.load_alias_dictionary(temp_path)
            assert loaded_dict == sample_dict
        finally:
            Path(temp_path).unlink()
    
    def test_load_alias_dictionary_file_not_found(self):
        """Test error handling when dictionary file doesn't exist."""
        normalizer = SkillNormalizer({})
        
        with pytest.raises(FileNotFoundError) as exc_info:
            normalizer.load_alias_dictionary("nonexistent_file.json")
        
        assert "Alias dictionary not found" in str(exc_info.value)
    
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
    
    def test_load_alias_dictionary_empty_file(self):
        """Test loading empty JSON file."""
        # Create temporary empty JSON file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump({}, f)
            temp_path = f.name
        
        try:
            normalizer = SkillNormalizer({})
            loaded_dict = normalizer.load_alias_dictionary(temp_path)
            assert loaded_dict == {}
        finally:
            Path(temp_path).unlink()
    
    def test_load_alias_dictionary_with_unicode(self):
        """Test loading dictionary with unicode characters."""
        sample_dict = {
            "c++": "C++",
            "c#": "C#",
            "café": "Café"
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
            json.dump(sample_dict, f, ensure_ascii=False)
            temp_path = f.name
        
        try:
            normalizer = SkillNormalizer({})
            loaded_dict = normalizer.load_alias_dictionary(temp_path)
            assert loaded_dict == sample_dict
        finally:
            Path(temp_path).unlink()


class TestNormalizeSkillsList:
    """Tests for normalizing lists of skills."""
    
    @pytest.fixture
    def normalizer(self):
        """Create a SkillNormalizer instance."""
        alias_dict = {
            "js": "JavaScript",
            "python3": "Python",
            "react.js": "React",
            "ml": "Machine Learning"
        }
        return SkillNormalizer(alias_dict, fuzzy_threshold=85)
    
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
        assert len(result) == 3
        assert all(skill == "JavaScript" for skill in result)
    
    def test_normalize_skills_mixed_known_unknown(self, normalizer):
        """Test normalizing mix of known and unknown skills."""
        skills = ["js", "UnknownSkill1", "python3", "UnknownSkill2"]
        result = normalizer.normalize_skills(skills)
        
        assert len(result) == 4
        assert result[0] == "JavaScript"
        assert result[1] == "unknownskill1"
        assert result[2] == "Python"
        assert result[3] == "unknownskill2"
    
    def test_normalize_skills_preserves_order(self, normalizer):
        """Test that skill order is preserved."""
        skills = ["react.js", "js", "ml"]
        result = normalizer.normalize_skills(skills)
        
        assert result[0] == "React"
        assert result[1] == "JavaScript"
        assert result[2] == "Machine Learning"


class TestEdgeCases:
    """Tests for edge cases and boundary conditions."""
    
    @pytest.fixture
    def normalizer(self):
        """Create a SkillNormalizer instance."""
        alias_dict = {"python": "Python"}
        return SkillNormalizer(alias_dict, fuzzy_threshold=85)
    
    def test_empty_string(self, normalizer):
        """Test handling of empty string."""
        result = normalizer.normalize_skill("")
        assert result == ""
    
    def test_whitespace_only(self, normalizer):
        """Test handling of whitespace-only string."""
        result = normalizer.normalize_skill("   ")
        assert result == ""
    
    def test_tab_and_newline_characters(self, normalizer):
        """Test handling of tab and newline characters."""
        result = normalizer.normalize_skill("\t\n")
        assert result == ""
    
    def test_very_long_skill_name(self, normalizer):
        """Test handling of very long skill name."""
        long_skill = "A" * 1000
        result = normalizer.normalize_skill(long_skill)
        assert result == long_skill.lower()
    
    def test_skill_with_only_special_characters(self, normalizer):
        """Test handling of skill with only special characters."""
        result = normalizer.normalize_skill("@#$%")
        assert result == "@#$%"
    
    def test_skill_with_numbers_only(self, normalizer):
        """Test handling of skill with only numbers."""
        result = normalizer.normalize_skill("12345")
        assert result == "12345"
    
    def test_none_in_skills_list(self, normalizer):
        """Test handling of None values in skills list."""
        # This tests robustness - implementation should handle or document this
        skills = ["python", None, "javascript"]
        try:
            result = normalizer.normalize_skills(skills)
            # If it handles None, check the result
            assert len(result) == 3
        except (TypeError, AttributeError):
            # If it raises an error, that's also acceptable
            pass


class TestIntegrationWithRealConfig:
    """Integration tests with actual configuration file."""
    
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
        else:
            pytest.skip("Config file not found")
    
    def test_real_config_structure(self):
        """Test that real config file has expected structure."""
        config_path = "config/skill_aliases.json"
        
        if Path(config_path).exists():
            with open(config_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Check structure
            assert isinstance(data, dict)
            
            # If it has 'aliases' key, check that
            if "aliases" in data:
                assert isinstance(data["aliases"], dict)
            else:
                # Direct format should be a dict
                assert all(isinstance(k, str) and isinstance(v, str) for k, v in data.items())
        else:
            pytest.skip("Config file not found")


class TestNormalizationConsistency:
    """Tests for normalization consistency and idempotency."""
    
    @pytest.fixture
    def normalizer(self):
        """Create a SkillNormalizer instance."""
        alias_dict = {
            "js": "JavaScript",
            "javascript": "JavaScript",
            "python": "Python"
        }
        return SkillNormalizer(alias_dict, fuzzy_threshold=85)
    
    def test_normalization_is_idempotent(self, normalizer):
        """Test that normalizing twice gives same result."""
        skill = "js"
        result1 = normalizer.normalize_skill(skill)
        result2 = normalizer.normalize_skill(result1)
        
        # Normalizing the normalized result should give same output
        assert result1 == result2
    
    def test_consistent_normalization_across_calls(self, normalizer):
        """Test that same input always gives same output."""
        skill = "JavaScript"
        results = [normalizer.normalize_skill(skill) for _ in range(10)]
        
        # All results should be identical
        assert all(r == results[0] for r in results)
    
    def test_batch_vs_individual_normalization(self, normalizer):
        """Test that batch normalization matches individual normalization."""
        skills = ["js", "python", "UnknownSkill"]
        
        # Normalize individually
        individual_results = [normalizer.normalize_skill(s) for s in skills]
        
        # Normalize as batch
        batch_results = normalizer.normalize_skills(skills)
        
        # Results should match
        assert individual_results == batch_results
