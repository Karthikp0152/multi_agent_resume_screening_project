"""
Validation script for Task 7.1: SkillNormalizer Implementation

This script validates that all requirements (6.1-6.5) are satisfied.
"""

from src.skill_normalizer import SkillNormalizer
import json


def validate_requirement_6_1():
    """
    Requirement 6.1: THE Skill_Normalizer SHALL maintain an alias dictionary 
    mapping skill variations to canonical forms
    """
    print("\n=== Validating Requirement 6.1 ===")
    print("Requirement: Maintain alias dictionary mapping variations to canonical forms")
    
    # Load alias dictionary
    normalizer = SkillNormalizer({})
    alias_dict = normalizer.load_alias_dictionary("config/skill_aliases.json")
    
    # Verify dictionary structure
    assert isinstance(alias_dict, dict), "Alias dictionary must be a dict"
    assert len(alias_dict) > 0, "Alias dictionary must not be empty"
    
    # Verify mappings exist
    assert "js" in alias_dict, "Dictionary should contain 'js' alias"
    assert alias_dict["js"] == "JavaScript", "js should map to JavaScript"
    
    print(f"✓ Alias dictionary loaded with {len(alias_dict)} mappings")
    print(f"✓ Sample mapping: 'js' -> '{alias_dict['js']}'")
    print("✓ Requirement 6.1 SATISFIED")
    return True


def validate_requirement_6_2():
    """
    Requirement 6.2: WHEN a skill matches an alias dictionary entry, 
    THE Skill_Normalizer SHALL replace it with the canonical form
    """
    print("\n=== Validating Requirement 6.2 ===")
    print("Requirement: Replace exact matches with canonical form")
    
    # Create normalizer
    normalizer = SkillNormalizer({})
    alias_dict = normalizer.load_alias_dictionary("config/skill_aliases.json")
    normalizer = SkillNormalizer(alias_dict)
    
    # Test exact matches
    test_cases = [
        ("js", "JavaScript"),
        ("ml", "Machine Learning"),
        ("py", "Python"),
        ("react.js", "React"),
        ("k8s", "Kubernetes"),
    ]
    
    for input_skill, expected in test_cases:
        result = normalizer.normalize_skill(input_skill)
        assert result == expected, f"Failed: {input_skill} -> {result} (expected {expected})"
        print(f"✓ '{input_skill}' -> '{result}'")
    
    print("✓ Requirement 6.2 SATISFIED")
    return True


def validate_requirement_6_3():
    """
    Requirement 6.3: WHEN a skill does not match the alias dictionary, 
    THE Skill_Normalizer SHALL apply fuzzy matching to find similar canonical skills
    """
    print("\n=== Validating Requirement 6.3 ===")
    print("Requirement: Apply fuzzy matching for non-exact matches")
    
    # Create normalizer
    normalizer = SkillNormalizer({})
    alias_dict = normalizer.load_alias_dictionary("config/skill_aliases.json")
    normalizer = SkillNormalizer(alias_dict, fuzzy_threshold=85)
    
    # Test fuzzy matches (typos that should match)
    test_cases = [
        ("Pyton", "Python"),  # Missing 'h'
        ("JavaScritp", "JavaScript"),  # Transposed letters
    ]
    
    for input_skill, expected in test_cases:
        result = normalizer.normalize_skill(input_skill)
        assert result == expected, f"Failed: {input_skill} -> {result} (expected {expected})"
        print(f"✓ Fuzzy match: '{input_skill}' -> '{result}'")
    
    # Test fallback for skills that don't match
    unknown_skill = "CompletelyUnknownSkill123"
    result = normalizer.normalize_skill(unknown_skill)
    assert result == unknown_skill.lower(), "Unknown skills should fallback to lowercase"
    print(f"✓ Fallback: '{unknown_skill}' -> '{result}'")
    
    print("✓ Requirement 6.3 SATISFIED")
    return True


def validate_requirement_6_4():
    """
    Requirement 6.4: THE Skill_Normalizer SHALL output normalized skill names
    """
    print("\n=== Validating Requirement 6.4 ===")
    print("Requirement: Output normalized skill names")
    
    # Create normalizer
    normalizer = SkillNormalizer({})
    alias_dict = normalizer.load_alias_dictionary("config/skill_aliases.json")
    normalizer = SkillNormalizer(alias_dict)
    
    # Test single skill normalization
    input_skill = "js"
    result = normalizer.normalize_skill(input_skill)
    assert isinstance(result, str), "Output must be a string"
    assert result == "JavaScript", "Output must be normalized"
    print(f"✓ Single skill output: '{input_skill}' -> '{result}'")
    
    # Test list normalization
    input_skills = ["js", "ml", "py"]
    results = normalizer.normalize_skills(input_skills)
    assert isinstance(results, list), "Output must be a list"
    assert len(results) == len(input_skills), "Output length must match input"
    assert all(isinstance(s, str) for s in results), "All outputs must be strings"
    print(f"✓ List output: {input_skills} -> {results}")
    
    print("✓ Requirement 6.4 SATISFIED")
    return True


