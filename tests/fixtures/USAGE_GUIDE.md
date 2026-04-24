# Test Fixtures Usage Guide

This guide provides practical examples of how to use the test fixtures in your tests for the Smart Resume Screening System.

## Quick Start

All fixtures are automatically available through pytest fixtures defined in `tests/conftest.py`. Simply add the fixture name as a parameter to your test function.

```python
def test_my_feature(sample_csv_path, fixtures_dir):
    # Fixtures are automatically injected
    assert sample_csv_path.exists()
```

## Available Fixtures

### Directory Fixtures

#### `fixtures_dir`
Returns the path to the fixtures directory.

```python
def test_with_fixtures_dir(fixtures_dir):
    assert fixtures_dir.exists()
    custom_file = fixtures_dir / "my_custom_data.json"
```

### CSV Data Fixtures

#### `sample_csv_path`
Returns path to the sample CSV file with 5 resume entries.

```python
def test_csv_processing(sample_csv_path):
    import pandas as pd
    df = pd.read_csv(sample_csv_path)
    assert len(df) == 5
    assert "ID" in df.columns
```

### PDF Resume Fixtures

#### `sample_pdf_resumes`
Returns a dictionary of paths to sample PDF resume files.

```python
def test_pdf_extraction(sample_pdf_resumes):
    accountant_resume = sample_pdf_resumes["accountant"]
    content = accountant_resume.read_text()
    assert "SKILLS" in content.upper()
```

Available keys:
- `"accountant"` - Accountant resume
- `"it_developer"` - IT Developer resume
- `"healthcare"` - Healthcare Nurse resume

### Expected Output Fixtures

#### `expected_outputs`
Returns a dictionary of paths to expected output JSON files.

```python
def test_output_validation(expected_outputs):
    import json
    with open(expected_outputs["accountant"]) as f:
        expected = json.load(f)
    assert expected["job_category"] == "ACCOUNTANT"
```

Available keys:
- `"accountant"` - Expected output for accountant resume
- `"it_developer"` - Expected output for IT developer resume

### Job Requirements Fixtures

#### `job_requirements`
Returns a dictionary of paths to job requirement JSON files.

```python
def test_scoring(job_requirements):
    import json
    with open(job_requirements["accountant"]) as f:
        job_req = json.load(f)
    required_skills = job_req["required_skills"]
    assert len(required_skills) > 0
```

Available keys:
- `"accountant"` - Accountant job requirements
- `"software_developer"` - Software Developer job requirements
- `"nurse"` - Nurse job requirements

#### `load_job_requirements`
Helper function to load job requirements directly.

```python
def test_with_job_req_helper(load_job_requirements):
    job_req = load_job_requirements("accountant")
    assert "required_skills" in job_req
    assert job_req["job_category"] == "ACCOUNTANT"
```

### Validation Fixtures

#### `validation_mapping`
Returns path to the PDF-CSV validation mapping file.

```python
def test_cross_validation(validation_mapping):
    import json
    with open(validation_mapping) as f:
        mapping = json.load(f)
    assert "mappings" in mapping
    assert "validation_criteria" in mapping
```

## Common Testing Patterns

### Pattern 1: Testing CSV Processing

```python
def test_csv_resume_processing(sample_csv_path):
    """Test processing resumes from CSV file."""
    from src.resume_processor import ResumeProcessor
    import pandas as pd
    
    # Load CSV
    df = pd.read_csv(sample_csv_path)
    
    # Process first resume
    processor = ResumeProcessor()
    resume_text = df.iloc[0]["Resume_str"]
    category = df.iloc[0]["Category"]
    
    # Your processing logic here
    assert category in ["ACCOUNTANT", "INFORMATION-TECHNOLOGY", "HEALTHCARE"]
```

### Pattern 2: Testing PDF Extraction

```python
def test_pdf_text_extraction(sample_pdf_resumes):
    """Test extracting text from PDF-like files."""
    from src.text_extractor import TextExtractor
    
    extractor = TextExtractor()
    
    # Test with accountant resume
    accountant_path = sample_pdf_resumes["accountant"]
    text = extractor.extract_from_text(str(accountant_path))
    
    assert len(text) > 0
    assert "SKILLS" in text.upper()
```

### Pattern 3: Testing Skill Extraction

