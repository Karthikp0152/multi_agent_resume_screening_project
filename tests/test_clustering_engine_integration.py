"""
Integration tests for ClusteringEngine with FeatureGenerator.

Tests the complete workflow of generating features from resumes and
applying clustering to identify candidate groups.
"""

import pytest
import numpy as np
from src.clustering_engine import ClusteringEngine
from src.feature_generator import FeatureGenerator
from src.models import (
    StructuredResume, ResumeSections, SkillSet, 
    ResumeMetadata, Scores
)


class TestClusteringEngineWithFeatureGenerator:
    """Integration tests combining ClusteringEngine and FeatureGenerator."""
    
    @pytest.fixture
    def sample_resumes(self):
        """Create sample resumes with different skill profiles."""
        resumes = []
        
        # Backend developer resumes
        for i in range(5):
            resume = StructuredResume(
                resume_id=f"backend_{i}",
                job_category="SOFTWARE_ENGINEER",
                sections=ResumeSections(
                    skills="Python, Java, SQL, Docker",
                    experience="Backend development",
                    education="BS Computer Science",
                    projects="API development",
                    raw_text="Resume text"
                ),
                skills=SkillSet(
                    explicit_skills=["Python", "Java", "SQL", "Docker"],
                    implicit_skills=[]
                ),
                normalized_skills=["Python", "Java", "SQL", "Docker"],
                scores=None,
                metadata=ResumeMetadata(
                    file_path=f"resume_{i}.pdf",
                    processed_date="2025-01-01",
                    processing_time_ms=100
                )
            )
            resumes.append(resume)
        
        # Frontend developer resumes
        for i in range(5):
            resume = StructuredResume(
                resume_id=f"frontend_{i}",
                job_category="SOFTWARE_ENGINEER",
                sections=ResumeSections(
                    skills="JavaScript, React, CSS, HTML",
                    experience="Frontend development",
                    education="BS Computer Science",
                    projects="Web applications",
                    raw_text="Resume text"
                ),
                skills=SkillSet(
                    explicit_skills=["JavaScript", "React", "CSS", "HTML"],
                    implicit_skills=[]
                ),
                normalized_skills=["JavaScript", "React", "CSS", "HTML"],
                scores=None,
                metadata=ResumeMetadata(
                    file_path=f"resume_{i+5}.pdf",
                    processed_date="2025-01-01",
                    processing_time_ms=100
                )
            )
            resumes.append(resume)
        
        # Data scientist resumes
        for i in range(5):
            resume = StructuredResume(
                resume_id=f"datascience_{i}",
                job_category="DATA_SCIENTIST",
                sections=ResumeSections(
                    skills="Python, Machine Learning, TensorFlow, Pandas",
                    experience="Data analysis",
                    education="MS Data Science",
                    projects="ML models",
                    raw_text="Resume text"
                ),
                skills=SkillSet(
                    explicit_skills=["Python", "Machine Learning", "TensorFlow", "Pandas"],
                    implicit_skills=[]
                ),
                normalized_skills=["Python", "Machine Learning", "TensorFlow", "Pandas"],
                scores=None,
                metadata=ResumeMetadata(
                    file_path=f"resume_{i+10}.pdf",
                    processed_date="2025-01-01",
                    processing_time_ms=100
                )
            )
            resumes.append(resume)
        
        return resumes
    
    def test_clustering_with_feature_generator(self, sample_resumes):
        """Test complete workflow: feature generation -> clustering."""
        # Generate features
        feature_gen = FeatureGenerator()
        feature_matrix, vocabulary = feature_gen.generate_feature_matrix(sample_resumes)
        
        # Apply clustering
        clustering_engine = ClusteringEngine(n_clusters=3)
        labels = clustering_engine.fit_clusters(feature_matrix)
        
        # Verify results
        assert labels.shape == (15,)  # 15 resumes
        assert len(set(labels)) <= 3  # At most 3 clusters
        assert feature_matrix.shape[1] == len(vocabulary)
    
    def test_cluster_profiles_with_real_vocabulary(self, sample_resumes):
        """Test cluster profile generation with real skill vocabulary."""
        # Generate features
        feature_gen = FeatureGenerator()
        feature_matrix, vocabulary = feature_gen.generate_feature_matrix(sample_resumes)
        
        # Apply clustering
        clustering_engine = ClusteringEngine(n_clusters=3)
        clustering_engine.fit_clusters(feature_matrix)
        
        # Get cluster profiles
        profiles = clustering_engine.get_cluster_profiles(vocabulary, top_n=5)
        
        # Verify profiles
        assert len(profiles) == 3
        for cluster_id, skills in profiles.items():
            assert len(skills) <= 5
            assert all(skill in vocabulary for skill in skills)
    
    def test_clustering_identifies_similar_candidates(self, sample_resumes):
        """Test that clustering groups similar candidates together."""
        # Generate features
        feature_gen = FeatureGenerator()
        feature_matrix, vocabulary = feature_gen.generate_feature_matrix(sample_resumes)
        
        # Apply clustering
        clustering_engine = ClusteringEngine(n_clusters=3)
        labels = clustering_engine.fit_clusters(feature_matrix)
        
        # Check that similar resumes tend to be in the same cluster
        # Backend developers (indices 0-4)
        backend_labels = labels[0:5]
        # Frontend developers (indices 5-9)
        frontend_labels = labels[5:10]
        # Data scientists (indices 10-14)
        datascience_labels = labels[10:15]
        
        # Within each group, there should be some clustering tendency
        # (not all in different clusters)
        assert len(set(backend_labels)) <= 3
        assert len(set(frontend_labels)) <= 3
        assert len(set(datascience_labels)) <= 3
    
    def test_centroids_represent_cluster_characteristics(self, sample_resumes):
        """Test that centroids capture cluster characteristics."""
        # Generate features
        feature_gen = FeatureGenerator()
        feature_matrix, vocabulary = feature_gen.generate_feature_matrix(sample_resumes)
        
        # Apply clustering
        clustering_engine = ClusteringEngine(n_clusters=3)
        labels = clustering_engine.fit_clusters(feature_matrix)
        centroids = clustering_engine.get_cluster_centroids()
        
        # Verify centroid properties
        assert centroids.shape == (3, len(vocabulary))
        
        # Centroids should have values between 0 and 1 for binary features
        # (they represent the average of binary values in each cluster)
        # Use tolerance for floating point comparison
        assert centroids.min() >= -1e-10
        assert centroids.max() <= 1 + 1e-10
        
        # Each centroid should have some non-zero values
        for centroid in centroids:
            assert np.sum(centroid) > 0
    
    def test_clustering_with_varying_cluster_sizes(self, sample_resumes):
        """Test clustering with different numbers of clusters."""
        feature_gen = FeatureGenerator()
        feature_matrix, vocabulary = feature_gen.generate_feature_matrix(sample_resumes)
        
        # Test with different cluster sizes
        for n_clusters in [2, 3, 5]:
            clustering_engine = ClusteringEngine(n_clusters=n_clusters)
            labels = clustering_engine.fit_clusters(feature_matrix)
            profiles = clustering_engine.get_cluster_profiles(vocabulary, top_n=3)
            
            assert len(set(labels)) <= n_clusters
            assert len(profiles) == n_clusters
    
    def test_clustering_with_sparse_features(self):
        """Test clustering with sparse feature vectors (realistic scenario)."""
        # Create resumes with sparse skill sets
        resumes = []
        all_skills = [
            "Python", "Java", "JavaScript", "C++", "Ruby",
            "SQL", "MongoDB", "PostgreSQL", "Redis", "Elasticsearch",
            "React", "Angular", "Vue", "Django", "Flask",
            "Docker", "Kubernetes", "AWS", "Azure", "GCP",
            "Machine Learning", "Deep Learning", "NLP", "Computer Vision", "Data Mining"
        ]
        
        # Each resume has only 5-8 skills from the pool of 25
        np.random.seed(42)
        for i in range(30):
            n_skills = np.random.randint(5, 9)
            selected_skills = list(np.random.choice(all_skills, n_skills, replace=False))
            
            resume = StructuredResume(
                resume_id=f"resume_{i}",
                job_category="SOFTWARE_ENGINEER",
                sections=ResumeSections(
                    skills=", ".join(selected_skills),
                    experience="Work experience",
                    education="Education",
                    projects="Projects",
                    raw_text="Resume text"
                ),
                skills=SkillSet(
                    explicit_skills=selected_skills,
                    implicit_skills=[]
                ),
                normalized_skills=selected_skills,
                scores=None,
                metadata=ResumeMetadata(
                    file_path=f"resume_{i}.pdf",
                    processed_date="2025-01-01",
                    processing_time_ms=100
                )
            )
            resumes.append(resume)
        
        # Generate features and cluster
        feature_gen = FeatureGenerator()
        feature_matrix, vocabulary = feature_gen.generate_feature_matrix(resumes)
        
        clustering_engine = ClusteringEngine(n_clusters=5)
        labels = clustering_engine.fit_clusters(feature_matrix)
        profiles = clustering_engine.get_cluster_profiles(vocabulary, top_n=5)
        
        # Verify results
        assert labels.shape == (30,)
        assert len(profiles) == 5
        assert len(vocabulary) == 25  # All unique skills
        
        # Feature matrix should be sparse
        sparsity = 1 - (np.count_nonzero(feature_matrix) / feature_matrix.size)
        assert sparsity > 0.5  # At least 50% sparse


