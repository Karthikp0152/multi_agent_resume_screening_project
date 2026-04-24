# Implementation Plan: Smart Resume Screening System

## Overview

This implementation plan breaks down the Smart Resume Screening System into discrete, actionable coding tasks. The system will be built incrementally, starting with core data models and basic processing, then adding NLP capabilities, ML analysis, and evaluation. Each task builds on previous work to ensure continuous integration and validation.

The implementation follows a bottom-up approach: foundational components first (data models, text extraction), then processing layers (parsing, extraction, normalization), followed by analysis components (scoring, feature engineering), and finally ML capabilities (classification, clustering, association mining) with comprehensive evaluation.

## Tasks

- [x] 1. Set up project structure and dependencies
  - Create directory structure: `src/`, `tests/`, `config/`, `data/`, `models/`
  - Create `requirements.txt` with all dependencies: pdfplumber, pypdf, spacy, sentence-transformers, rapidfuzz, scikit-learn, mlxtend, pandas, numpy, pytest
  - Create `setup.py` or `pyproject.toml` for package configuration
  - Set up logging configuration with structured logging
  - Create configuration files: `config/skill_aliases.json`, `config/config.yaml`, `config/job_categories.json`
  - Initialize pytest test structure
  - _Requirements: All (foundational setup)_

- [x] 2. Implement core data models and schemas
  - [x] 2.1 Create data model classes
    - Implement `ResumeSections` dataclass with skills, experience, education, projects, raw_text fields
    - Implement `SkillSet` dataclass with explicit_skills, implicit_skills lists and all_skills() method
    - Implement `Scores` dataclass with ats_score and semantic_score fields
    - Implement `ResumeMetadata` dataclass with file_path, processed_date, processing_time_ms
    - Implement `StructuredResume` dataclass with all fields and to_json()/from_json() methods
    - Implement `ProcessorConfig` and `MLConfig` dataclasses
    - _Requirements: 9.1, 9.2, 9.3, 9.4, 9.5_

  - [x] 2.2 Write unit tests for data models
    - Test JSON serialization and deserialization
    - Test dataclass field validation
    - Test SkillSet.all_skills() method
    - _Requirements: 9.6_

- [x] 3. Implement Text Extractor component
  - [x] 3.1 Create TextExtractor class with PDF and text extraction
    - Implement `extract_from_pdf()` using pdfplumber with pypdf fallback
    - Implement `extract_from_text()` for plain text files
    - Implement `clean_text()` with regex-based special character removal and whitespace normalization
    - Implement `validate_format()` to check supported file formats
    - Add error handling for FileNotFoundError, PDFExtractionError, UnsupportedFormatError
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 1.1, 1.2, 1.3_

  - [x] 3.2 Write unit tests for TextExtractor
    - Test PDF extraction with sample PDF files
    - Test text file loading
    - Test text cleaning with special characters and whitespace
    - Test format validation for supported and unsupported formats
    - Test fallback mechanism when pdfplumber fails
    - Test error handling for missing files
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5_

- [x] 4. Implement Section Parser component
  - [x] 4.1 Create SectionParser class with pattern-based section detection
    - Implement `__init__()` with regex patterns for Skills, Experience, Education, Projects sections
    - Implement `parse_sections()` to identify and extract all sections using case-insensitive regex
    - Implement `extract_section()` to extract specific section by name
    - Handle missing sections by returning empty strings
    - Return ResumeSections dataclass with all parsed sections
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 3.6_

  - [x] 4.2 Write unit tests for SectionParser
    - Test section detection with various header formats
    - Test case-insensitive matching
    - Test handling of missing sections
    - Test section boundary detection
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5_

- [x] 5. Checkpoint - Ensure basic extraction pipeline works
  - Ensure all tests pass, ask the user if questions arise.

- [x] 6. Implement Skill Extractor component
  - [x] 6.1 Create SkillExtractor class with NLP-based extraction
    - Implement `__init__()` to load spaCy model (en_core_web_sm)
    - Implement `extract_explicit_skills()` to extract skills from Skills section using NER and noun phrase extraction
    - Implement `extract_implicit_skills()` to infer skills from Experience and Projects sections using NER
    - Implement `extract_all_skills()` to extract both explicit and implicit skills
    - Return SkillSet dataclass with separated explicit and implicit skills
    - Add error handling for ModelLoadError and SkillExtractionError
    - _Requirements: 4.1, 4.2, 4.3, 4.4, 5.1, 5.2, 5.3, 5.4_

  - [x] 6.2 Write unit tests for SkillExtractor
    - Test explicit skill extraction from Skills sections
    - Test implicit skill extraction from Experience and Projects
    - Test distinction between explicit and implicit skills
    - Test handling of empty sections
    - Test error handling for model loading failures
    - _Requirements: 4.1, 4.2, 4.3, 4.4, 5.1, 5.2, 5.3, 5.4_

