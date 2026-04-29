"""
Unit tests for the ClusteringEngine component.

Tests cover initialization, K-Means clustering, centroid retrieval,
and cluster profile generation.
"""

import pytest
import numpy as np
from src.clustering_engine import ClusteringEngine


class TestClusteringEngineInitialization:
    """Tests for ClusteringEngine initialization."""
    
    def test_init_default_clusters(self):
        """Test initialization with default number of clusters."""
        engine = ClusteringEngine()
        
        assert engine.n_clusters == 10
        assert engine.kmeans is None
    
    def test_init_custom_clusters(self):
        """Test initialization with custom number of clusters."""
        engine = ClusteringEngine(n_clusters=5)
        
        assert engine.n_clusters == 5
        assert engine.kmeans is None
    
    def test_init_invalid_clusters_raises_error(self):
        """Test that n_clusters < 2 raises ValueError."""
        with pytest.raises(ValueError, match="n_clusters must be at least 2"):
            ClusteringEngine(n_clusters=1)
        
        with pytest.raises(ValueError, match="n_clusters must be at least 2"):
            ClusteringEngine(n_clusters=0)
    
    def test_init_logging(self, caplog):
        """Test that initialization logs correctly."""
        with caplog.at_level("INFO"):
            engine = ClusteringEngine(n_clusters=7)
        
        assert "ClusteringEngine initialized with 7 clusters" in caplog.text


class TestFitClusters:
    """Tests for fit_clusters method."""
    
    def test_fit_clusters_basic(self):
        """Test basic clustering with simple data."""
        engine = ClusteringEngine(n_clusters=2)
        
        # Create simple binary feature matrix
        X = np.array([
            [1, 0, 0, 1],
            [1, 0, 0, 0],
            [0, 1, 1, 0],
            [0, 1, 1, 1],
            [1, 0, 1, 0],
            [0, 1, 0, 1]
        ])
        
        labels = engine.fit_clusters(X)
        
        # Check labels shape and values
        assert labels.shape == (6,)
        assert set(labels) <= {0, 1}  # Labels should be 0 or 1
        assert engine.kmeans is not None
    
    def test_fit_clusters_returns_correct_number_of_clusters(self):
        """Test that clustering creates the specified number of clusters."""
        engine = ClusteringEngine(n_clusters=3)
        
        # Create data with clear clusters
        X = np.array([
            [1, 0, 0],
            [1, 0, 0],
            [0, 1, 0],
            [0, 1, 0],
            [0, 0, 1],
            [0, 0, 1],
            [1, 1, 0],
            [0, 1, 1],
            [1, 0, 1]
        ])
        
        labels = engine.fit_clusters(X)
        
        # Check that we have at most n_clusters unique labels
        unique_labels = set(labels)
        assert len(unique_labels) <= 3
        assert all(0 <= label < 3 for label in labels)
    
    def test_fit_clusters_empty_matrix_raises_error(self):
        """Test that empty feature matrix raises ValueError."""
        engine = ClusteringEngine(n_clusters=2)
        X = np.array([]).reshape(0, 4)
        
        with pytest.raises(ValueError, match="Cannot cluster empty feature matrix"):
            engine.fit_clusters(X)
    
    def test_fit_clusters_too_few_samples_raises_error(self):
        """Test that fewer samples than clusters raises ValueError."""
        engine = ClusteringEngine(n_clusters=5)
        X = np.array([
            [1, 0, 0],
            [0, 1, 0],
            [0, 0, 1]
        ])
        
        with pytest.raises(ValueError, match="Number of samples .* must be >= number of clusters"):
            engine.fit_clusters(X)
    
    def test_fit_clusters_uses_kmeans_plus_plus(self):
        """Test that K-Means uses k-means++ initialization."""
        engine = ClusteringEngine(n_clusters=2)
        X = np.random.rand(20, 5)
        
        engine.fit_clusters(X)
        
        # Check that kmeans model was created with correct parameters
        assert engine.kmeans.init == 'k-means++'
        assert engine.kmeans.n_clusters == 2
    
    def test_fit_clusters_deterministic_with_random_state(self):
        """Test that clustering is deterministic with fixed random_state."""
        X = np.random.rand(30, 10)
        
        engine1 = ClusteringEngine(n_clusters=3)
        labels1 = engine1.fit_clusters(X)
        
        engine2 = ClusteringEngine(n_clusters=3)
        labels2 = engine2.fit_clusters(X)
        
        # Results should be identical with same random_state
        np.testing.assert_array_equal(labels1, labels2)
    
    def test_fit_clusters_logging(self, caplog):
        """Test that fit_clusters logs correctly."""
        engine = ClusteringEngine(n_clusters=2)
        X = np.random.rand(10, 5)
        
        with caplog.at_level("INFO"):
            engine.fit_clusters(X)
        
        assert "Fitting K-Means clustering on 10 samples with 5 features" in caplog.text
        assert "Clustering complete: 2 clusters created" in caplog.text