def validate_requirement_6_5():
    """
    Requirement 6.5: FOR ALL extracted skills, THE Skill_Normalizer 
    SHALL produce a normalized version
    """
    print("\n=== Validating Requirement 6.5 ===")
    print("Requirement: Normalize ALL extracted skills")
    
    # Create normalizer
    normalizer = SkillNormalizer({})
    alias_dict = normalizer.load_alias_dictionary("config/skill_aliases.json")
    normalizer = SkillNormalizer(alias_dict)
    
    # Test with various skill types
    all_skills = [
        "js",  # Exact match
        "JavaScript",  # Already canonical
        "Pyton",  # Fuzzy match
        "UnknownSkill",  # Fallback
        "ml",  # Exact match
        "",  # Empty string
        "   ",  # Whitespace
    ]
    
    results = normalizer.normalize_skills(all_skills)
    
    # Verify all skills were processed
    assert len(results) == len(all_skills), "All skills must be normalized"
    
    expected = ["JavaScript", "JavaScript", "Python", "unknownskill", "Machine Learning", "", ""]
    
    for i, (input_skill, result, expected_result) in enumerate(zip(all_skills, results, expected)):
        assert result == expected_result, f"Failed at index {i}: {input_skill} -> {result} (expected {expected_result})"
        print(f"✓ Skill {i+1}: '{input_skill}' -> '{result}'")
    
    print("✓ Requirement 6.5 SATISFIED")
    return True


def validate_implementation_details():
    """Validate implementation details from design document."""
    print("\n=== Validating Implementation Details ===")
    
    # Create normalizer
    normalizer = SkillNormalizer({})
    alias_dict = normalizer.load_alias_dictionary("config/skill_aliases.json")
    normalizer = SkillNormalizer(alias_dict, fuzzy_threshold=85)
    
    # Verify __init__ implementation
    assert hasattr(normalizer, 'alias_dict'), "Must have alias_dict attribute"
    assert hasattr(normalizer, 'fuzzy_threshold'), "Must have fuzzy_threshold attribute"
    assert hasattr(normalizer, 'canonical_skills'), "Must have canonical_skills attribute"
    assert normalizer.fuzzy_threshold == 85, "Default threshold should be 85"
    print("✓ __init__() correctly implemented")
    
    # Verify load_alias_dictionary implementation
    assert hasattr(normalizer, 'load_alias_dictionary'), "Must have load_alias_dictionary method"
    loaded_dict = normalizer.load_alias_dictionary("config/skill_aliases.json")
    assert isinstance(loaded_dict, dict), "Must return dictionary"
    print("✓ load_alias_dictionary() correctly implemented")
    
    # Verify normalize_skill implementation
    assert hasattr(normalizer, 'normalize_skill'), "Must have normalize_skill method"
    result = normalizer.normalize_skill("js")
    assert result == "JavaScript", "Must normalize correctly"
    print("✓ normalize_skill() correctly implemented")
    
    # Verify normalize_skills implementation
    assert hasattr(normalizer, 'normalize_skills'), "Must have normalize_skills method"
    results = normalizer.normalize_skills(["js", "ml"])
    assert isinstance(results, list), "Must return list"
    print("✓ normalize_skills() correctly implemented")
    
    # Verify RapidFuzz usage with 85% threshold
    # Test that skills below threshold fallback
    very_different = "xyz123"
    result = normalizer.normalize_skill(very_different)
    assert result == very_different.lower(), "Skills below threshold should fallback"
    print("✓ RapidFuzz with 85% threshold correctly implemented")
    
    print("✓ All implementation details validated")
    return True


def main():
    """Run all validation checks."""
    print("=" * 70)
    print("TASK 7.1 VALIDATION: SkillNormalizer Implementation")
    print("=" * 70)
    
    try:
        # Validate all requirements
        validate_requirement_6_1()
        validate_requirement_6_2()
        validate_requirement_6_3()
        validate_requirement_6_4()
        validate_requirement_6_5()
        validate_implementation_details()
        
        print("\n" + "=" * 70)
        print("✓ ALL REQUIREMENTS SATISFIED")
        print("✓ TASK 7.1 COMPLETE")
        print("=" * 70)
        
        return True
        
    except AssertionError as e:
        print(f"\n✗ VALIDATION FAILED: {e}")
        return False
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        return False


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
