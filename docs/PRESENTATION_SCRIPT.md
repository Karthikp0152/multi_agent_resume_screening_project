# Final Presentation Script

Target length: under 5 minutes.

## 1. Intro

Hi everyone, I am Luan Nguyen. Our project is a Smart Resume Screening and Skill Mining System for CSE 572. The goal is to take resumes from a real Kaggle dataset, extract structured information, normalize skills, run machine learning models, and analyze patterns across candidates using data mining techniques.

## 2. Agenda

I will cover five things today: the problem we are solving, the system architecture, the core agent-style modules, a short demo of the local dashboard, and the final results from classification, CSV/PDF validation, and association mining.

## 3. Problem Statement

Resume screening is a common problem for both recruiters and job applicants. Many systems rely heavily on keyword matching, so small wording differences can matter too much. For example, one resume might say "ReactJS" while another says "React," even though they mean almost the same thing.

Another issue is format. Resumes can come from CSV text, PDFs, or different templates, and that makes extraction inconsistent. Our project tries to turn messy resume data into structured, analyzable data. Instead of only asking whether a resume matches a keyword, we extract skills, normalize them, classify job categories, mine skill patterns, cluster resumes, and validate whether PDF extraction matches the CSV ground truth.

## 4. System Architecture

The system is built as a modular Python pipeline with both a command-line interface and a local FastAPI web dashboard. The CLI is still the source of truth, and the dashboard runs the same commands and displays the saved reports.

The pipeline supports CSV resumes and PDF resume folders. It loads the data, parses resume sections, extracts and normalizes skills, builds features, trains models, evaluates results, mines associations, performs clustering, and validates CSV versus PDF extraction.

The architecture is multi-agent-style in the sense that each module has a specific responsibility, but these are in-process pipeline agents rather than separate autonomous services.

## 5. Core Features - Agents

The first agent is the section parsing agent. It breaks resumes into sections like skills, education, experience, and projects.

The second is the skill extraction agent. It uses spaCy and resume heuristics to find explicit skills listed by the candidate and implicit skills from experience or project descriptions.

The third is the skill normalization agent. It cleans variations like abbreviations or alternate spellings so similar skills map to a consistent form.

The fourth is the classification agent. It trains two models: a TF-IDF plus Logistic Regression baseline, and a proposed hybrid model that combines raw text TF-IDF features with normalized skill features.

The fifth group is the analysis agents: association mining, clustering, and validation. These help us understand skill co-occurrence, resume groupings, and whether the PDF pipeline produces results close to the CSV data.

## 6. Project Demo

For the demo, I will open the local dashboard. The first page shows whether the dataset and reports are available, plus summary cards for classification, association mining, clustering, and validation.

Then I will show the pipeline controls. From the dashboard, we can run the same commands as the CLI: process CSV, process PDF, train, evaluate, mine, cluster, and validate. When a job runs, the dashboard highlights the active process and shows a loading animation and logs.

Finally, I will open the reports page, which displays the saved metrics and results from the real dataset without committing the generated output files to GitHub.

## 7. Results - F1 Scores Baseline vs. Hybrid

For classification, the baseline model performed better than our proposed hybrid model.

The baseline, which uses raw resume text with TF-IDF and Logistic Regression, reached 0.6258 accuracy and 0.5468 Macro F1.

The proposed hybrid model, which combines text TF-IDF with normalized skill features, reached 0.4165 accuracy and 0.3685 Macro F1.

The main finding is that our normalized skills are useful for analysis, but they did not improve classification in the current model. Full resume text still carries stronger category information than the extracted skill features alone. This is important because it shows where the project needs improvement instead of claiming the new model is automatically better.

## 8. Results Continued - Validation and Association Mining

For CSV/PDF validation, we compared 2,483 matched resume pairs. The text similarity was 0.9979, which means the PDF extraction preserved the raw text very well. The skill overlap was 0.7575, and the overall extraction accuracy was 0.8777.

This tells us the PDF pipeline is mostly reliable, but skill extraction still loses some information compared with raw text.

For association mining, the system found 21 frequent itemsets, but zero final association rules at the configured thresholds of 0.1 support and 0.5 confidence. After cleaning header and contact artifacts, we did not get strong enough skill rules. That is useful because it shows the dataset has frequent skills, but not enough consistent co-occurrence patterns under our current thresholds.

## 9. Thank You

To summarize, our project delivers a working resume processing pipeline, a CLI, a local dashboard, real dataset results, classification, clustering, mining, and CSV/PDF validation. The system is functional, but the results also show clear limitations, especially around skill extraction and hybrid feature design.

Thank you.