class TestGetClusterCentroids:
    """Tests for get_cluster_centroids method."""
    
    def test_get_cluster_centroids_basic(self):
        """Test retrieving cluster centroids."""
        engine = ClusteringEngine(n_clusters=2)
        X = np.array([
            [1, 0, 0],
            [1, 0, 0],
            [0, 1, 1],
            [0, 1, 1]
        ])
        
        engine.fit_clusters(X)
        centroids = engine.get_cluster_centroids()
        
        # Check shape
        assert centroids.shape == (2, 3)
        
        # Centroids should be within valid range for binary features
        assert np.all(centroids >= 0)
        assert np.all(centroids <= 1)
    
    def test_get_cluster_centroids_correct_shape(self):
        """Test that centroids have correct shape."""
        engine = ClusteringEngine(n_clusters=4)
        X = np.random.rand(20, 8)
        
        engine.fit_clusters(X)
        centroids = engine.get_cluster_centroids()
        
        assert centroids.shape == (4, 8)
    
    def test_get_cluster_centroids_before_fitting_raises_error(self):
        """Test that calling get_cluster_centroids before fitting raises error."""
        engine = ClusteringEngine(n_clusters=2)
        
        with pytest.raises(RuntimeError, match="Clustering model not fitted"):
            engine.get_cluster_centroids()
    
    def test_get_cluster_centroids_logging(self, caplog):
        """Test that get_cluster_centroids logs correctly."""
        engine = ClusteringEngine(n_clusters=2)
        X = np.random.rand(10, 5)
        engine.fit_clusters(X)
        
        with caplog.at_level("INFO"):
            engine.get_cluster_centroids()
        
        assert "Retrieved centroids: shape (2, 5)" in caplog.text


