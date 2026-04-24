# Requirements Document

## Introduction

The Smart Resume Screening System is an intelligent resume processing pipeline that extracts, normalizes, and analyzes resume data to improve candidate evaluation beyond traditional keyword-based Applicant Tracking Systems (ATS). The system processes resumes in PDF or text format, extracts structured information, performs semantic analysis, and enables data mining tasks including job category classification, candidate clustering, and skill association discovery.

## Glossary

- **Resume_Processor**: The system component responsible for processing resume files
- **Text_Extractor**: Component that converts PDF resumes to plain text
- **Section_Parser**: Component that divides resume text into logical sections
- **Skill_Extractor**: Component that identifies skills from resume sections using language models
- **Skill_Normalizer**: Component that standardizes skill variations using alias dictionaries and fuzzy matching
- **Scoring_Engine**: Component that calculates ATS and semantic similarity scores
- **Feature_Generator**: Component that converts skills into numerical feature vectors
- **Classifier**: Component that predicts job categories from resume features
- **Clustering_Engine**: Component that groups similar resumes using K-Means
- **Association_Miner**: Component that discovers frequently co-occurring skills using Apriori algorithm
- **Evaluation_Module**: Component that measures system performance and fairness
- **Structured_Data**: JSON representation of resume with normalized skills, scores, and metadata
- **ATS_Score**: Keyword match score between resume skills and job requirements
- **Semantic_Score**: Similarity score calculated using sentence embeddings
- **Explicit_Skill**: Skill directly listed in the Skills section of a resume
- **Implicit_Skill**: Skill inferred from Experience or Projects sections
- **Job_Category**: Classification label for resume (e.g., ACCOUNTANT, ADVOCATE, AGRICULTURE, APPAREL)

## Requirements

### Requirement 1: Resume Input Processing

**User Story:** As a recruiter, I want to submit resumes in PDF or text format, so that the system can process various resume formats.

#### Acceptance Criteria

1. WHEN a PDF resume file is provided, THE Resume_Processor SHALL accept the file for processing
2. WHEN a text resume file is provided, THE Resume_Processor SHALL accept the file for processing
3. WHEN a file with an unsupported format is provided, THE Resume_Processor SHALL return an error message indicating supported formats
4. THE Resume_Processor SHALL load resumes from the archive data directory organized by job categories

### Requirement 2: Text Extraction and Cleaning

**User Story:** As a system administrator, I want resumes converted to clean text, so that downstream components can process the content accurately.

#### Acceptance Criteria

1. WHEN a PDF resume is received, THE Text_Extractor SHALL convert the PDF to plain text
2. THE Text_Extractor SHALL remove special characters from extracted text
3. THE Text_Extractor SHALL normalize whitespace in extracted text
4. THE Text_Extractor SHALL preserve alphanumeric characters and standard punctuation
5. WHEN text extraction fails, THE Text_Extractor SHALL return an error with the failure reason

### Requirement 3: Section Parsing

**User Story:** As a data analyst, I want resumes divided into logical sections, so that I can extract information from specific resume parts.

#### Acceptance Criteria

1. THE Section_Parser SHALL identify the Skills section in resume text
2. THE Section_Parser SHALL identify the Experience section in resume text
3. THE Section_Parser SHALL identify the Education section in resume text
4. THE Section_Parser SHALL identify the Projects section in resume text
5. WHEN a section cannot be identified, THE Section_Parser SHALL mark that section as empty
6. THE Section_Parser SHALL output sections as labeled text segments

### Requirement 4: Explicit Skill Extraction

**User Story:** As a recruiter, I want skills explicitly listed in resumes extracted, so that I can quickly identify candidate qualifications.

#### Acceptance Criteria

1. WHEN the Skills section is available, THE Skill_Extractor SHALL extract all skills listed in that section
2. THE Skill_Extractor SHALL use a language model to identify skill entities
3. THE Skill_Extractor SHALL extract skills as individual text tokens
4. WHEN no Skills section exists, THE Skill_Extractor SHALL return an empty skill list for explicit skills

### Requirement 5: Implicit Skill Extraction

**User Story:** As a recruiter, I want skills inferred from work experience, so that I can identify candidate capabilities not explicitly listed.

#### Acceptance Criteria

1. WHEN the Experience section is available, THE Skill_Extractor SHALL extract implicit skills from work descriptions
2. WHEN the Projects section is available, THE Skill_Extractor SHALL extract implicit skills from project descriptions
3. THE Skill_Extractor SHALL use a language model to infer skills from context
4. THE Skill_Extractor SHALL distinguish between explicit skills and implicit skills in output

### Requirement 6: Skill Normalization

**User Story:** As a data analyst, I want skill variations standardized, so that equivalent skills are treated consistently across resumes.

#### Acceptance Criteria

1. THE Skill_Normalizer SHALL maintain an alias dictionary mapping skill variations to canonical forms
2. WHEN a skill matches an alias dictionary entry, THE Skill_Normalizer SHALL replace it with the canonical form
3. WHEN a skill does not match the alias dictionary, THE Skill_Normalizer SHALL apply fuzzy matching to find similar canonical skills
4. THE Skill_Normalizer SHALL output normalized skill names
5. FOR ALL extracted skills, THE Skill_Normalizer SHALL produce a normalized version

### Requirement 7: ATS Score Calculation

**User Story:** As a recruiter, I want keyword-based matching scores, so that I can compare candidates using traditional ATS metrics.