```python
def test_skill_extraction_from_fixtures(sample_pdf_resumes):
    """Test skill extraction using fixture resumes."""
    from src.skill_extractor import SkillExtractor
    from src.section_parser import SectionParser
    
    extractor = SkillExtractor()
    parser = SectionParser()
    
    # Load resume
    resume_text = sample_pdf_resumes["it_developer"].read_text()
    
    # Parse sections
    sections = parser.parse_sections(resume_text)
    
    # Extract skills
    skills = extractor.extract_all_skills(sections)
    
    assert len(skills.explicit_skills) > 0
    assert "JavaScript" in skills.explicit_skills or "Python" in skills.explicit_skills
```

### Pattern 4: Testing Scoring Engine

```python
def test_ats_scoring_with_fixtures(load_job_requirements):
    """Test ATS scoring using fixture job requirements."""
    from src.scoring_engine import ScoringEngine
    
    engine = ScoringEngine()
    
    # Load job requirements
    job_req = load_job_requirements("software_developer")
    required_skills = job_req["required_skills"]
    
    # Sample resume skills
    resume_skills = ["JavaScript", "React", "Node.js", "Python", "SQL"]
    
    # Calculate score
    ats_score = engine.calculate_ats_score(resume_skills, required_skills)
    
    assert 0 <= ats_score <= 100
    assert ats_score > 0  # Should have some matches
```

### Pattern 5: Testing Output Validation

```python
def test_output_matches_expected(sample_csv_path, load_expected_output):
    """Test that processing output matches expected structure."""
    from src.resume_processor import ResumeProcessor
    import pandas as pd
    
    processor = ResumeProcessor()
    
    # Load expected output
    expected = load_expected_output("accountant")
    
    # Process corresponding CSV entry
    df = pd.read_csv(sample_csv_path)
    accountant_row = df[df["ID"] == "TEST001"].iloc[0]
    
    # Process resume
    result = processor.process_csv_entry(accountant_row)
    
    # Validate structure
    assert result["resume_id"] == expected["resume_id"]
    assert result["job_category"] == expected["job_category"]
    assert "sections" in result
    assert "skills" in result
```

### Pattern 6: Testing Cross-Source Validation

```python
def test_csv_vs_pdf_consistency(sample_csv_path, sample_pdf_resumes, validation_mapping):
    """Test consistency between CSV and PDF processing."""
    from src.resume_processor import ResumeProcessor
    import pandas as pd
    import json
    
    processor = ResumeProcessor()
    
    # Load validation mapping
    with open(validation_mapping) as f:
        mapping_data = json.load(f)
    
    # Get first mapping
    first_mapping = mapping_data["mappings"][0]
    csv_id = first_mapping["csv_id"]
    
    # Process CSV entry
    df = pd.read_csv(sample_csv_path)
    csv_row = df[df["ID"] == csv_id].iloc[0]
    csv_result = processor.process_csv_entry(csv_row)
    
    # Process PDF file
    pdf_path = first_mapping["pdf_file"]
    pdf_result = processor.process_resume(pdf_path)
    
    # Compare results
    csv_skills = set(csv_result["normalized_skills"])
    pdf_skills = set(pdf_result["normalized_skills"])
    
    # Calculate overlap
    overlap = len(csv_skills & pdf_skills) / len(csv_skills | pdf_skills)
    
    # Should have significant overlap
    threshold = mapping_data["validation_criteria"]["skill_overlap_threshold"]
    assert overlap >= threshold
```

### Pattern 7: Testing Feature Generation

```python
def test_feature_generation_from_csv(sample_csv_path):
    """Test feature generation from CSV data."""
    from src.feature_generator import FeatureGenerator
    from src.resume_processor import ResumeProcessor
    import pandas as pd
    
    processor = ResumeProcessor()
    generator = FeatureGenerator()
    
    # Load and process all CSV resumes
    df = pd.read_csv(sample_csv_path)
    resumes = []
    for _, row in df.iterrows():
        resume = processor.process_csv_entry(row)
        resumes.append(resume)
    
    # Generate features
    feature_matrix, vocabulary = generator.generate_feature_matrix(resumes)
    
    assert feature_matrix.shape[0] == len(resumes)
    assert feature_matrix.shape[1] == len(vocabulary)
    assert len(vocabulary) > 0
```

### Pattern 8: Testing Classification

```python
def test_classification_with_fixtures(sample_csv_path):
    """Test classification using fixture data."""
    from src.classifier import Classifier
    from src.feature_generator import FeatureGenerator
    from src.resume_processor import ResumeProcessor
    import pandas as pd
    
    processor = ResumeProcessor()
    generator = FeatureGenerator()
    classifier = Classifier()
    
    # Load and process CSV resumes
    df = pd.read_csv(sample_csv_path)
    resumes = [processor.process_csv_entry(row) for _, row in df.iterrows()]
    
    # Generate features
    X, vocab = generator.generate_feature_matrix(resumes)
    y = [r["job_category"] for r in resumes]
    
    # Train classifier
    classifier.train_proposed(X, y)
    
    # Predict
    predictions = classifier.predict(X)
    
    assert len(predictions) == len(resumes)
```