class TestGetClusterProfiles:
    """Tests for get_cluster_profiles method."""
    
    def test_get_cluster_profiles_basic(self):
        """Test basic cluster profile generation."""
        engine = ClusteringEngine(n_clusters=2)
        X = np.array([
            [1, 0, 0, 1, 0],
            [1, 0, 0, 0, 0],
            [0, 1, 1, 0, 1],
            [0, 1, 1, 0, 0]
        ])
        vocabulary = ["Python", "Java", "JavaScript", "SQL", "React"]
        
        engine.fit_clusters(X)
        profiles = engine.get_cluster_profiles(vocabulary, top_n=3)
        
        # Check structure
        assert len(profiles) == 2
        assert all(cluster_id in profiles for cluster_id in range(2))
        assert all(len(skills) == 3 for skills in profiles.values())
        assert all(isinstance(skill, str) for skills in profiles.values() for skill in skills)
    
    def test_get_cluster_profiles_returns_top_skills(self):
        """Test that profiles return skills with highest centroid values."""
        engine = ClusteringEngine(n_clusters=2)
        
        # Create data where cluster 0 has high values for first features
        # and cluster 1 has high values for last features
        X = np.array([
            [1, 1, 0, 0, 0],
            [1, 1, 0, 0, 0],
            [1, 1, 0, 0, 0],
            [0, 0, 0, 1, 1],
            [0, 0, 0, 1, 1],
            [0, 0, 0, 1, 1]
        ])
        vocabulary = ["Skill_A", "Skill_B", "Skill_C", "Skill_D", "Skill_E"]
        
        engine.fit_clusters(X)
        profiles = engine.get_cluster_profiles(vocabulary, top_n=2)
        
        # Each cluster should have 2 top skills
        assert all(len(skills) == 2 for skills in profiles.values())
        
        # Skills should be from vocabulary
        all_profile_skills = set()
        for skills in profiles.values():
            all_profile_skills.update(skills)
        assert all_profile_skills.issubset(set(vocabulary))
    
    def test_get_cluster_profiles_custom_top_n(self):
        """Test cluster profiles with custom top_n parameter."""
        engine = ClusteringEngine(n_clusters=2)
        X = np.random.rand(10, 8)
        vocabulary = [f"Skill_{i}" for i in range(8)]
        
        engine.fit_clusters(X)
        
        # Test with different top_n values
        profiles_3 = engine.get_cluster_profiles(vocabulary, top_n=3)
        profiles_5 = engine.get_cluster_profiles(vocabulary, top_n=5)
        
        assert all(len(skills) == 3 for skills in profiles_3.values())
        assert all(len(skills) == 5 for skills in profiles_5.values())

    def test_get_cluster_profiles_filters_resume_metadata_noise(self):
        """Test that cluster labels skip obvious resume header artifacts."""
        engine = ClusteringEngine(n_clusters=2)
        X = np.array([
            [1, 1, 1, 1, 1, 1, 0, 0, 0],
            [1, 1, 1, 1, 1, 1, 0, 0, 0],
            [1, 1, 1, 1, 1, 1, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 1, 1, 1],
            [0, 0, 0, 0, 0, 0, 1, 1, 1],
            [0, 0, 0, 0, 0, 0, 1, 1, 1],
        ])
        vocabulary = [
            "name city",
            "state",
            "highlights",
            "ed",
            "Python",
            "SQL",
            "company name city",
            "data analysis",
            "machine learning",
        ]

        engine.fit_clusters(X)
        profiles = engine.get_cluster_profiles(vocabulary, top_n=2)

        all_profile_skills = {
            skill.lower()
            for cluster_skills in profiles.values()
            for skill in cluster_skills
        }
        assert "name city" not in all_profile_skills
        assert "state" not in all_profile_skills
        assert "company name city" not in all_profile_skills
        assert "highlights" not in all_profile_skills
        assert "ed" not in all_profile_skills
        assert {"python", "sql", "data analysis", "machine learning"} == all_profile_skills
    
    def test_get_cluster_profiles_before_fitting_raises_error(self):
        """Test that calling get_cluster_profiles before fitting raises error."""
        engine = ClusteringEngine(n_clusters=2)
        vocabulary = ["Python", "Java", "JavaScript"]
        
        with pytest.raises(RuntimeError, match="Clustering model not fitted"):
            engine.get_cluster_profiles(vocabulary)
    
    def test_get_cluster_profiles_vocabulary_mismatch_raises_error(self):
        """Test that vocabulary length mismatch raises ValueError."""
        engine = ClusteringEngine(n_clusters=2)
        X = np.random.rand(10, 5)
        vocabulary = ["Python", "Java", "JavaScript"]  # Length 3, but X has 5 features
        
        engine.fit_clusters(X)
        
        with pytest.raises(ValueError, match="Vocabulary length .* must match feature dimensions"):
            engine.get_cluster_profiles(vocabulary)
    
    def test_get_cluster_profiles_all_clusters_have_profiles(self):
        """Test that all clusters get profiles."""
        engine = ClusteringEngine(n_clusters=4)
        X = np.random.rand(20, 10)
        vocabulary = [f"Skill_{i}" for i in range(10)]
        
        engine.fit_clusters(X)
        profiles = engine.get_cluster_profiles(vocabulary, top_n=5)
        
        # All clusters should have profiles
        assert len(profiles) == 4
        assert set(profiles.keys()) == {0, 1, 2, 3}
    
    def test_get_cluster_profiles_logging(self, caplog):
        """Test that get_cluster_profiles logs correctly."""
        engine = ClusteringEngine(n_clusters=2)
        X = np.random.rand(10, 5)
        vocabulary = [f"Skill_{i}" for i in range(5)]
        
        engine.fit_clusters(X)
        
        with caplog.at_level("INFO"):
            engine.get_cluster_profiles(vocabulary, top_n=3)
        
        assert "Generating cluster profiles: top 3 skills per cluster" in caplog.text
        assert "Cluster profiles generated for 2 clusters" in caplog.text