- [x] 7. Implement Skill Normalizer component
  - [x] 7.1 Create SkillNormalizer class with fuzzy matching
    - Implement `__init__()` with alias dictionary loading and fuzzy threshold configuration
    - Implement `load_alias_dictionary()` to load skill aliases from JSON file
    - Implement `normalize_skill()` with exact match, fuzzy match (RapidFuzz), and fallback logic
    - Implement `normalize_skills()` to normalize list of skills
    - Use RapidFuzz with threshold of 85% for fuzzy matching
    - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5_

  - [x] 7.2 Write unit tests for SkillNormalizer
    - Test exact alias dictionary matches
    - Test fuzzy matching with various similarity thresholds
    - Test handling of skills not in dictionary
    - Test case normalization
    - Test alias dictionary loading
    - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5_

- [x] 8. Implement Scoring Engine component
  - [x] 8.1 Create ScoringEngine class with ATS and semantic scoring
    - Implement `__init__()` to load sentence-transformers model (all-MiniLM-L6-v2)
    - Implement `calculate_ats_score()` using set intersection for keyword matching
    - Implement `calculate_semantic_score()` using sentence embeddings and cosine similarity
    - Implement `calculate_both_scores()` to return both scores
    - Handle empty skill sets by returning 0.0 scores
    - Add error handling for EmbeddingError with fallback to ATS only
    - _Requirements: 7.1, 7.2, 7.3, 7.4, 8.1, 8.2, 8.3, 8.4_

  - [x] 8.2 Write unit tests for ScoringEngine
    - Test ATS score calculation with various skill overlaps
    - Test semantic score calculation with embeddings
    - Test handling of empty skill sets
    - Test score boundary conditions (0-100 for ATS, 0-1 for semantic)
    - Test error handling for embedding failures
    - _Requirements: 7.1, 7.2, 7.3, 7.4, 8.1, 8.2, 8.3, 8.4_

- [x] 9. Implement Resume Processor orchestrator with dual data source support
  - [x] 9.1 Create ResumeProcessor class to orchestrate pipeline with CSV and PDF support
    - Implement `__init__()` to initialize all component dependencies (TextExtractor, SectionParser, SkillExtractor, SkillNormalizer, ScoringEngine)
    - Implement `process_resume()` to orchestrate full pipeline for single resume (PDF or text)
    - Implement `process_batch()` to process all resumes in a directory
    - Implement `load_from_archive()` to load resumes organized by job category folders (PDF files)
    - Implement `load_from_csv()` to load resume data from CSV file with ID, Resume_str, Resume_html, Category columns
    - Implement `process_csv_data()` to process CSV resume entries (skip PDF extraction, use Resume_str directly)
    - Generate StructuredResume with all fields populated
    - Add comprehensive error handling and logging
    - Track processing time for metadata
    - _Requirements: 1.1, 1.2, 1.4, 9.1, 9.2, 9.3, 9.4, 9.5, 9.6_

  - [x] 9.2 Add CSV data validation capabilities
    - Implement `validate_csv_extraction()` to compare PDF extraction results against CSV Resume_str data
    - Implement `cross_validate_data_sources()` to identify discrepancies between PDF and CSV text
    - Generate validation report showing extraction accuracy metrics
    - _Requirements: 1.1, 1.2, 2.1, 2.2, 2.3_

  - [x] 9.3 Write integration tests for ResumeProcessor
    - Test end-to-end processing from PDF to StructuredResume JSON
    - Test CSV data loading and processing pipeline
    - Test batch processing of multiple resumes from both sources
    - Test archive loading with job category organization
    - Test CSV validation against PDF extraction
    - Test error handling and recovery for both data sources
    - _Requirements: 1.1, 1.2, 1.4, 9.1, 9.2, 9.3, 9.4, 9.5, 9.6_

- [x] 10. Checkpoint - Ensure complete extraction pipeline works
  - Ensure all tests pass, ask the user if questions arise.