## Integration Test Example

Here's a complete integration test using multiple fixtures:

```python
def test_end_to_end_pipeline(
    sample_csv_path,
    sample_pdf_resumes,
    load_job_requirements,
    validation_mapping
):
    """Complete end-to-end test of the resume screening pipeline."""
    from src.resume_processor import ResumeProcessor
    from src.scoring_engine import ScoringEngine
    import pandas as pd
    import json
    
    processor = ResumeProcessor()
    scorer = ScoringEngine()
    
    # 1. Process CSV data
    df = pd.read_csv(sample_csv_path)
    csv_resumes = [processor.process_csv_entry(row) for _, row in df.iterrows()]
    assert len(csv_resumes) == 5
    
    # 2. Process PDF data
    pdf_resumes = []
    for resume_type, path in sample_pdf_resumes.items():
        resume = processor.process_resume(str(path))
        pdf_resumes.append(resume)
    assert len(pdf_resumes) == 3
    
    # 3. Score resumes against job requirements
    job_req = load_job_requirements("software_developer")
    required_skills = job_req["required_skills"]
    
    for resume in csv_resumes:
        if resume["job_category"] == "INFORMATION-TECHNOLOGY":
            scores = scorer.calculate_both_scores(
                resume["normalized_skills"],
                required_skills
            )
            assert scores.ats_score >= 0
            assert 0 <= scores.semantic_score <= 1
    
    # 4. Validate cross-source consistency
    with open(validation_mapping) as f:
        mapping_data = json.load(f)
    
    for mapping in mapping_data["mappings"]:
        csv_id = mapping["csv_id"]
        csv_resume = next(r for r in csv_resumes if r["resume_id"] == csv_id)
        
        # Find corresponding PDF resume
        pdf_path = mapping["pdf_file"]
        pdf_resume = processor.process_resume(pdf_path)
        
        # Validate category match
        assert csv_resume["job_category"] == pdf_resume["job_category"]
```

## Tips and Best Practices

1. **Use Fixtures for Setup**: Let pytest fixtures handle file loading and setup
2. **Test Data Isolation**: Each test should be independent and not modify shared fixtures
3. **Validate Structure First**: Check data structure before testing business logic
4. **Use Helper Fixtures**: Leverage `load_job_requirements` and `load_expected_output` for cleaner tests
5. **Test Both Sources**: Always test both CSV and PDF processing paths
6. **Cross-Validate**: Use validation mapping to ensure consistency between sources
7. **Check Edge Cases**: Test with different job categories and skill combinations
8. **Assert Meaningful Values**: Don't just check existence, validate actual content

## Troubleshooting

### Fixture Not Found
```python
# Bad: Typo in fixture name
def test_something(sample_csv):  # Wrong name
    pass

# Good: Correct fixture name
def test_something(sample_csv_path):  # Correct
    pass
```

### File Not Found
```python
# Make sure to use the fixture, not hardcoded paths
def test_something(sample_csv_path):
    # Good: Use fixture
    df = pd.read_csv(sample_csv_path)
    
    # Bad: Hardcoded path
    # df = pd.read_csv("tests/fixtures/sample_data/sample_resumes.csv")
```

### JSON Loading Issues
```python
# Always use context manager for file operations
def test_something(expected_outputs):
    # Good
    with open(expected_outputs["accountant"]) as f:
        data = json.load(f)
    
    # Bad: File not closed properly
    # f = open(expected_outputs["accountant"])
    # data = json.load(f)
```

## Adding New Fixtures

To add new test fixtures:

1. Add the file to appropriate directory under `tests/fixtures/`
2. Add a fixture function in `tests/conftest.py`
3. Document the fixture in this guide
4. Add validation tests in `tests/test_fixtures.py`

Example:
```python
# In tests/conftest.py
@pytest.fixture
def my_new_fixture(fixtures_dir):
    """Description of what this fixture provides."""
    return fixtures_dir / "my_data" / "my_file.json"
```

## Further Reading

- [pytest fixtures documentation](https://docs.pytest.org/en/stable/fixture.html)
- [Test Fixtures README](README.md) - Overview of all available fixtures
- Project design document - Understanding the system architecture
