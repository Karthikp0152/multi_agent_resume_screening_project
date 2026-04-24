"""
Integration tests for the EvaluationModule component.

Tests the EvaluationModule working with other system components like
Classifier, ClusteringEngine, and FeatureGenerator.
"""

import pytest
import numpy as np
from src.evaluation_module import EvaluationModule
from src.classifier import Classifier
from src.clustering_engine import ClusteringEngine
from src.feature_generator import FeatureGenerator
from src.models import StructuredResume, ResumeSections, SkillSet, ResumeMetadata


@pytest.fixture
def sample_resumes():
    """Create sample structured resumes for testing."""
    resumes = []
    
    # Create resumes for different categories
    categories = ['ACCOUNTANT', 'ADVOCATE', 'AGRICULTURE']
    skills_by_category = {
        'ACCOUNTANT': ['Excel', 'QuickBooks', 'Accounting', 'Finance'],
        'ADVOCATE': ['Legal Research', 'Contract Law', 'Litigation', 'Legal Writing'],
        'AGRICULTURE': ['Crop Management', 'Soil Science', 'Irrigation', 'Farming']
    }
    
    for i, category in enumerate(categories):
        for j in range(5):  # 5 resumes per category
            resume_id = f"{category}_{j}"
            skills = skills_by_category[category]
            
            resume = StructuredResume(
                resume_id=resume_id,
                job_category=category,
                sections=ResumeSections(
                    skills=", ".join(skills),
                    experience="Sample experience",
                    education="Sample education",
                    projects="Sample projects",
                    raw_text=f"Resume for {category}"
                ),
                skills=SkillSet(explicit_skills=skills, implicit_skills=[]),
                normalized_skills=skills,
                scores=None,
                metadata=ResumeMetadata(
                    file_path=f"test_{resume_id}.pdf",
                    processed_date="2025-01-01T00:00:00",
                    processing_time_ms=100
                )
            )
            resumes.append(resume)
    
    return resumes


class TestEvaluationWithClassifier:
    """Integration tests with Classifier component."""
    
    def test_evaluate_classifier_predictions(self, sample_resumes):
        """Test evaluating classifier predictions."""
        # Generate features
        feature_gen = FeatureGenerator()
        X, vocabulary = feature_gen.generate_feature_matrix(sample_resumes)
        
        # Get true labels
        y_true = np.array([r.job_category for r in sample_resumes])
        
        # Train classifier
        classifier = Classifier()
        classifier.train_proposed(X, y_true)
        
        # Make predictions
        y_pred = classifier.predict(X, model_type="proposed")
        
        # Evaluate
        evaluator = EvaluationModule()
        metrics = evaluator.evaluate_classification(y_true, y_pred)
        
        # Should have high accuracy on training data
        assert metrics.accuracy > 0.8
        assert metrics.macro_f1 > 0.8
        assert len(metrics.per_class_f1) == 3
    
    def test_compare_baseline_and_proposed(self, sample_resumes):
        """Test comparing baseline and proposed models."""
        # Generate features
        feature_gen = FeatureGenerator()
        X, vocabulary = feature_gen.generate_feature_matrix(sample_resumes)
        
        # Get labels and texts
        y_true = np.array([r.job_category for r in sample_resumes])
        resume_texts = [r.sections.raw_text for r in sample_resumes]
        
        # Train both models
        classifier = Classifier()
        classifier.train_baseline(resume_texts, y_true)
        classifier.train_proposed(X, y_true)
        
        # Get predictions
        y_pred_baseline = classifier.predict(
            None, model_type="baseline", resume_texts=resume_texts
        )
        y_pred_proposed = classifier.predict(X, model_type="proposed")
        
        # Evaluate both
        evaluator = EvaluationModule()
        baseline_metrics = evaluator.evaluate_classification(y_true, y_pred_baseline)
        proposed_metrics = evaluator.evaluate_classification(y_true, y_pred_proposed)
        
        # Compare
        comparison = evaluator.compare_models(baseline_metrics, proposed_metrics)
        
        assert comparison.baseline_metrics == baseline_metrics
        assert comparison.proposed_metrics == proposed_metrics
        # Both should perform well on training data
        assert comparison.baseline_metrics.accuracy > 0.5
        assert comparison.proposed_metrics.accuracy > 0.5
    
    def test_fairness_analysis_with_classifier(self, sample_resumes):
        """Test fairness analysis on classifier predictions."""
        # Generate features
        feature_gen = FeatureGenerator()
        X, vocabulary = feature_gen.generate_feature_matrix(sample_resumes)
        
        # Get true labels
        y_true = np.array([r.job_category for r in sample_resumes])
        categories = ['ACCOUNTANT', 'ADVOCATE', 'AGRICULTURE']
        
        # Train classifier
        classifier = Classifier()
        classifier.train_proposed(X, y_true)
        
        # Make predictions
        y_pred = classifier.predict(X, model_type="proposed")
        
        # Analyze fairness
        evaluator = EvaluationModule()
        fairness_report = evaluator.analyze_fairness(y_true, y_pred, categories)
        
        assert len(fairness_report.per_category_f1) == 3
        assert fairness_report.mean_f1 > 0.0
        assert fairness_report.f1_variance >= 0.0
        # With balanced data and good performance, shouldn't flag many categories
        assert len(fairness_report.flagged_categories) <= 1