- [x] 11. Implement Feature Generator component with dual data source support
  - [x] 11.1 Create FeatureGenerator class for ML feature engineering with CSV and PDF data
    - Implement `build_vocabulary()` to collect all unique normalized skills from dataset (prioritize CSV data)
    - Implement `generate_feature_vector()` to convert skills to binary vector based on vocabulary
    - Implement `generate_feature_matrix()` to create feature matrix for all resumes
    - Implement `load_csv_features()` to generate features directly from CSV Resume_str data
    - Implement `load_pdf_features()` to generate features from PDF extraction pipeline
    - Use numpy arrays for efficient computation
    - Ensure consistent dimensionality across all feature vectors from both sources
    - _Requirements: 10.1, 10.2, 10.3, 10.4, 10.5_

  - [x] 11.2 Write unit tests for FeatureGenerator
    - Test vocabulary building from multiple resumes (CSV and PDF sources)
    - Test binary vector generation for both data sources
    - Test consistent dimensionality across resumes from different sources
    - Test handling of unseen skills
    - Test CSV vs PDF feature vector comparison
    - _Requirements: 10.1, 10.2, 10.3, 10.4, 10.5_

- [-] 12. Implement Classifier component with CSV-primary training
  - [x] 12.1 Create Classifier class with baseline and proposed models using CSV data
    - Implement `__init__()` to initialize baseline (TF-IDF + Logistic Regression) and proposed (skill features + Random Forest) models
    - Implement `train_baseline()` with TfidfVectorizer and LogisticRegression (C=1.0, max_iter=1000, multi_class='multinomial') using CSV Resume_str data
    - Implement `train_proposed()` with RandomForestClassifier (n_estimators=100, max_depth=20, min_samples_split=5, random_state=42) using CSV-derived skill features
    - Implement `predict()` to predict job categories for given model type
    - Implement `predict_proba()` to return prediction confidence scores
    - Implement `validate_on_pdf_data()` to test trained models on PDF-extracted features
    - _Requirements: 11.1, 11.2, 11.3, 11.4, 11.5_

  - [x] 12.2 Write unit tests for Classifier
    - Test baseline model training and prediction on CSV data
    - Test proposed model training and prediction on CSV-derived features
    - Test probability output format
    - Test handling of unknown categories
    - Test cross-validation between CSV-trained models and PDF-extracted features
    - _Requirements: 11.1, 11.2, 11.3, 11.4, 11.5_

- [-] 13. Implement Clustering Engine component
  - [x] 13.1 Create ClusteringEngine class with K-Means
    - Implement `__init__()` with configurable number of clusters (default 10)
    - Implement `fit_clusters()` using KMeans with k-means++ initialization
    - Implement `get_cluster_centroids()` to return cluster centroids
    - Implement `get_cluster_profiles()` to identify top skills per cluster based on centroid values
    - _Requirements: 12.1, 12.2, 12.3, 12.4_

  - [x] 13.2 Write unit tests for ClusteringEngine
    - Test K-Means clustering with various k values
    - Test centroid calculation
    - Test cluster profile generation
    - Test handling of edge cases (k > n_samples)
    - _Requirements: 12.1, 12.2, 12.3, 12.4_

- [-] 14. Implement Association Miner component
  - [x] 14.1 Create AssociationMiner class with Apriori algorithm
    - Implement `__init__()` with min_support (default 0.1) and min_confidence (default 0.5) thresholds
    - Implement `mine_frequent_itemsets()` using mlxtend.frequent_patterns.apriori
    - Implement `generate_rules()` using mlxtend.frequent_patterns.association_rules with lift calculation
    - Implement `mine_associations()` to transform resumes to transactions and run complete pipeline
    - Return AssociationRule dataclass with antecedents, consequents, support, confidence, lift
    - _Requirements: 13.1, 13.2, 13.3, 13.4, 13.5_

  - [x] 14.2 Write unit tests for AssociationMiner
    - Test frequent itemset discovery
    - Test rule generation with support/confidence thresholds
    - Test lift calculation
    - Test handling of sparse transactions
    - _Requirements: 13.1, 13.2, 13.3, 13.4, 13.5_

- [x] 15. Checkpoint - Ensure ML pipeline works
  - Ensure all tests pass, ask the user if questions arise.

- [-] 16. Implement Evaluation Module component with dual data source validation
  - [x] 16.1 Create EvaluationModule class for performance and fairness analysis across data sources
    - Implement `evaluate_classification()` using sklearn.metrics for accuracy and macro-F1 score
    - Implement `evaluate_clustering()` using sklearn.metrics.silhouette_score
    - Implement `compare_models()` to compare baseline vs proposed model performance
    - Implement `analyze_fairness()` to calculate per-category F1 scores, variance, and flag disparities
    - Implement `evaluate_extraction_pipeline()` to validate PDF extraction accuracy against CSV ground truth
    - Implement `cross_source_validation()` to compare model performance on CSV vs PDF-derived features
    - Generate structured reports for classification, clustering, comparison, fairness, and extraction validation
    - _Requirements: 14.1, 14.2, 14.3, 14.4, 14.5, 15.1, 15.2, 15.3, 15.4, 15.5_

  - [x] 16.2 Write unit tests for EvaluationModule
    - Test accuracy and F1 score calculations
    - Test silhouette score calculation
    - Test fairness analysis across categories
    - Test variance calculation and flagging logic
    - Test extraction pipeline validation metrics
    - Test cross-source performance comparison
    - _Requirements: 14.1, 14.2, 14.3, 14.4, 14.5, 15.1, 15.2, 15.3, 15.4, 15.5_

