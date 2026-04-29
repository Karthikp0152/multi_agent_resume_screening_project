"""
Clustering Engine component for the Smart Resume Screening System.

This module provides the ClusteringEngine class that groups similar candidates
using K-Means clustering based on their skill feature vectors.
"""

import logging
import re
import numpy as np
from typing import List, Dict
from sklearn.cluster import KMeans

logger = logging.getLogger(__name__)

PROFILE_NOISE_TERMS = {
    "name",
    "city",
    "state",
    "name city",
    "city state",
    "company name city",
    "email",
    "phone",
    "address",
    "linkedin",
    "resume",
    "www",
    "http",
    "accomplishment",
    "accomplishments",
    "core",
    "ed",
    "education",
    "experience",
    "highlight",
    "highlights",
    "objective",
    "profile",
    "summary",
}

PROFILE_NOISE_FRAGMENTS = {
    "name city",
    "company name city",
}

URL_PATTERN = re.compile(r"^(https?://|www\.)|\.com\b|\.org\b|\.net\b", re.IGNORECASE)
EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
PHONE_PATTERN = re.compile(r"^\+?[\d\s().-]{7,}$")


class ClusteringEngine:
    """Groups similar candidates using K-Means clustering.
    
    This class applies K-Means clustering to resume feature vectors to identify
    groups of candidates with similar skill profiles. It uses k-means++
    initialization for better convergence and provides methods to analyze
    cluster characteristics.
    
    Attributes:
        n_clusters: Number of clusters to create
        kmeans: Fitted KMeans model (None until fit_clusters is called)
    """
    
    def __init__(self, n_clusters: int = 10):
        """Initialize with number of clusters.
        
        Args:
            n_clusters: Number of clusters to create (default: 10)
            
        Raises:
            ValueError: If n_clusters is less than 2
        """
        if n_clusters < 2:
            raise ValueError("n_clusters must be at least 2")
        
        self.n_clusters = n_clusters
        self.kmeans = None
        logger.info(f"ClusteringEngine initialized with {n_clusters} clusters")
    
    def fit_clusters(self, X: np.ndarray) -> np.ndarray:
        """Apply K-Means clustering and return cluster labels.
        
        This method fits a K-Means model to the provided feature vectors using
        k-means++ initialization for better convergence. The Euclidean distance
        metric is used on the binary feature vectors.
        
        Args:
            X: Feature matrix of shape (n_samples, n_features)
            
        Returns:
            Array of cluster labels of shape (n_samples,)
            
        Raises:
            ValueError: If X is empty or has fewer samples than clusters
        """
        if X.shape[0] == 0:
            raise ValueError("Cannot cluster empty feature matrix")
        
        if X.shape[0] < self.n_clusters:
            raise ValueError(
                f"Number of samples ({X.shape[0]}) must be >= "
                f"number of clusters ({self.n_clusters})"
            )
        
        logger.info(
            f"Fitting K-Means clustering on {X.shape[0]} samples "
            f"with {X.shape[1]} features"
        )
        
        # Initialize and fit K-Means with k-means++ initialization
        self.kmeans = KMeans(
            n_clusters=self.n_clusters,
            init='k-means++',
            random_state=42,
            n_init=10
        )
        
        # Fit and get cluster labels
        labels = self.kmeans.fit_predict(X)
        
        logger.info(f"Clustering complete: {self.n_clusters} clusters created")
        
        return labels
    
    def get_cluster_centroids(self) -> np.ndarray:
        """Return cluster centroids.
        
        Returns the centroids (center points) of each cluster, which represent
        the typical skill profile for that cluster.
        
        Returns:
            Array of cluster centroids of shape (n_clusters, n_features)
            
        Raises:
            RuntimeError: If fit_clusters has not been called yet
        """
        if self.kmeans is None:
            raise RuntimeError(
                "Clustering model not fitted. Call fit_clusters() first."
            )
        
        centroids = self.kmeans.cluster_centers_
        
        logger.info(
            f"Retrieved centroids: shape {centroids.shape} "
            f"({centroids.shape[0]} clusters x {centroids.shape[1]} features)"
        )
        
        return centroids
    
    def get_cluster_profiles(
        self,
        vocabulary: List[str],
        top_n: int = 10
    ) -> Dict[int, List[str]]:
        """Get top skills for each cluster.
        
        Identifies the most characteristic skills for each cluster by finding
        the skills with the highest centroid values. This helps understand what
        defines each cluster.
        
        Args:
            vocabulary: List of skill names corresponding to feature indices
            top_n: Number of top skills to return per cluster (default: 10)
            
        Returns:
            Dictionary mapping cluster ID to list of top skill names
            
        Raises:
            RuntimeError: If fit_clusters has not been called yet
            ValueError: If vocabulary length doesn't match feature dimensions
        """
        if self.kmeans is None:
            raise RuntimeError(
                "Clustering model not fitted. Call fit_clusters() first."
            )
        
        centroids = self.kmeans.cluster_centers_
        
        if len(vocabulary) != centroids.shape[1]:
            raise ValueError(
                f"Vocabulary length ({len(vocabulary)}) must match "
                f"feature dimensions ({centroids.shape[1]})"
            )
        
        logger.info(
            f"Generating cluster profiles: top {top_n} skills per cluster"
        )
        
        cluster_profiles = {}
        
        for cluster_id in range(self.n_clusters):
            # Get centroid values for this cluster
            centroid = centroids[cluster_id]
            
            # Scan all features by centroid weight so noisy resume metadata can
            # be skipped while still filling the requested number of labels.
            sorted_indices = np.argsort(centroid)[::-1]

            top_skills = []
            seen = set()
            for idx in sorted_indices:
                skill = vocabulary[idx]
                if self._is_profile_noise(skill):
                    continue

                display_skill = self._format_profile_skill(skill)
                dedupe_key = display_skill.lower()
                if dedupe_key in seen:
                    continue

                top_skills.append(display_skill)
                seen.add(dedupe_key)

                if len(top_skills) >= top_n:
                    break
            
            cluster_profiles[cluster_id] = top_skills
            
            logger.debug(
                f"Cluster {cluster_id} top skills: {', '.join(top_skills[:3])}..."
            )
        
        logger.info(f"Cluster profiles generated for {self.n_clusters} clusters")
        
        return cluster_profiles

    def _format_profile_skill(self, skill: str) -> str:
        """Collapse whitespace for readable cluster labels."""
        return " ".join(skill.strip().split())

    def _is_profile_noise(self, skill: str) -> bool:
        """Return True for resume metadata artifacts in cluster labels."""
        normalized = skill.strip().lower()
        collapsed = " ".join(normalized.split())

        if not collapsed:
            return True

        if "\n" in skill or "\r" in skill:
            return True

        if collapsed in PROFILE_NOISE_TERMS:
            return True

        if any(fragment in collapsed for fragment in PROFILE_NOISE_FRAGMENTS):
            return True

        if URL_PATTERN.search(collapsed):
            return True

        if EMAIL_PATTERN.match(collapsed):
            return True

        if PHONE_PATTERN.match(collapsed):
            return True

        return False
