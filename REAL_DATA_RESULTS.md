# Real Data Results

This file summarizes the latest successful run on the Kaggle Resume Dataset using the code currently in this repository.

## Dataset Summary

- CSV resumes: `2484`
- PDF files in archive: `2484`
- Job categories: `24`
- Successfully compared CSV/PDF resumes in validation: `2483`

Commands used:

```bash
python setup_dataset.py
python main.py process-csv --output-dir output
python main.py train --output-dir output
python main.py evaluate --output-dir output
python main.py mine --output-dir output
python main.py validate --output-dir output
```

Generated artifacts:

- `output/models/classifier.pkl`
- `output/models/feature_generator.pkl`
- `output/models/vocabulary.json`
- `output/reports/evaluation_report.json`
- `output/reports/association_rules.json`
- `output/reports/validation_report.json`

## Classification Results

The current real-data run uses the configuration in `config/config.yaml`, including:

- `test_size = 0.2`
- `random_state = 42`

Observed metrics:

| Model | Accuracy | Macro F1 |
| --- | ---: | ---: |
| Baseline: TF-IDF + Logistic Regression | 0.6258 | 0.5468 |
| Proposed: Skill Features + Random Forest | 0.2857 | 0.2301 |

Observation:

- The baseline model outperformed the proposed skill-feature model in the current implementation.

Fairness output for the proposed model:

- Mean per-category F1: `0.2301`
- F1 standard deviation: `0.1837`
- Flagged categories: `ADVOCATE`, `AGRICULTURE`, `ARTS`, `AUTOMOBILE`, `BPO`, `CONSULTANT`

Best proposed-model categories by F1:

- `CHEF`: `0.6531`
- `ACCOUNTANT`: `0.5161`
- `TEACHER`: `0.4364`
- `BUSINESS-DEVELOPMENT`: `0.4314`
- `INFORMATION-TECHNOLOGY`: `0.3939`

## Association Mining Results

Rule count: `2`

Rules discovered:

1. `{state} => {name city}`
   - support: `0.1450`
   - confidence: `0.5854`
   - lift: `2.2952`
2. `{name city} => {state}`
   - support: `0.1450`
   - confidence: `0.5687`
   - lift: `2.2952`

Observation:

- The current association output is dominated by resume header/location artifacts rather than strong skill bundles, so this should be presented as a limitation.

## Cross-Source Validation Results

Observed metrics:

- Samples compared: `2483`
- Text similarity mean: `0.9979`
- Text similarity std: `0.0172`
- Skill overlap mean: `0.7575`
- Skill overlap std: `0.1633`
- Extraction accuracy: `0.8777`

Observation:

- PDF text extraction is very close to the CSV source text.
- Skill extraction is less stable than raw text extraction, which is reflected in the lower skill-overlap score.

## Current Reporting Guidance

If you reference this project in a course report or README, the safest claims are:

- The CLI workflow `process-csv`, `train`, `evaluate`, `mine`, and `validate` runs successfully on the Kaggle dataset.
- The repository currently supports 24 job categories from the Kaggle dataset.
- The baseline classifier outperformed the proposed skill-feature classifier in the latest real-data run.
- Cross-source extraction validation produced strong text similarity and moderate skill overlap.
- Clustering is implemented as a module but is not exposed as a CLI command.
- The scoring engine exists in code, but normal CLI processing still saves `scores: null` in structured resumes.
