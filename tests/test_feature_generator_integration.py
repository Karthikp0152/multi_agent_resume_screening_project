"""
Integration tests for FeatureGenerator with CSV and PDF data sources.

Tests verify that the FeatureGenerator correctly processes data from both
CSV files and PDF archives, maintaining consistent feature dimensionality.
"""

import pytest
import numpy as np
from pathlib import Path
import csv
import tempfile
import shutil

from src.feature_generator import FeatureGenerator
from src.resume_processor import ResumeProcessor
from src.models import ProcessorConfig


class TestCSVFeatureLoading:
    """Test feature generation from CSV data."""
    
    @pytest.fixture
    def temp_csv_file(self):
        """Create a temporary CSV file with sample resume data."""
        temp_dir = tempfile.mkdtemp()
        csv_path = Path(temp_dir) / "test_resumes.csv"
        
        # Create sample CSV data
        data = [
            {
                'ID': '001',
                'Resume_str': 'SKILLS\nPython, Java, SQL\n\nEXPERIENCE\nSoftware Engineer',
                'Resume_html': '<html>...</html>',
                'Category': 'ENGINEER'
            },
            {
                'ID': '002',
                'Resume_str': 'SKILLS\nJavaScript, React, Node.js\n\nEXPERIENCE\nWeb Developer',
                'Resume_html': '<html>...</html>',
                'Category': 'ENGINEER'
            },
            {
                'ID': '003',
                'Resume_str': 'SKILLS\nPython, Machine Learning, TensorFlow\n\nEXPERIENCE\nData Scientist',
                'Resume_html': '<html>...</html>',
                'Category': 'DATA_SCIENCE'
            }
        ]
        
        # Write CSV file
        with open(csv_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['ID', 'Resume_str', 'Resume_html', 'Category'])
            writer.writeheader()
            writer.writerows(data)
        
        yield csv_path
        
        # Cleanup
        shutil.rmtree(temp_dir)
    
    def test_load_csv_features(self, temp_csv_file):
        """Test loading features from CSV file."""
        # Initialize components
        config = ProcessorConfig(alias_dict_path="config/skill_aliases.json")
        processor = ResumeProcessor(config)
        generator = FeatureGenerator()
        
        # Load features from CSV
        feature_matrix, vocabulary, structured_resumes = generator.load_csv_features(
            csv_path=str(temp_csv_file),
            processor=processor
        )
        
        # Verify results
        assert feature_matrix.shape[0] == 3  # 3 resumes
        assert len(vocabulary) > 0  # Should have extracted skills
        assert len(structured_resumes) == 3
        
        # Verify all resumes have same feature dimensionality
        assert feature_matrix.shape[1] == len(vocabulary)
        
        # Verify binary values
        assert np.all((feature_matrix == 0) | (feature_matrix == 1))
    
    def test_csv_features_consistent_dimensionality(self, temp_csv_file):
        """Test that CSV features have consistent dimensionality."""
        config = ProcessorConfig(alias_dict_path="config/skill_aliases.json")
        processor = ResumeProcessor(config)
        generator = FeatureGenerator()
        
        feature_matrix, vocabulary, _ = generator.load_csv_features(
            csv_path=str(temp_csv_file),
            processor=processor
        )
        
        # All rows should have same number of columns
        for i in range(feature_matrix.shape[0]):
            assert feature_matrix[i].shape == (len(vocabulary),)
    
    def test_csv_features_vocabulary_building(self, temp_csv_file):
        """Test that vocabulary is built correctly from CSV data."""
        config = ProcessorConfig(alias_dict_path="config/skill_aliases.json")
        processor = ResumeProcessor(config)
        generator = FeatureGenerator()
        
        feature_matrix, vocabulary, structured_resumes = generator.load_csv_features(
            csv_path=str(temp_csv_file),
            processor=processor
        )
        
        # Vocabulary should contain normalized skills from all resumes
        all_skills = set()
        for resume in structured_resumes:
            all_skills.update(resume.normalized_skills)
        
        # Vocabulary should match unique skills
        assert set(vocabulary) == all_skills
        
        # Vocabulary should be sorted
        assert vocabulary == sorted(vocabulary)