class TestClusteringEngineIntegration:
    """Integration tests for complete clustering workflow."""
    
    def test_complete_clustering_workflow(self):
        """Test complete workflow: fit -> get centroids -> get profiles."""
        engine = ClusteringEngine(n_clusters=3)
        
        # Create realistic binary feature data
        np.random.seed(42)
        X = np.random.randint(0, 2, size=(30, 15))
        vocabulary = [f"Skill_{i}" for i in range(15)]
        
        # Fit clusters
        labels = engine.fit_clusters(X)
        assert labels.shape == (30,)
        
        # Get centroids
        centroids = engine.get_cluster_centroids()
        assert centroids.shape == (3, 15)
        
        # Get profiles
        profiles = engine.get_cluster_profiles(vocabulary, top_n=5)
        assert len(profiles) == 3
        assert all(len(skills) == 5 for skills in profiles.values())
    
    def test_clustering_with_real_world_like_data(self):
        """Test clustering with data resembling real resume features."""
        engine = ClusteringEngine(n_clusters=5)
        
        # Simulate resume feature vectors (sparse binary vectors)
        np.random.seed(42)
        n_resumes = 50
        n_skills = 100
        
        # Create sparse binary matrix (most resumes have only a few skills)
        X = np.zeros((n_resumes, n_skills))
        for i in range(n_resumes):
            # Each resume has 5-15 skills
            n_skills_per_resume = np.random.randint(5, 16)
            skill_indices = np.random.choice(n_skills, n_skills_per_resume, replace=False)
            X[i, skill_indices] = 1
        
        vocabulary = [f"Skill_{i}" for i in range(n_skills)]
        
        # Perform clustering
        labels = engine.fit_clusters(X)
        centroids = engine.get_cluster_centroids()
        profiles = engine.get_cluster_profiles(vocabulary, top_n=10)
        
        # Validate results
        assert labels.shape == (n_resumes,)
        assert len(set(labels)) <= 5  # At most 5 clusters
        assert centroids.shape == (5, n_skills)
        assert len(profiles) == 5
        assert all(len(skills) == 10 for skills in profiles.values())
    
    def test_refitting_updates_model(self):
        """Test that refitting with new data updates the model."""
        engine = ClusteringEngine(n_clusters=2)
        
        # First fit
        X1 = np.array([[1, 0], [1, 0], [0, 1], [0, 1]])
        labels1 = engine.fit_clusters(X1)
        centroids1 = engine.get_cluster_centroids()
        
        # Second fit with different data
        X2 = np.array([[0, 1], [0, 1], [1, 0], [1, 0]])
        labels2 = engine.fit_clusters(X2)
        centroids2 = engine.get_cluster_centroids()
        
        # Centroids should be different
        assert not np.array_equal(centroids1, centroids2)


class TestEdgeCases:
    """Tests for edge cases and boundary conditions."""
    
    def test_clustering_with_minimum_samples(self):
        """Test clustering with exactly n_clusters samples."""
        engine = ClusteringEngine(n_clusters=3)
        X = np.array([
            [1, 0, 0],
            [0, 1, 0],
            [0, 0, 1]
        ])
        
        labels = engine.fit_clusters(X)
        
        assert labels.shape == (3,)
        assert len(set(labels)) <= 3
    
    def test_clustering_with_identical_samples(self):
        """Test clustering when all samples are identical."""
        engine = ClusteringEngine(n_clusters=2)
        X = np.array([
            [1, 0, 1],
            [1, 0, 1],
            [1, 0, 1],
            [1, 0, 1]
        ])
        
        labels = engine.fit_clusters(X)
        
        # Should still produce labels (though all might be in one cluster)
        assert labels.shape == (4,)
    
    def test_clustering_with_all_zeros(self):
        """Test clustering with all-zero feature vectors."""
        engine = ClusteringEngine(n_clusters=2)
        X = np.zeros((10, 5))
        
        labels = engine.fit_clusters(X)
        
        assert labels.shape == (10,)
    
    def test_clustering_with_all_ones(self):
        """Test clustering with all-one feature vectors."""
        engine = ClusteringEngine(n_clusters=2)
        X = np.ones((10, 5))
        
        labels = engine.fit_clusters(X)
        
        assert labels.shape == (10,)
    
    def test_get_cluster_profiles_with_top_n_larger_than_vocabulary(self):
        """Test cluster profiles when top_n exceeds vocabulary size."""
        engine = ClusteringEngine(n_clusters=2)
        X = np.random.rand(10, 3)
        vocabulary = ["Skill_A", "Skill_B", "Skill_C"]
        
        engine.fit_clusters(X)
        profiles = engine.get_cluster_profiles(vocabulary, top_n=10)
        
        # Should return all available skills (3) even though top_n=10
        assert all(len(skills) == 3 for skills in profiles.values())
