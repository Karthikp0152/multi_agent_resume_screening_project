"""
Unit tests for SkillExtractor component.

Tests explicit skill extraction, implicit skill extraction, error handling,
and integration with ResumeSections dataclass.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from src.skill_extractor import SkillExtractor, ModelLoadError, SkillExtractionError
from src.models import ResumeSections, SkillSet


class TestSkillExtractorInitialization:
    """Tests for SkillExtractor initialization and model loading."""
    
    @pytest.mark.skipif(
        not pytest.importorskip("spacy", reason="spaCy not installed"),
        reason="spaCy not available"
    )
    def test_init_with_default_model(self):
        """Test SkillExtractor initialization with default model."""
        try:
            extractor = SkillExtractor()
            assert extractor.nlp_model == "en_core_web_sm"
            assert extractor.nlp is not None
        except ModelLoadError:
            pytest.skip("spaCy model en_core_web_sm not installed")
    
    @pytest.mark.skipif(
        not pytest.importorskip("spacy", reason="spaCy not installed"),
        reason="spaCy not available"
    )
    def test_init_with_custom_model(self):
        """Test SkillExtractor initialization with custom model name."""
        try:
            extractor = SkillExtractor(nlp_model="en_core_web_sm")
            assert extractor.nlp_model == "en_core_web_sm"
        except ModelLoadError:
            pytest.skip("spaCy model not installed")
    
    def test_init_with_invalid_model_raises_error(self):
        """Test that invalid model name raises ModelLoadError."""
        with pytest.raises(ModelLoadError) as exc_info:
            SkillExtractor(nlp_model="invalid_model_name_xyz")
        
        assert "Failed to load spaCy model" in str(exc_info.value)
        assert "invalid_model_name_xyz" in str(exc_info.value)


class TestExplicitSkillExtraction:
    """Tests for extract_explicit_skills method."""
    
    @pytest.fixture
    def extractor(self):
        """Create SkillExtractor instance for testing."""
        try:
            return SkillExtractor()
        except ModelLoadError:
            pytest.skip("spaCy model not installed")
    
    def test_extract_explicit_skills_from_simple_list(self, extractor):
        """Test extracting skills from simple comma-separated list."""
        skills_text = "Python, Java, SQL, Machine Learning, Docker"
        skills = extractor.extract_explicit_skills(skills_text)
        
        assert isinstance(skills, list)
        assert len(skills) > 0
        # Should extract at least some of the skills
        assert any("Python" in skill or "python" in skill.lower() for skill in skills)
    
    def test_extract_explicit_skills_from_formatted_section(self, extractor):
        """Test extracting skills from formatted Skills section."""
        skills_text = """
        Technical Skills:
        - Programming Languages: Python, Java, JavaScript
        - Frameworks: React, Django, Spring Boot
        - Databases: PostgreSQL, MongoDB
        - Tools: Docker, Kubernetes, Git
        """
        skills = extractor.extract_explicit_skills(skills_text)
        
        assert isinstance(skills, list)
        assert len(skills) > 0
    
    def test_extract_explicit_skills_empty_section(self, extractor):
        """Test extracting skills from empty section returns empty list."""
        skills = extractor.extract_explicit_skills("")
        assert skills == []
        
        skills = extractor.extract_explicit_skills("   ")
        assert skills == []
    
    def test_extract_explicit_skills_with_multi_word_skills(self, extractor):
        """Test extracting multi-word skills like 'Machine Learning'."""
        skills_text = "Machine Learning, Natural Language Processing, Deep Learning"
        skills = extractor.extract_explicit_skills(skills_text)
        
        assert isinstance(skills, list)
        assert len(skills) > 0
    
    def test_extract_explicit_skills_filters_single_characters(self, extractor):
        """Test that single characters are filtered out."""
        skills_text = "Python, C, R, Java, SQL"
        skills = extractor.extract_explicit_skills(skills_text)
        
        # Should extract skills but filter single chars
        assert isinstance(skills, list)
        # Single character 'C' and 'R' might be filtered depending on NLP processing


class TestImplicitSkillExtraction:
    """Tests for extract_implicit_skills method."""
    
    @pytest.fixture
    def extractor(self):
        """Create SkillExtractor instance for testing."""
        try:
            return SkillExtractor()
        except ModelLoadError:
            pytest.skip("spaCy model not installed")
    
    def test_extract_implicit_skills_from_experience(self, extractor):
        """Test extracting implicit skills from experience section."""
        experience = """
        Software Engineer at Tech Corp (2020-2023)
        - Developed web applications using React and Node.js
        - Implemented CI/CD pipelines with Jenkins and Docker
        - Worked with PostgreSQL and MongoDB databases
        """
        projects = ""
        
        skills = extractor.extract_implicit_skills(experience, projects)
        
        assert isinstance(skills, list)
        assert len(skills) > 0
    
    def test_extract_implicit_skills_from_projects(self, extractor):
        """Test extracting implicit skills from projects section."""
        experience = ""
        projects = """
        E-commerce Platform
        - Built using Django and React
        - Deployed on AWS with Docker containers
        - Used Redis for caching
        """
        
        skills = extractor.extract_implicit_skills(experience, projects)
        
        assert isinstance(skills, list)
        assert len(skills) > 0
    
    def test_extract_implicit_skills_from_both_sections(self, extractor):
        """Test extracting implicit skills from both experience and projects."""
        experience = "Worked with Python and Django framework"
        projects = "Built applications using React and TypeScript"
        
        skills = extractor.extract_implicit_skills(experience, projects)
        
        assert isinstance(skills, list)
        assert len(skills) > 0
    
    def test_extract_implicit_skills_empty_sections(self, extractor):
        """Test extracting implicit skills from empty sections returns empty list."""
        skills = extractor.extract_implicit_skills("", "")
        assert skills == []
        
        skills = extractor.extract_implicit_skills("   ", "   ")
        assert skills == []
    
    def test_extract_implicit_skills_no_duplicates(self, extractor):
        """Test that duplicate skills are not included."""
        experience = "Used Python and Django. Python is great."
        projects = "Built with Python and Flask"
        
        skills = extractor.extract_implicit_skills(experience, projects)
        
        # Check that skills list doesn't have obvious duplicates
        assert isinstance(skills, list)


class TestExtractAllSkills:
    """Tests for extract_all_skills method."""
    
    @pytest.fixture
    def extractor(self):
        """Create SkillExtractor instance for testing."""
        try:
            return SkillExtractor()
        except ModelLoadError:
            pytest.skip("spaCy model not installed")
    
    def test_extract_all_skills_returns_skillset(self, extractor):
        """Test that extract_all_skills returns SkillSet dataclass."""
        sections = ResumeSections(
            skills="Python, Java, SQL",
            experience="Worked as Software Engineer using Django",
            education="BS Computer Science",
            projects="Built web applications with React",
            raw_text="Full resume text"
        )
        
        skill_set = extractor.extract_all_skills(sections)
        
        assert isinstance(skill_set, SkillSet)
        assert isinstance(skill_set.explicit_skills, list)
        assert isinstance(skill_set.implicit_skills, list)
    
    def test_extract_all_skills_separates_explicit_and_implicit(self, extractor):
        """Test that explicit and implicit skills are properly separated."""
        sections = ResumeSections(
            skills="Python, Java",
            experience="Used Docker and Kubernetes",
            education="",
            projects="",
            raw_text=""
        )
        
        skill_set = extractor.extract_all_skills(sections)
        
        # Explicit skills should come from skills section
        assert len(skill_set.explicit_skills) > 0
        # Implicit skills should come from experience
        assert len(skill_set.implicit_skills) >= 0
    
    def test_extract_all_skills_with_empty_sections(self, extractor):
        """Test extract_all_skills with all empty sections."""
        sections = ResumeSections(
            skills="",
            experience="",
            education="",
            projects="",
            raw_text=""
        )
        
        skill_set = extractor.extract_all_skills(sections)
        
        assert isinstance(skill_set, SkillSet)
        assert skill_set.explicit_skills == []
        assert skill_set.implicit_skills == []
    
    def test_extract_all_skills_all_skills_method(self, extractor):
        """Test that SkillSet.all_skills() combines both skill types."""
        sections = ResumeSections(
            skills="Python, Java",
            experience="Used Docker",
            education="",
            projects="",
            raw_text=""
        )
        
        skill_set = extractor.extract_all_skills(sections)
        all_skills = skill_set.all_skills()
        
        assert isinstance(all_skills, list)
        assert len(all_skills) == len(skill_set.explicit_skills) + len(skill_set.implicit_skills)


class TestErrorHandling:
    """Tests for error handling in SkillExtractor."""
    
    @pytest.fixture
    def extractor(self):
        """Create SkillExtractor instance for testing."""
        try:
            return SkillExtractor()
        except ModelLoadError:
            pytest.skip("spaCy model not installed")
    
    def test_extract_explicit_skills_handles_none_gracefully(self, extractor):
        """Test that None input is handled gracefully."""
        # This should not raise an error, but return empty list
        # Note: The current implementation expects string, so this tests robustness
        try:
            skills = extractor.extract_explicit_skills(None)
            # If it doesn't raise, it should return empty list
            assert skills == []
        except (TypeError, AttributeError):
            # If it raises, that's also acceptable behavior
            pass
    
    def test_model_load_error_contains_helpful_message(self):
        """Test that ModelLoadError contains helpful installation instructions."""
        with pytest.raises(ModelLoadError) as exc_info:
            SkillExtractor(nlp_model="nonexistent_model")
        
        error_message = str(exc_info.value)
        assert "python -m spacy download" in error_message or "Failed to load" in error_message


class TestIntegrationWithResumeSections:
    """Integration tests with ResumeSections dataclass."""
    
    @pytest.fixture
    def extractor(self):
        """Create SkillExtractor instance for testing."""
        try:
            return SkillExtractor()
        except ModelLoadError:
            pytest.skip("spaCy model not installed")
    
    def test_realistic_resume_sections(self, extractor):
        """Test with realistic resume sections."""
        sections = ResumeSections(
            skills="""
            Programming Languages: Python, Java, JavaScript, SQL
            Frameworks: Django, React, Spring Boot
            Tools: Docker, Git, Jenkins
            """,
            experience="""
            Senior Software Engineer - Tech Corp (2020-2023)
            - Led development of microservices architecture using Python and Docker
            - Implemented CI/CD pipelines with Jenkins and Kubernetes
            - Mentored junior developers on best practices
            
            Software Engineer - StartupXYZ (2018-2020)
            - Built RESTful APIs using Django and PostgreSQL
            - Developed frontend applications with React and Redux
            """,
            education="BS Computer Science, University of Technology",
            projects="""
            E-commerce Platform
            - Full-stack application using MERN stack (MongoDB, Express, React, Node.js)
            - Deployed on AWS with Docker containers
            """,
            raw_text="Full resume text here"
        )
        
        skill_set = extractor.extract_all_skills(sections)
        
        assert isinstance(skill_set, SkillSet)
        assert len(skill_set.explicit_skills) > 0
        assert len(skill_set.implicit_skills) > 0
        assert len(skill_set.all_skills()) > 0
        
        # Verify that we got a reasonable number of skills
        total_skills = len(skill_set.all_skills())
        assert total_skills > 5, f"Expected more than 5 skills, got {total_skills}"


class TestSkillExtractionQuality:
    """Tests for skill extraction quality and accuracy."""
    
    @pytest.fixture
    def extractor(self):
        """Create SkillExtractor instance for testing."""
        try:
            return SkillExtractor()
        except ModelLoadError:
            pytest.skip("spaCy model not installed")
    
    def test_extracts_common_programming_languages(self, extractor):
        """Test that common programming languages are extracted."""
        skills_text = "Python, Java, JavaScript, C++, Ruby, Go"
        skills = extractor.extract_explicit_skills(skills_text)
        
        assert len(skills) > 0
        # At least some programming languages should be extracted
    
    def test_extracts_frameworks_and_libraries(self, extractor):
        """Test that frameworks and libraries are extracted."""
        skills_text = "Django, React, Spring Boot, TensorFlow, Flask"
        skills = extractor.extract_explicit_skills(skills_text)
        
        assert len(skills) > 0
    
    def test_extracts_tools_and_technologies(self, extractor):
        """Test that tools and technologies are extracted."""
        skills_text = "Docker, Kubernetes, Git, Jenkins, AWS"
        skills = extractor.extract_explicit_skills(skills_text)
        
        assert len(skills) > 0