class TestPDFFeatureLoading:
    """Test feature generation from PDF archive."""
    
    @pytest.fixture
    def temp_pdf_archive(self):
        """Create a temporary PDF archive structure."""
        temp_dir = tempfile.mkdtemp()
        archive_path = Path(temp_dir) / "archive"
        archive_path.mkdir()
        
        # Create category directories
        engineer_dir = archive_path / "ENGINEER"
        engineer_dir.mkdir()
        
        data_science_dir = archive_path / "DATA_SCIENCE"
        data_science_dir.mkdir()
        
        # Note: We can't create real PDFs easily in tests, so we'll skip this
        # In real integration tests, you would use actual PDF files
        
        yield archive_path
        
        # Cleanup
        shutil.rmtree(temp_dir)
    
    def test_pdf_features_structure(self):
        """Test that PDF feature loading has correct structure."""
        # This test would require actual PDF files
        # For now, we verify the method signature and basic structure
        generator = FeatureGenerator()
        
        # Verify method exists and has correct signature
        assert hasattr(generator, 'load_pdf_features')
        assert callable(generator.load_pdf_features)


class TestCrossSourceConsistency:
    """Test consistency between CSV and PDF feature generation."""
    
    def test_same_vocabulary_produces_same_dimensionality(self):
        """Test that same vocabulary produces consistent feature dimensions."""
        generator = FeatureGenerator()
        
        # Create mock resumes with same skills
        from src.models import StructuredResume, ResumeSections, SkillSet, ResumeMetadata
        
        resume1 = StructuredResume(
            resume_id="csv_001",
            job_category="ENGINEER",
            sections=ResumeSections("", "", "", "", ""),
            skills=SkillSet([], []),
            normalized_skills=["python", "java", "sql"],
            scores=None,
            metadata=ResumeMetadata("csv:test.csv:row_0", "2024-01-01", 100)
        )
        
        resume2 = StructuredResume(
            resume_id="pdf_001",
            job_category="ENGINEER",
            sections=ResumeSections("", "", "", "", ""),
            skills=SkillSet([], []),
            normalized_skills=["python", "javascript"],
            scores=None,
            metadata=ResumeMetadata("test.pdf", "2024-01-01", 100)
        )
        
        # Generate feature matrix
        feature_matrix, vocabulary = generator.generate_feature_matrix([resume1, resume2])
        
        # Both resumes should have same feature dimensionality
        assert feature_matrix.shape[0] == 2
        assert feature_matrix.shape[1] == len(vocabulary)
        
        # Verify each resume has correct features
        vocab_index = {skill: idx for idx, skill in enumerate(vocabulary)}
        
        # Resume 1 should have python, java, sql
        for skill in ["python", "java", "sql"]:
            if skill in vocab_index:
                assert feature_matrix[0, vocab_index[skill]] == 1
        
        # Resume 2 should have python, javascript
        for skill in ["python", "javascript"]:
            if skill in vocab_index:
                assert feature_matrix[1, vocab_index[skill]] == 1
    
    def test_feature_vectors_from_different_sources_compatible(self):
        """Test that feature vectors from CSV and PDF are compatible."""
        generator = FeatureGenerator()
        
        from src.models import StructuredResume, ResumeSections, SkillSet, ResumeMetadata
        
        # Simulate CSV resume
        csv_resume = StructuredResume(
            resume_id="csv_001",
            job_category="ENGINEER",
            sections=ResumeSections("", "", "", "", ""),
            skills=SkillSet([], []),
            normalized_skills=["python", "java"],
            scores=None,
            metadata=ResumeMetadata("csv:test.csv:row_0", "2024-01-01", 100)
        )
        
        # Simulate PDF resume
        pdf_resume = StructuredResume(
            resume_id="pdf_001",
            job_category="ENGINEER",
            sections=ResumeSections("", "", "", "", ""),
            skills=SkillSet([], []),
            normalized_skills=["python", "sql"],
            scores=None,
            metadata=ResumeMetadata("test.pdf", "2024-01-01", 100)
        )
        
        # Build vocabulary from both
        vocabulary = generator.build_vocabulary([csv_resume, pdf_resume])
        
        # Generate feature vectors
        csv_vector = generator.generate_feature_vector(
            csv_resume.normalized_skills,
            vocabulary
        )
        
        pdf_vector = generator.generate_feature_vector(
            pdf_resume.normalized_skills,
            vocabulary
        )
        
        # Both vectors should have same dimensionality
        assert csv_vector.shape == pdf_vector.shape
        assert csv_vector.shape == (len(vocabulary),)


