"""
Demo script for ClusteringEngine component.

This script demonstrates how to use the ClusteringEngine to group similar
candidates based on their skill profiles.
"""

import numpy as np
from src.clustering_engine import ClusteringEngine
from src.feature_generator import FeatureGenerator
from src.models import (
    StructuredResume, ResumeSections, SkillSet, 
    ResumeMetadata
)


def create_sample_resumes():
    """Create sample resumes with different skill profiles."""
    resumes = []
    
    # Backend developers
    backend_skills = [
        ["Python", "Django", "PostgreSQL", "Docker", "REST API"],
        ["Java", "Spring Boot", "MySQL", "Kubernetes", "Microservices"],
        ["Python", "Flask", "MongoDB", "Redis", "GraphQL"],
        ["Node.js", "Express", "PostgreSQL", "Docker", "REST API"],
        ["Java", "Spring", "Oracle", "Jenkins", "REST API"]
    ]
    
    # Frontend developers
    frontend_skills = [
        ["JavaScript", "React", "Redux", "CSS", "HTML"],
        ["TypeScript", "Angular", "RxJS", "SASS", "HTML"],
        ["JavaScript", "Vue.js", "Vuex", "CSS", "Webpack"],
        ["React", "Next.js", "Tailwind CSS", "JavaScript", "HTML"],
        ["Angular", "TypeScript", "Material UI", "CSS", "HTML"]
    ]
    
    # Data scientists
    datascience_skills = [
        ["Python", "Machine Learning", "TensorFlow", "Pandas", "NumPy"],
        ["Python", "Deep Learning", "PyTorch", "Scikit-learn", "Jupyter"],
        ["R", "Machine Learning", "Statistics", "Data Visualization", "SQL"],
        ["Python", "NLP", "BERT", "spaCy", "TensorFlow"],
        ["Python", "Computer Vision", "OpenCV", "Keras", "NumPy"]
    ]
    
    # DevOps engineers
    devops_skills = [
        ["Docker", "Kubernetes", "AWS", "Terraform", "Jenkins"],
        ["Docker", "Azure", "Ansible", "GitLab CI", "Prometheus"],
        ["Kubernetes", "GCP", "Helm", "CircleCI", "Grafana"],
        ["Docker", "AWS", "CloudFormation", "Jenkins", "Datadog"],
        ["Kubernetes", "AWS", "Terraform", "GitHub Actions", "ELK Stack"]
    ]
    
    all_skill_sets = [
        ("Backend", backend_skills),
        ("Frontend", frontend_skills),
        ("DataScience", datascience_skills),
        ("DevOps", devops_skills)
    ]
    
    resume_id = 0
    for category, skill_sets in all_skill_sets:
        for skills in skill_sets:
            resume = StructuredResume(
                resume_id=f"{category}_{resume_id}",
                job_category=category,
                sections=ResumeSections(
                    skills=", ".join(skills),
                    experience="Professional experience",
                    education="Bachelor's degree",
                    projects="Various projects",
                    raw_text="Resume content"
                ),
                skills=SkillSet(
                    explicit_skills=skills,
                    implicit_skills=[]
                ),
                normalized_skills=skills,
                scores=None,
                metadata=ResumeMetadata(
                    file_path=f"resume_{resume_id}.pdf",
                    processed_date="2025-01-01",
                    processing_time_ms=100
                )
            )
            resumes.append(resume)
            resume_id += 1
    
    return resumes


def main():
    """Run clustering demo."""
    print("=" * 70)
    print("ClusteringEngine Demo - Smart Resume Screening System")
    print("=" * 70)
    print()
    
    # Create sample resumes
    print("Creating sample resumes with different skill profiles...")
    resumes = create_sample_resumes()
    print(f"Created {len(resumes)} sample resumes")
    print()
    
    # Generate features
    print("Generating feature vectors from resumes...")
    feature_gen = FeatureGenerator()
    feature_matrix, vocabulary = feature_gen.generate_feature_matrix(resumes)
    print(f"Feature matrix shape: {feature_matrix.shape}")
    print(f"Vocabulary size: {len(vocabulary)} unique skills")
    print()
    
    # Apply clustering
    print("Applying K-Means clustering (k=4)...")
    clustering_engine = ClusteringEngine(n_clusters=4)
    labels = clustering_engine.fit_clusters(feature_matrix)
    print(f"Clustering complete!")
    print()
    
    # Display cluster assignments
    print("Cluster Assignments:")
    print("-" * 70)
    for i, (resume, label) in enumerate(zip(resumes, labels)):
        print(f"Resume {i+1:2d} ({resume.job_category:12s}): Cluster {label}")
    print()
    
    # Get cluster centroids
    print("Cluster Centroids:")
    print("-" * 70)
    centroids = clustering_engine.get_cluster_centroids()
    print(f"Centroid matrix shape: {centroids.shape}")
    print()
    
    # Get cluster profiles
    print("Cluster Profiles (Top 5 Skills per Cluster):")
    print("-" * 70)
    profiles = clustering_engine.get_cluster_profiles(vocabulary, top_n=5)
    
    for cluster_id, top_skills in profiles.items():
        print(f"\nCluster {cluster_id}:")
        print(f"  Top skills: {', '.join(top_skills)}")
        
        # Show which resumes are in this cluster
        cluster_resumes = [
            resumes[i].resume_id 
            for i, label in enumerate(labels) 
            if label == cluster_id
        ]
        print(f"  Resumes: {', '.join(cluster_resumes)}")
        print(f"  Count: {len(cluster_resumes)} resumes")
    
    print()
    print("=" * 70)
    print("Demo complete!")
    print("=" * 70)


if __name__ == "__main__":
    main()
