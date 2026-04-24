"""
Integration tests for the AssociationMiner component.

Tests the complete association mining workflow with realistic resume data
to verify end-to-end functionality.
"""

import pytest
from src.association_miner import AssociationMiner, AssociationRule


class TestAssociationMinerIntegration:
    """Integration tests for complete association mining workflow."""
    
    def test_complete_mining_workflow(self):
        """Test complete workflow from resumes to association rules."""
        # Create realistic resume data
        resumes = [
            {
                'resume_id': '1',
                'normalized_skills': ['Python', 'Machine Learning', 'Data Science', 'TensorFlow']
            },
            {
                'resume_id': '2',
                'normalized_skills': ['Python', 'Machine Learning', 'Deep Learning', 'TensorFlow']
            },
            {
                'resume_id': '3',
                'normalized_skills': ['Python', 'Data Science', 'SQL', 'Pandas']
            },
            {
                'resume_id': '4',
                'normalized_skills': ['Machine Learning', 'Data Science', 'R', 'Statistics']
            },
            {
                'resume_id': '5',
                'normalized_skills': ['Python', 'Machine Learning', 'Data Science', 'Scikit-learn']
            },
            {
                'resume_id': '6',
                'normalized_skills': ['Python', 'Deep Learning', 'TensorFlow', 'Keras']
            },
            {
                'resume_id': '7',
                'normalized_skills': ['Data Science', 'SQL', 'Tableau', 'Excel']
            },
            {
                'resume_id': '8',
                'normalized_skills': ['Python', 'Machine Learning', 'NLP', 'NLTK']
            }
        ]
        
        # Initialize miner with reasonable thresholds
        miner = AssociationMiner(min_support=0.3, min_confidence=0.5)
        
        # Run complete mining pipeline
        rules = miner.mine_associations(resumes)
        
        # Verify results
        assert isinstance(rules, list)
        
        # Should find some rules with this data
        assert len(rules) > 0
        
        # Verify rule structure
        for rule in rules:
            assert isinstance(rule, AssociationRule)
            assert len(rule.antecedents) > 0
            assert len(rule.consequents) > 0
            assert 0 <= rule.support <= 1
            assert 0 <= rule.confidence <= 1
            assert rule.lift > 0
        
        # Verify that Python -> Machine Learning might be a rule
        # (Python appears in 6/8 resumes, ML in 5/8, together in 4/8)
        python_ml_rules = [
            r for r in rules
            if 'Python' in r.antecedents and 'Machine Learning' in r.consequents
        ]
        
        # This is a strong association in our data
        if python_ml_rules:
            rule = python_ml_rules[0]
            assert rule.confidence >= 0.5
            assert rule.lift > 1.0  # Positive correlation
    
    def test_mining_with_varying_thresholds(self):
        """Test that different thresholds produce different results."""
        resumes = [
            {'normalized_skills': ['A', 'B', 'C']},
            {'normalized_skills': ['A', 'B', 'D']},
            {'normalized_skills': ['A', 'C', 'D']},
            {'normalized_skills': ['B', 'C', 'D']},
            {'normalized_skills': ['A', 'B', 'C', 'D']},
        ]
        
        # Low thresholds should find more rules
        miner_low = AssociationMiner(min_support=0.2, min_confidence=0.3)
        rules_low = miner_low.mine_associations(resumes)
        
        # High thresholds should find fewer rules
        miner_high = AssociationMiner(min_support=0.6, min_confidence=0.8)
        rules_high = miner_high.mine_associations(resumes)
        
        # Low threshold should find at least as many rules as high threshold
        assert len(rules_low) >= len(rules_high)
    
    def test_mining_with_sparse_data(self):
        """Test mining with sparse skill data (few common skills)."""
        resumes = [
            {'normalized_skills': ['Python', 'Java']},
            {'normalized_skills': ['JavaScript', 'React']},
            {'normalized_skills': ['C++', 'Qt']},
            {'normalized_skills': ['Ruby', 'Rails']},
            {'normalized_skills': ['Go', 'Docker']},
        ]
        
        # With sparse data and reasonable thresholds, may find no rules
        miner = AssociationMiner(min_support=0.4, min_confidence=0.6)
        rules = miner.mine_associations(resumes)
        
        # Should handle sparse data gracefully
        assert isinstance(rules, list)
        # May be empty, which is correct for sparse data
    
    def test_mining_with_dense_data(self):
        """Test mining with dense skill data (many common skills)."""
        # All resumes share common core skills
        core_skills = ['Python', 'Git', 'Linux']
        
        resumes = [
            {'normalized_skills': core_skills + ['Django', 'PostgreSQL']},
            {'normalized_skills': core_skills + ['Flask', 'MySQL']},
            {'normalized_skills': core_skills + ['FastAPI', 'MongoDB']},
            {'normalized_skills': core_skills + ['Django', 'Redis']},
            {'normalized_skills': core_skills + ['Flask', 'PostgreSQL']},
        ]
        
        miner = AssociationMiner(min_support=0.4, min_confidence=0.5)
        rules = miner.mine_associations(resumes)
        
        # Should find rules involving core skills
        assert len(rules) > 0
        
        # Core skills should appear in many rules
        core_skill_rules = [
            r for r in rules
            if any(skill in r.antecedents or skill in r.consequents
                   for skill in core_skills)
        ]
        assert len(core_skill_rules) > 0
    
    def test_rule_quality_metrics(self):
        """Test that generated rules have meaningful quality metrics."""
        # Create data with clear associations
        resumes = [
            {'normalized_skills': ['Frontend', 'React', 'JavaScript']},
            {'normalized_skills': ['Frontend', 'React', 'TypeScript']},
            {'normalized_skills': ['Frontend', 'Vue', 'JavaScript']},
            {'normalized_skills': ['Backend', 'Node.js', 'JavaScript']},
            {'normalized_skills': ['Frontend', 'React', 'JavaScript', 'CSS']},
            {'normalized_skills': ['Frontend', 'React', 'Redux']},
        ]
        
        miner = AssociationMiner(min_support=0.3, min_confidence=0.5)
        rules = miner.mine_associations(resumes)
        
        if rules:
            # Check that lift values make sense
            for rule in rules:
                # Lift > 1 means positive correlation
                # Lift = 1 means independence
                # Lift < 1 means negative correlation
                assert rule.lift > 0
                
                # Confidence should be at least min_confidence
                assert rule.confidence >= miner.min_confidence
                
                # Support should be at least min_support
                assert rule.support >= miner.min_support
    
    def test_mining_preserves_skill_names(self):
        """Test that skill names are preserved correctly in rules."""
        resumes = [
            {'normalized_skills': ['Machine Learning', 'Deep Learning', 'Neural Networks']},
            {'normalized_skills': ['Machine Learning', 'Deep Learning', 'CNN']},
            {'normalized_skills': ['Machine Learning', 'Neural Networks', 'RNN']},
            {'normalized_skills': ['Deep Learning', 'Neural Networks', 'Transformers']},
        ]
        
        miner = AssociationMiner(min_support=0.4, min_confidence=0.5)
        rules = miner.mine_associations(resumes)
        
        # Verify that multi-word skill names are preserved
        all_skills_in_rules = set()
        for rule in rules:
            all_skills_in_rules.update(rule.antecedents)
            all_skills_in_rules.update(rule.consequents)
        
        # Check that original skill names appear in rules
        expected_skills = {'Machine Learning', 'Deep Learning', 'Neural Networks'}
        assert len(all_skills_in_rules.intersection(expected_skills)) > 0