class TestFeatureMatrixProperties:
    """Test properties of generated feature matrices."""
    
    def test_feature_matrix_is_sparse(self):
        """Test that feature matrix is sparse for resumes with few skills."""
        generator = FeatureGenerator()
        
        from src.models import StructuredResume, ResumeSections, SkillSet, ResumeMetadata
        
        # Create resumes with few skills relative to vocabulary
        resumes = []
        all_skills = [f"skill_{i}" for i in range(100)]
        
        for i in range(10):
            # Each resume has only 5 skills out of 100
            resume_skills = [f"skill_{j}" for j in range(i*10, i*10 + 5)]
            
            resume = StructuredResume(
                resume_id=f"test_{i:03d}",
                job_category="ENGINEER",
                sections=ResumeSections("", "", "", "", ""),
                skills=SkillSet([], []),
                normalized_skills=resume_skills,
                scores=None,
                metadata=ResumeMetadata(f"test_{i}.pdf", "2024-01-01", 100)
            )
            resumes.append(resume)
        
        # Generate feature matrix
        feature_matrix, vocabulary = generator.generate_feature_matrix(resumes)
        
        # Calculate sparsity (percentage of zeros)
        total_elements = feature_matrix.size
        zero_elements = np.sum(feature_matrix == 0)
        sparsity = zero_elements / total_elements
        
        # Matrix should be sparse (mostly zeros)
        assert sparsity > 0.5  # At least 50% zeros
    
    def test_feature_matrix_dtype(self):
        """Test that feature matrix uses efficient data type."""
        generator = FeatureGenerator()
        
        from src.models import StructuredResume, ResumeSections, SkillSet, ResumeMetadata
        
        resume = StructuredResume(
            resume_id="test_001",
            job_category="ENGINEER",
            sections=ResumeSections("", "", "", "", ""),
            skills=SkillSet([], []),
            normalized_skills=["python", "java"],
            scores=None,
            metadata=ResumeMetadata("test.pdf", "2024-01-01", 100)
        )
        
        feature_matrix, _ = generator.generate_feature_matrix([resume])
        
        # Should use int8 for memory efficiency
        assert feature_matrix.dtype == np.int8