class TestEvaluationWithClustering:
    """Integration tests with ClusteringEngine component."""
    
    def test_evaluate_clustering_quality(self, sample_resumes):
        """Test evaluating clustering quality."""
        # Generate features
        feature_gen = FeatureGenerator()
        X, vocabulary = feature_gen.generate_feature_matrix(sample_resumes)
        
        # Perform clustering
        clustering_engine = ClusteringEngine(n_clusters=3)
        labels = clustering_engine.fit_clusters(X)
        
        # Evaluate
        evaluator = EvaluationModule()
        metrics = evaluator.evaluate_clustering(X, labels)
        
        assert metrics.n_clusters == 3
        assert -1.0 <= metrics.silhouette_score <= 1.0
        # With distinct skill sets, should have reasonable separation
        assert metrics.silhouette_score > 0.0
    
    def test_evaluate_different_cluster_counts(self, sample_resumes):
        """Test evaluating clustering with different k values."""
        # Generate features
        feature_gen = FeatureGenerator()
        X, vocabulary = feature_gen.generate_feature_matrix(sample_resumes)
        
        evaluator = EvaluationModule()
        
        # Test different cluster counts (limited by number of distinct samples)
        for k in [2, 3]:
            clustering_engine = ClusteringEngine(n_clusters=k)
            labels = clustering_engine.fit_clusters(X)
            
            metrics = evaluator.evaluate_clustering(X, labels)
            
            # n_clusters should match k (we have enough distinct samples)
            assert metrics.n_clusters == k
            assert -1.0 <= metrics.silhouette_score <= 1.0