- [-] 17. Create main execution script and CLI with dual data source support
  - [x] 17.1 Create main.py with CLI interface for CSV and PDF processing
    - Implement command-line argument parsing for input directory, CSV file path, output directory, config file
    - Implement pipeline execution: load config, process resumes from both sources, train models, evaluate, generate reports
    - Add commands for: process-csv (extract and structure from CSV), process-pdf (extract from PDFs), train (train ML models on CSV data), evaluate (run evaluation), mine (association mining), validate (cross-source validation)
    - Save outputs: structured JSONs, trained models, evaluation reports, association rules, validation reports
    - Add progress logging and error reporting for both data sources
    - _Requirements: All (integration)_

  - [x] 17.2 Write integration tests for main execution with dual sources
    - Test end-to-end pipeline from CSV to evaluation reports
    - Test end-to-end pipeline from PDF archive to evaluation reports
    - Test cross-source validation pipeline
    - Test CLI argument parsing for both data sources
    - Test output file generation for all processing modes
    - _Requirements: All (integration)_

- [x] 18. Create sample configuration and test data for dual sources
  - [x] 18.1 Create sample configuration files
    - Create `config/skill_aliases.json` with common skill aliases (js→JavaScript, ml→Machine Learning, etc.)
    - Create `config/config.yaml` with default system configuration including CSV and PDF processing options
    - Create `config/job_categories.json` with list of valid job categories from both CSV and PDF archive
    - _Requirements: All (configuration)_

  - [x] 18.2 Create test fixtures and sample data for both sources
    - Create sample PDF resumes for testing extraction pipeline
    - Create sample CSV entries for testing CSV processing pipeline
    - Create sample text resumes for testing
    - Create expected output JSONs for validation from both sources
    - Create sample job requirements for scoring tests
    - Create validation datasets linking PDF files to CSV entries where possible
    - _Requirements: All (testing)_

- [x] 19. Add documentation and usage examples for dual data source system
  - [x] 19.1 Create README.md with installation and usage instructions for both data sources
    - Document installation steps (virtual environment, dependencies, spaCy model download)
    - Document CLI usage with examples for CSV processing, PDF processing, and cross-validation
    - Document configuration options for both data sources
    - Document output formats and data source comparison features
    - Include examples of processing CSV data vs PDF archive data
    - _Requirements: All (documentation)_

  - [x] 19.2 Create API documentation for dual source capabilities
    - Document all public classes and methods with docstrings
    - Create examples for each component showing CSV and PDF processing
    - Document data models and schemas for both data sources
    - Document validation and cross-source comparison features
    - _Requirements: All (documentation)_

- [x] 20. Final checkpoint - Run complete system test with dual data sources
  - Process sample resumes from CSV file (primary training data)
  - Process sample resumes from PDF archive directory (pipeline validation)
  - Train classification models on CSV data and evaluate performance
  - Validate trained models on PDF-extracted features
  - Run clustering and association mining on both data sources
  - Generate fairness analysis report across both data sources
  - Generate extraction pipeline validation report comparing PDF extraction vs CSV ground truth
  - Verify all outputs are generated correctly for both processing modes
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- Tasks marked with `*` are optional testing tasks and can be skipped for faster MVP
- Each task references specific requirements for traceability
- The implementation uses Python 3.9+ as specified in the design document
- **Dual Data Source Strategy**: CSV data (archive/Resume/Resume.csv) serves as primary training source for faster processing and pre-extracted text, while PDF files (archive/data/data/) validate the extraction pipeline
- **CSV Data Structure**: ID, Resume_str (plain text), Resume_html (formatted), Category (job classification)
- **PDF Data Structure**: Organized by job category folders (ACCOUNTANT, ADVOCATE, AGRICULTURE, APPAREL, etc.)
- **Training Approach**: Use CSV Resume_str for model training, then validate on PDF extraction results
- **Validation Strategy**: Compare PDF extraction accuracy against CSV ground truth where possible
- All ML models use scikit-learn and related libraries as specified
- NLP processing uses spaCy and sentence-transformers as specified
- Checkpoints ensure incremental validation at key milestones
- Focus on building working components incrementally rather than completing all features at once
- Integration tests validate end-to-end functionality for both data sources
- Configuration files enable easy customization without code changes
- Cross-source validation ensures extraction pipeline reliability