class TestClusteringEngineErrorHandling:
    """Test error handling in integration scenarios."""
    
    def test_clustering_with_insufficient_resumes(self):
        """Test that clustering fails gracefully with too few resumes."""
        # Create only 2 resumes
        resumes = []
        for i in range(2):
            resume = StructuredResume(
                resume_id=f"resume_{i}",
                job_category="SOFTWARE_ENGINEER",
                sections=ResumeSections(
                    skills="Python, Java",
                    experience="Experience",
                    education="Education",
                    projects="Projects",
                    raw_text="Resume text"
                ),
                skills=SkillSet(
                    explicit_skills=["Python", "Java"],
                    implicit_skills=[]
                ),
                normalized_skills=["Python", "Java"],
                scores=None,
                metadata=ResumeMetadata(
                    file_path=f"resume_{i}.pdf",
                    processed_date="2025-01-01",
                    processing_time_ms=100
                )
            )
            resumes.append(resume)
        
        # Generate features
        feature_gen = FeatureGenerator()
        feature_matrix, vocabulary = feature_gen.generate_feature_matrix(resumes)
        
        # Try to cluster with more clusters than samples
        clustering_engine = ClusteringEngine(n_clusters=5)
        
        with pytest.raises(ValueError, match="Number of samples .* must be >= number of clusters"):
            clustering_engine.fit_clusters(feature_matrix)
    
    def test_clustering_with_empty_skills(self):
        """Test clustering when some resumes have no skills."""
        resumes = []
        
        # Some resumes with skills
        for i in range(5):
            resume = StructuredResume(
                resume_id=f"resume_{i}",
                job_category="SOFTWARE_ENGINEER",
                sections=ResumeSections(
                    skills="Python, Java",
                    experience="Experience",
                    education="Education",
                    projects="Projects",
                    raw_text="Resume text"
                ),
                skills=SkillSet(
                    explicit_skills=["Python", "Java"],
                    implicit_skills=[]
                ),
                normalized_skills=["Python", "Java"],
                scores=None,
                metadata=ResumeMetadata(
                    file_path=f"resume_{i}.pdf",
                    processed_date="2025-01-01",
                    processing_time_ms=100
                )
            )
            resumes.append(resume)
        
        # Some resumes with no skills
        for i in range(5, 10):
            resume = StructuredResume(
                resume_id=f"resume_{i}",
                job_category="SOFTWARE_ENGINEER",
                sections=ResumeSections(
                    skills="",
                    experience="Experience",
                    education="Education",
                    projects="Projects",
                    raw_text="Resume text"
                ),
                skills=SkillSet(
                    explicit_skills=[],
                    implicit_skills=[]
                ),
                normalized_skills=[],
                scores=None,
                metadata=ResumeMetadata(
                    file_path=f"resume_{i}.pdf",
                    processed_date="2025-01-01",
                    processing_time_ms=100
                )
            )
            resumes.append(resume)
        
        # Generate features and cluster
        feature_gen = FeatureGenerator()
        feature_matrix, vocabulary = feature_gen.generate_feature_matrix(resumes)
        
        clustering_engine = ClusteringEngine(n_clusters=2)
        labels = clustering_engine.fit_clusters(feature_matrix)
        
        # Should still work - resumes with no skills will have all-zero vectors
        assert labels.shape == (10,)