class TestFullEvaluationPipeline:
    """Integration tests for complete evaluation pipeline."""
    
    def test_generate_comprehensive_report(self, sample_resumes):
        """Test generating a comprehensive evaluation report."""
        # Generate features
        feature_gen = FeatureGenerator()
        X, vocabulary = feature_gen.generate_feature_matrix(sample_resumes)
        
        # Get labels and texts
        y_true = np.array([r.job_category for r in sample_resumes])
        resume_texts = [r.sections.raw_text for r in sample_resumes]
        categories = ['ACCOUNTANT', 'ADVOCATE', 'AGRICULTURE']
        
        # Train classifier
        classifier = Classifier()
        classifier.train_baseline(resume_texts, y_true)
        classifier.train_proposed(X, y_true)
        
        # Get predictions
        y_pred_baseline = classifier.predict(
            None, model_type="baseline", resume_texts=resume_texts
        )
        y_pred_proposed = classifier.predict(X, model_type="proposed")
        
        # Perform clustering
        clustering_engine = ClusteringEngine(n_clusters=3)
        cluster_labels = clustering_engine.fit_clusters(X)
        
        # Evaluate everything
        evaluator = EvaluationModule()
        
        baseline_metrics = evaluator.evaluate_classification(y_true, y_pred_baseline)
        proposed_metrics = evaluator.evaluate_classification(y_true, y_pred_proposed)
        comparison = evaluator.compare_models(baseline_metrics, proposed_metrics)
        clustering_metrics = evaluator.evaluate_clustering(X, cluster_labels)
        fairness_report = evaluator.analyze_fairness(y_true, y_pred_proposed, categories)
        
        # Generate comprehensive report
        report = evaluator.generate_report(
            classification_metrics=proposed_metrics,
            clustering_metrics=clustering_metrics,
            comparison_report=comparison,
            fairness_report=fairness_report
        )
        
        # Verify report structure
        assert 'classification' in report
        assert 'clustering' in report
        assert 'model_comparison' in report
        assert 'fairness' in report
        
        # Verify report content
        assert report['classification']['accuracy'] > 0.0
        assert report['clustering']['n_clusters'] == 3
        assert 'baseline' in report['model_comparison']
        assert 'proposed' in report['model_comparison']
        assert 'improvements' in report['model_comparison']
        assert len(report['fairness']['per_category_f1']) == 3
    
    def test_cross_source_validation_simulation(self):
        """Test cross-source validation with simulated CSV and PDF data."""
        # Simulate CSV data (perfect predictions)
        csv_y_true = np.array(['A', 'B', 'C', 'A', 'B', 'C'])
        csv_y_pred = np.array(['A', 'B', 'C', 'A', 'B', 'C'])
        
        # Simulate PDF data (slightly worse predictions)
        pdf_y_true = np.array(['A', 'B', 'C', 'A', 'B', 'C'])
        pdf_y_pred = np.array(['A', 'B', 'C', 'A', 'B', 'A'])
        
        # Validate
        evaluator = EvaluationModule(consistency_threshold=0.2)
        report = evaluator.cross_source_validation(
            csv_y_true, csv_y_pred, pdf_y_true, pdf_y_pred
        )
        
        assert report.csv_accuracy == 1.0
        assert report.pdf_accuracy < 1.0
        assert report.accuracy_difference > 0.0
        # Should be consistent with threshold of 0.2
        assert report.consistent_performance is True
    
    def test_extraction_validation_simulation(self):
        """Test extraction validation with simulated data."""
        # Simulate CSV ground truth
        csv_texts = [
            "Python Java SQL Machine Learning",
            "JavaScript React Node.js",
            "Excel Accounting Finance"
        ]
        csv_skills = [
            ["Python", "Java", "SQL", "Machine Learning"],
            ["JavaScript", "React", "Node.js"],
            ["Excel", "Accounting", "Finance"]
        ]
        
        # Simulate PDF extraction (with some errors)
        pdf_texts = [
            "Python Java SQL",  # Missing ML
            "JavaScript React Node.js",  # Perfect
            "Excel Accounting"  # Missing Finance
        ]
        pdf_skills = [
            ["Python", "Java", "SQL"],
            ["JavaScript", "React", "Node.js"],
            ["Excel", "Accounting"]
        ]
        
        # Validate
        evaluator = EvaluationModule()
        report = evaluator.evaluate_extraction_pipeline(
            csv_texts, pdf_texts, csv_skills, pdf_skills
        )
        
        assert report.total_samples == 3
        assert 0.0 < report.skill_overlap_mean < 1.0
        assert 0.0 < report.extraction_accuracy < 1.0
        # Should detect that extraction is not perfect
        assert report.extraction_accuracy < 0.95