#### Acceptance Criteria

1. WHEN job requirements are provided, THE Scoring_Engine SHALL calculate keyword match percentage between resume skills and job requirements
2. THE Scoring_Engine SHALL output the ATS_Score as a numerical value between 0 and 100
3. THE Scoring_Engine SHALL count exact matches between normalized resume skills and job requirement keywords
4. THE Scoring_Engine SHALL calculate ATS_Score as the ratio of matched keywords to total required keywords

### Requirement 8: Semantic Score Calculation

**User Story:** As a recruiter, I want semantic similarity scores, so that I can identify candidates with conceptually related skills beyond exact keyword matches.

#### Acceptance Criteria

1. WHEN resume skills are extracted, THE Scoring_Engine SHALL generate sentence embeddings for the skills
2. WHEN job requirements are provided, THE Scoring_Engine SHALL generate sentence embeddings for the requirements
3. THE Scoring_Engine SHALL calculate cosine similarity between resume embeddings and job requirement embeddings
4. THE Scoring_Engine SHALL output the Semantic_Score as a numerical value between 0 and 1

### Requirement 9: Structured Data Generation

**User Story:** As a developer, I want resumes converted to structured JSON, so that I can integrate resume data with other systems and perform analysis.

#### Acceptance Criteria

1. THE Resume_Processor SHALL generate Structured_Data in JSON format for each processed resume
2. THE Structured_Data SHALL include normalized skills as a list
3. THE Structured_Data SHALL include ATS_Score and Semantic_Score
4. THE Structured_Data SHALL include metadata with resume identifier and job category
5. THE Structured_Data SHALL include parsed sections (Skills, Experience, Education, Projects)
6. THE Resume_Processor SHALL validate that generated JSON conforms to a defined schema

### Requirement 10: Feature Engineering

**User Story:** As a data scientist, I want skills converted to numerical features, so that I can train machine learning models.

#### Acceptance Criteria

1. THE Feature_Generator SHALL create a vocabulary of all unique normalized skills across the dataset
2. THE Feature_Generator SHALL convert each resume's skills into a binary feature vector
3. WHEN a skill is present in a resume, THE Feature_Generator SHALL set the corresponding feature value to 1
4. WHEN a skill is absent from a resume, THE Feature_Generator SHALL set the corresponding feature value to 0
5. THE Feature_Generator SHALL output feature vectors with consistent dimensionality across all resumes

### Requirement 11: Job Category Classification

**User Story:** As a recruiter, I want resumes automatically classified by job category, so that I can route candidates to appropriate hiring teams.

#### Acceptance Criteria

1. THE Classifier SHALL train a baseline model using TF-IDF features and Logistic Regression
2. THE Classifier SHALL train a proposed model using skill feature vectors and Random Forest
3. WHEN a resume feature vector is provided, THE Classifier SHALL predict the Job_Category
4. THE Classifier SHALL output a predicted Job_Category label
5. THE Classifier SHALL output prediction confidence scores for each Job_Category

### Requirement 12: Candidate Clustering

**User Story:** As a talent analyst, I want similar candidates grouped together, so that I can identify candidate pools with comparable skill sets.

#### Acceptance Criteria

1. THE Clustering_Engine SHALL apply K-Means clustering to resume feature vectors
2. THE Clustering_Engine SHALL assign each resume to a cluster identifier
3. THE Clustering_Engine SHALL calculate cluster centroids representing typical skill profiles
4. WHEN the number of clusters is specified, THE Clustering_Engine SHALL create that number of clusters

### Requirement 13: Skill Association Mining

**User Story:** As a talent strategist, I want to discover which skills frequently appear together, so that I can understand skill combinations and market trends.

#### Acceptance Criteria

1. THE Association_Miner SHALL apply the Apriori algorithm to discover frequently co-occurring skills
2. WHEN a minimum support threshold is specified, THE Association_Miner SHALL identify skill sets meeting that threshold
3. WHEN a minimum confidence threshold is specified, THE Association_Miner SHALL generate association rules meeting that threshold
4. THE Association_Miner SHALL output association rules in the format "skill_set_A implies skill_set_B"
5. THE Association_Miner SHALL include support, confidence, and lift metrics for each rule

### Requirement 14: Model Performance Evaluation

**User Story:** As a data scientist, I want model performance measured, so that I can compare the proposed system against baseline approaches.

#### Acceptance Criteria

1. THE Evaluation_Module SHALL calculate Macro-F1 score for classification models
2. THE Evaluation_Module SHALL calculate accuracy for classification models
3. THE Evaluation_Module SHALL calculate Silhouette Score for clustering results
4. THE Evaluation_Module SHALL compare baseline model performance against proposed model performance
5. THE Evaluation_Module SHALL output performance metrics in a structured report

### Requirement 15: Fairness Analysis

**User Story:** As a compliance officer, I want fairness metrics across job categories, so that I can ensure the system does not exhibit bias.

#### Acceptance Criteria

1. THE Evaluation_Module SHALL calculate performance metrics separately for each Job_Category
2. THE Evaluation_Module SHALL identify Job_Categories with significantly lower performance metrics
3. THE Evaluation_Module SHALL calculate the variance in performance metrics across Job_Categories
4. THE Evaluation_Module SHALL output a fairness report highlighting performance disparities
5. WHEN performance variance exceeds a threshold, THE Evaluation_Module SHALL flag the system for fairness review