class TestCSVvsPDFComparison:
    """Test comparison of feature vectors from CSV and PDF sources."""
    
    def test_csv_pdf_feature_vector_comparison_same_skills(self):
        """Test that CSV and PDF sources produce identical vectors for same skills."""
        generator = FeatureGenerator()
        
        from src.models import StructuredResume, ResumeSections, SkillSet, ResumeMetadata
        
        # Create resumes with identical normalized skills but different sources
        csv_resume = StructuredResume(
            resume_id="csv_001",
            job_category="ENGINEER",
            sections=ResumeSections("", "", "", "", ""),
            skills=SkillSet([], []),
            normalized_skills=["python", "java", "sql", "javascript"],
            scores=None,
            metadata=ResumeMetadata("csv:test.csv:row_0", "2024-01-01", 100)
        )
        
        pdf_resume = StructuredResume(
            resume_id="pdf_001",
            job_category="ENGINEER",
            sections=ResumeSections("", "", "", "", ""),
            skills=SkillSet([], []),
            normalized_skills=["python", "java", "sql", "javascript"],
            scores=None,
            metadata=ResumeMetadata("test.pdf", "2024-01-01", 100)
        )
        
        # Build vocabulary and generate vectors
        vocabulary = generator.build_vocabulary([csv_resume, pdf_resume])
        
        csv_vector = generator.generate_feature_vector(
            csv_resume.normalized_skills,
            vocabulary
        )
        
        pdf_vector = generator.generate_feature_vector(
            pdf_resume.normalized_skills,
            vocabulary
        )
        
        # Vectors should be identical
        assert np.array_equal(csv_vector, pdf_vector)
        assert csv_vector.shape == pdf_vector.shape
    
    def test_csv_pdf_feature_vector_comparison_different_skills(self):
        """Test that CSV and PDF sources produce different vectors for different skills."""
        generator = FeatureGenerator()
        
        from src.models import StructuredResume, ResumeSections, SkillSet, ResumeMetadata
        
        csv_resume = StructuredResume(
            resume_id="csv_001",
            job_category="ENGINEER",
            sections=ResumeSections("", "", "", "", ""),
            skills=SkillSet([], []),
            normalized_skills=["python", "java"],
            scores=None,
            metadata=ResumeMetadata("csv:test.csv:row_0", "2024-01-01", 100)
        )
        
        pdf_resume = StructuredResume(
            resume_id="pdf_001",
            job_category="ENGINEER",
            sections=ResumeSections("", "", "", "", ""),
            skills=SkillSet([], []),
            normalized_skills=["javascript", "react"],
            scores=None,
            metadata=ResumeMetadata("test.pdf", "2024-01-01", 100)
        )
        
        # Build vocabulary and generate vectors
        vocabulary = generator.build_vocabulary([csv_resume, pdf_resume])
        
        csv_vector = generator.generate_feature_vector(
            csv_resume.normalized_skills,
            vocabulary
        )
        
        pdf_vector = generator.generate_feature_vector(
            pdf_resume.normalized_skills,
            vocabulary
        )
        
        # Vectors should be different
        assert not np.array_equal(csv_vector, pdf_vector)
        # But same dimensionality
        assert csv_vector.shape == pdf_vector.shape
    
    def test_csv_pdf_feature_vector_comparison_partial_overlap(self):
        """Test CSV and PDF vectors with partial skill overlap."""
        generator = FeatureGenerator()
        
        from src.models import StructuredResume, ResumeSections, SkillSet, ResumeMetadata
        
        csv_resume = StructuredResume(
            resume_id="csv_001",
            job_category="ENGINEER",
            sections=ResumeSections("", "", "", "", ""),
            skills=SkillSet([], []),
            normalized_skills=["python", "java", "sql"],
            scores=None,
            metadata=ResumeMetadata("csv:test.csv:row_0", "2024-01-01", 100)
        )
        
        pdf_resume = StructuredResume(
            resume_id="pdf_001",
            job_category="ENGINEER",
            sections=ResumeSections("", "", "", "", ""),
            skills=SkillSet([], []),
            normalized_skills=["python", "javascript", "react"],
            scores=None,
            metadata=ResumeMetadata("test.pdf", "2024-01-01", 100)
        )
        
        # Build vocabulary and generate vectors
        vocabulary = generator.build_vocabulary([csv_resume, pdf_resume])
        
        csv_vector = generator.generate_feature_vector(
            csv_resume.normalized_skills,
            vocabulary
        )
        
        pdf_vector = generator.generate_feature_vector(
            pdf_resume.normalized_skills,
            vocabulary
        )
        
        # Verify vocabulary contains all skills
        assert len(vocabulary) == 5  # python, java, sql, javascript, react
        
        # Verify both vectors have same dimensionality
        assert csv_vector.shape == pdf_vector.shape == (5,)
        
        # Verify overlap: both should have python=1
        vocab_index = {skill: idx for idx, skill in enumerate(vocabulary)}
        assert csv_vector[vocab_index["python"]] == 1
        assert pdf_vector[vocab_index["python"]] == 1
        
        # Verify differences
        assert csv_vector[vocab_index["java"]] == 1
        assert pdf_vector[vocab_index["java"]] == 0
        
        assert csv_vector[vocab_index["javascript"]] == 0
        assert pdf_vector[vocab_index["javascript"]] == 1
    
    def test_csv_pdf_mixed_batch_feature_matrix(self):
        """Test feature matrix generation from mixed CSV and PDF resumes."""
        generator = FeatureGenerator()
        
        from src.models import StructuredResume, ResumeSections, SkillSet, ResumeMetadata
        
        # Create mixed batch of resumes
        csv_resume1 = StructuredResume(
            resume_id="csv_001",
            job_category="ENGINEER",
            sections=ResumeSections("", "", "", "", ""),
            skills=SkillSet([], []),
            normalized_skills=["python", "java"],
            scores=None,
            metadata=ResumeMetadata("csv:test.csv:row_0", "2024-01-01", 100)
        )
        
        pdf_resume1 = StructuredResume(
            resume_id="pdf_001",
            job_category="ENGINEER",
            sections=ResumeSections("", "", "", "", ""),
            skills=SkillSet([], []),
            normalized_skills=["python", "sql"],
            scores=None,
            metadata=ResumeMetadata("test1.pdf", "2024-01-01", 100)
        )
        
        csv_resume2 = StructuredResume(
            resume_id="csv_002",
            job_category="DATA_SCIENCE",
            sections=ResumeSections("", "", "", "", ""),
            skills=SkillSet([], []),
            normalized_skills=["python", "machine learning"],
            scores=None,
            metadata=ResumeMetadata("csv:test.csv:row_1", "2024-01-01", 100)
        )
        
        pdf_resume2 = StructuredResume(
            resume_id="pdf_002",
            job_category="DATA_SCIENCE",
            sections=ResumeSections("", "", "", "", ""),
            skills=SkillSet([], []),
            normalized_skills=["r", "statistics"],
            scores=None,
            metadata=ResumeMetadata("test2.pdf", "2024-01-01", 100)
        )
        
        # Generate feature matrix from mixed sources
        all_resumes = [csv_resume1, pdf_resume1, csv_resume2, pdf_resume2]
        feature_matrix, vocabulary = generator.generate_feature_matrix(all_resumes)
        
        # Verify matrix properties
        assert feature_matrix.shape[0] == 4  # 4 resumes
        assert feature_matrix.shape[1] == len(vocabulary)
        
        # All rows should have same dimensionality
        for i in range(4):
            assert feature_matrix[i].shape == (len(vocabulary),)
        
        # Verify binary values
        assert np.all((feature_matrix == 0) | (feature_matrix == 1))
    
    def test_csv_pdf_feature_similarity_metric(self):
        """Test computing similarity between CSV and PDF feature vectors."""
        generator = FeatureGenerator()
        
        from src.models import StructuredResume, ResumeSections, SkillSet, ResumeMetadata
        
        # Create resumes with high overlap
        csv_resume = StructuredResume(
            resume_id="csv_001",
            job_category="ENGINEER",
            sections=ResumeSections("", "", "", "", ""),
            skills=SkillSet([], []),
            normalized_skills=["python", "java", "sql", "javascript"],
            scores=None,
            metadata=ResumeMetadata("csv:test.csv:row_0", "2024-01-01", 100)
        )
        
        pdf_resume = StructuredResume(
            resume_id="pdf_001",
            job_category="ENGINEER",
            sections=ResumeSections("", "", "", "", ""),
            skills=SkillSet([], []),
            normalized_skills=["python", "java", "sql"],  # 3 out of 4 overlap
            scores=None,
            metadata=ResumeMetadata("test.pdf", "2024-01-01", 100)
        )
        
        # Build vocabulary and generate vectors
        vocabulary = generator.build_vocabulary([csv_resume, pdf_resume])
        
        csv_vector = generator.generate_feature_vector(
            csv_resume.normalized_skills,
            vocabulary
        )
        
        pdf_vector = generator.generate_feature_vector(
            pdf_resume.normalized_skills,
            vocabulary
        )
        
        # Calculate cosine similarity
        from sklearn.metrics.pairwise import cosine_similarity
        similarity = cosine_similarity([csv_vector], [pdf_vector])[0][0]
        
        # Should have high similarity due to overlap
        assert similarity > 0.8
    
    def test_csv_pdf_vocabulary_union(self):
        """Test that vocabulary is union of skills from both CSV and PDF sources."""
        generator = FeatureGenerator()
        
        from src.models import StructuredResume, ResumeSections, SkillSet, ResumeMetadata
        
        csv_resumes = [
            StructuredResume(
                resume_id="csv_001",
                job_category="ENGINEER",
                sections=ResumeSections("", "", "", "", ""),
                skills=SkillSet([], []),
                normalized_skills=["python", "java"],
                scores=None,
                metadata=ResumeMetadata("csv:test.csv:row_0", "2024-01-01", 100)
            ),
            StructuredResume(
                resume_id="csv_002",
                job_category="ENGINEER",
                sections=ResumeSections("", "", "", "", ""),
                skills=SkillSet([], []),
                normalized_skills=["sql", "mongodb"],
                scores=None,
                metadata=ResumeMetadata("csv:test.csv:row_1", "2024-01-01", 100)
            )
        ]
        
        pdf_resumes = [
            StructuredResume(
                resume_id="pdf_001",
                job_category="ENGINEER",
                sections=ResumeSections("", "", "", "", ""),
                skills=SkillSet([], []),
                normalized_skills=["javascript", "react"],
                scores=None,
                metadata=ResumeMetadata("test1.pdf", "2024-01-01", 100)
            ),
            StructuredResume(
                resume_id="pdf_002",
                job_category="ENGINEER",
                sections=ResumeSections("", "", "", "", ""),
                skills=SkillSet([], []),
                normalized_skills=["python", "django"],  # python overlaps with CSV
                scores=None,
                metadata=ResumeMetadata("test2.pdf", "2024-01-01", 100)
            )
        ]
        
        # Build vocabulary from both sources
        all_resumes = csv_resumes + pdf_resumes
        vocabulary = generator.build_vocabulary(all_resumes)
        
        # Vocabulary should be union of all skills
        expected_skills = {"python", "java", "sql", "mongodb", "javascript", "react", "django"}
        assert set(vocabulary) == expected_skills
        
        # Verify no duplicates
        assert len(vocabulary) == len(set(vocabulary))


class TestErrorHandling:
    """Test error handling in feature generation."""
    
    def test_load_csv_features_missing_file(self):
        """Test error handling for missing CSV file."""
        config = ProcessorConfig(alias_dict_path="config/skill_aliases.json")
        processor = ResumeProcessor(config)
        generator = FeatureGenerator()
        
        with pytest.raises(FileNotFoundError):
            generator.load_csv_features(
                csv_path="nonexistent.csv",
                processor=processor
            )
    
    def test_load_pdf_features_missing_directory(self):
        """Test error handling for missing PDF archive."""
        config = ProcessorConfig(alias_dict_path="config/skill_aliases.json")
        processor = ResumeProcessor(config)
        generator = FeatureGenerator()
        
        with pytest.raises(FileNotFoundError):
            generator.load_pdf_features(
                archive_path="nonexistent_archive",
                processor=processor
            )
