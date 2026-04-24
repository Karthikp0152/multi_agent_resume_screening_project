"""
Demonstration script for the AssociationMiner component.

This script shows how to use the AssociationMiner to discover frequently
co-occurring skills in resume data.
"""

from src.association_miner import AssociationMiner
from src.models import AssociationRule


def main():
    """Demonstrate AssociationMiner functionality."""
    
    print("=" * 70)
    print("AssociationMiner Demonstration")
    print("=" * 70)
    print()
    
    # Create sample resume data
    print("Creating sample resume data...")
    resumes = [
        {
            'resume_id': '1',
            'normalized_skills': ['Python', 'Machine Learning', 'Data Science', 'TensorFlow', 'Pandas']
        },
        {
            'resume_id': '2',
            'normalized_skills': ['Python', 'Machine Learning', 'Deep Learning', 'TensorFlow', 'Keras']
        },
        {
            'resume_id': '3',
            'normalized_skills': ['Python', 'Data Science', 'SQL', 'Pandas', 'NumPy']
        },
        {
            'resume_id': '4',
            'normalized_skills': ['Machine Learning', 'Data Science', 'R', 'Statistics', 'Scikit-learn']
        },
        {
            'resume_id': '5',
            'normalized_skills': ['Python', 'Machine Learning', 'Data Science', 'Scikit-learn', 'Pandas']
        },
        {
            'resume_id': '6',
            'normalized_skills': ['Python', 'Deep Learning', 'TensorFlow', 'Keras', 'PyTorch']
        },
        {
            'resume_id': '7',
            'normalized_skills': ['Data Science', 'SQL', 'Tableau', 'Excel', 'Statistics']
        },
        {
            'resume_id': '8',
            'normalized_skills': ['Python', 'Machine Learning', 'NLP', 'NLTK', 'Scikit-learn']
        },
        {
            'resume_id': '9',
            'normalized_skills': ['Python', 'Data Science', 'Machine Learning', 'Pandas', 'NumPy']
        },
        {
            'resume_id': '10',
            'normalized_skills': ['Deep Learning', 'TensorFlow', 'Keras', 'Computer Vision', 'OpenCV']
        }
    ]
    
    print(f"Created {len(resumes)} sample resumes")
    print()
    
    # Initialize AssociationMiner
    print("Initializing AssociationMiner...")
    print("  - min_support: 0.3 (30% of resumes must contain the itemset)")
    print("  - min_confidence: 0.6 (60% confidence for rules)")
    miner = AssociationMiner(min_support=0.3, min_confidence=0.6)
    print()
    
    # Mine associations
    print("Mining association rules...")
    rules = miner.mine_associations(resumes)
    print(f"Found {len(rules)} association rules")
    print()
    
    # Display results
    if rules:
        print("=" * 70)
        print("Top Association Rules (sorted by lift)")
        print("=" * 70)
        print()
        
        # Sort by lift (higher lift = stronger association)
        sorted_rules = sorted(rules, key=lambda r: r.lift, reverse=True)
        
        for i, rule in enumerate(sorted_rules[:10], 1):
            antecedents = ', '.join(sorted(rule.antecedents))
            consequents = ', '.join(sorted(rule.consequents))
            
            print(f"Rule {i}:")
            print(f"  IF: {antecedents}")
            print(f"  THEN: {consequents}")
            print(f"  Support: {rule.support:.3f} ({rule.support*100:.1f}%)")
            print(f"  Confidence: {rule.confidence:.3f} ({rule.confidence*100:.1f}%)")
            print(f"  Lift: {rule.lift:.3f}")
            print()
            
            # Explain the metrics
            if i == 1:
                print("  Interpretation:")
                print(f"    - {rule.support*100:.1f}% of resumes contain both skill sets")
                print(f"    - {rule.confidence*100:.1f}% of resumes with '{antecedents}'")
                print(f"      also have '{consequents}'")
                print(f"    - Lift of {rule.lift:.2f} means this combination is")
                print(f"      {rule.lift:.2f}x more likely than random chance")
                print()
    else:
        print("No association rules found with the current thresholds.")
        print("Try lowering min_support or min_confidence.")
    
    print("=" * 70)
    print("Demonstration complete!")
    print("=" * 70)


if __name__ == "__main__":
    main()
