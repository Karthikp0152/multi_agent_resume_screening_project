# Test Fixtures and Sample Data

This directory contains test fixtures and sample data for the Smart Resume Screening System. The data supports testing of both CSV and PDF processing pipelines.

## Directory Structure

```
tests/fixtures/
├── README.md                           # This file
├── sample_resumes/                     # Sample resume files
│   └── pdf/                           # Text versions of PDF resumes
│       ├── accountant_sample.txt      # Sample accountant resume
│       ├── it_developer_sample.txt    # Sample IT developer resume
│       └── healthcare_nurse_sample.txt # Sample healthcare nurse resume
├── sample_data/                        # CSV and structured data
│   └── sample_resumes.csv             # Sample CSV with 5 resume entries
├── expected_outputs/                   # Expected JSON outputs for validation
│   ├── accountant_expected.json       # Expected output for accountant resume
│   └── it_developer_expected.json     # Expected output for IT developer resume
├── job_requirements/                   # Sample job requirement files
│   ├── accountant_job.json            # Accountant job requirements
│   ├── software_developer_job.json    # Software developer job requirements
│   └── nurse_job.json                 # Nurse job requirements
└── validation_data/                    # Cross-source validation data
    └── pdf_csv_mapping.json           # Mapping between PDF and CSV entries

```

## Data Sources

### 1. Sample Resumes (PDF/Text Format)

Located in `sample_resumes/pdf/`, these files simulate PDF resume content in text format for testing the extraction pipeline.

**Files:**
- `accountant_sample.txt` - CPA with 8+ years experience, financial reporting skills
- `it_developer_sample.txt` - Full Stack Developer with React, Node.js, AWS skills
- `healthcare_nurse_sample.txt` - Registered Nurse with ICU experience

**Usage:**
```python
from pathlib import Path
resume_path = Path("tests/fixtures/sample_resumes/pdf/accountant_sample.txt")
```

### 2. Sample CSV Data

Located in `sample_data/sample_resumes.csv`, this file contains 5 resume entries in the same format as the main archive CSV.

**Columns:**
- `ID` - Unique resume identifier (TEST001-TEST005)
- `Resume_str` - Plain text resume content
- `Resume_html` - HTML formatted resume excerpt
- `Category` - Job category classification

**Categories Covered:**
- ACCOUNTANT
- INFORMATION-TECHNOLOGY
- HEALTHCARE
- ENGINEERING
- SALES

**Usage:**
```python
import pandas as pd
df = pd.read_csv("tests/fixtures/sample_data/sample_resumes.csv")
```

### 3. Expected Outputs

Located in `expected_outputs/`, these JSON files show the expected structured output after processing resumes.

**Structure:**
```json
{
  "resume_id": "string",
  "job_category": "string",
  "sections": {
    "skills": "string",
    "experience": "string",
    "education": "string",
    "projects": "string",
    "raw_text": "string"
  },
  "skills": {
    "explicit_skills": ["string"],
    "implicit_skills": ["string"]
  },
  "normalized_skills": ["string"],
  "scores": null,
  "metadata": {
    "file_path": "string",
    "processed_date": "string",
    "processing_time_ms": 0
  }
}
```

**Usage:**
```python
import json
with open("tests/fixtures/expected_outputs/accountant_expected.json") as f:
    expected = json.load(f)
```

### 4. Job Requirements

Located in `job_requirements/`, these JSON files define job requirements for scoring tests.

**Structure:**
```json
{
  "job_title": "string",
  "job_category": "string",
  "required_skills": ["string"],
  "preferred_skills": ["string"],
  "experience_years": 0,
  "education": "string"
}
```

**Usage:**
```python
import json
with open("tests/fixtures/job_requirements/accountant_job.json") as f:
    job_req = json.load(f)
    required_skills = job_req["required_skills"]
```

### 5. Validation Data

Located in `validation_data/pdf_csv_mapping.json`, this file maps PDF files to CSV entries for cross-source validation.

**Purpose:**
- Validate PDF extraction accuracy against CSV ground truth
- Test cross-source consistency
- Ensure both pipelines extract similar skills

**Structure:**
```json
{
  "mappings": [
    {
      "csv_id": "TEST001",
      "pdf_file": "path/to/pdf",
      "job_category": "ACCOUNTANT",
      "validation_notes": "string"
    }
  ],
  "validation_criteria": {
    "skill_overlap_threshold": 0.7,
    "category_match_required": true,
    "min_skills_extracted": 5
  }
}
```

## Testing Scenarios

### Scenario 1: CSV Processing Pipeline
Test the system's ability to process CSV data directly without PDF extraction.

```python
from src.resume_processor import ResumeProcessor

processor = ResumeProcessor(config)
csv_path = "tests/fixtures/sample_data/sample_resumes.csv"
resumes = processor.load_from_csv(csv_path)
```

### Scenario 2: PDF Extraction Pipeline
Test the system's ability to extract text from PDF-like files and process them.

```python
from src.resume_processor import ResumeProcessor

processor = ResumeProcessor(config)
pdf_path = "tests/fixtures/sample_resumes/pdf/accountant_sample.txt"
resume = processor.process_resume(pdf_path)
```

### Scenario 3: Scoring Tests
Test ATS and semantic scoring using job requirements.

```python
from src.scoring_engine import ScoringEngine
import json

engine = ScoringEngine()
with open("tests/fixtures/job_requirements/accountant_job.json") as f:
    job_req = json.load(f)

resume_skills = ["Financial Reporting", "GAAP", "QuickBooks"]
scores = engine.calculate_both_scores(resume_skills, job_req["required_skills"])
```

### Scenario 4: Cross-Source Validation
Test consistency between CSV and PDF processing.

```python
from src.resume_processor import ResumeProcessor
import json

processor = ResumeProcessor(config)

# Load mapping
with open("tests/fixtures/validation_data/pdf_csv_mapping.json") as f:
    mapping = json.load(f)

# Process both sources and compare
for entry in mapping["mappings"]:
    csv_resume = processor.process_csv_entry(entry["csv_id"])
    pdf_resume = processor.process_resume(entry["pdf_file"])
    # Compare skills, categories, etc.
```

### Scenario 5: Feature Engineering Tests
Test feature vector generation from both data sources.

```python
from src.feature_generator import FeatureGenerator

generator = FeatureGenerator()
csv_resumes = processor.load_from_csv("tests/fixtures/sample_data/sample_resumes.csv")
feature_matrix, vocabulary = generator.generate_feature_matrix(csv_resumes)
```

## Data Quality Notes

1. **Skill Diversity**: Sample resumes cover diverse skill sets across different job categories
2. **Realistic Content**: Resume content mimics real-world resume structures and language
3. **Category Coverage**: Includes 5 different job categories for classification testing
4. **Skill Normalization**: Includes variations (e.g., "js" vs "JavaScript") to test normalization
5. **Cross-Source Consistency**: PDF and CSV samples for same roles have overlapping skills

## Extending Test Data

To add new test fixtures:

1. **New Resume Sample**: Add to `sample_resumes/pdf/` with descriptive filename
2. **New CSV Entry**: Add row to `sample_resumes.csv` with unique TEST ID
3. **Expected Output**: Create corresponding JSON in `expected_outputs/`
4. **Job Requirements**: Add job requirement file if testing new category
5. **Validation Mapping**: Update `pdf_csv_mapping.json` if linking PDF to CSV

## Maintenance

- Keep sample data synchronized with actual archive data structure
- Update expected outputs when data models change
- Validate that skill aliases in samples exist in `config/skill_aliases.json`
- Ensure job categories in samples exist in `config/job_categories.json`
