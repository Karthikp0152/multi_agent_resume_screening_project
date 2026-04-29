# Report Figures

These PNG files were generated from the real local pipeline outputs in
`output/reports/`.

Regenerate the figures after rerunning the pipeline:

```bash
python scripts/generate_report_plots.py --reports-dir output/reports --output-dir docs/figures
```

## Figure Captions

- `model_metrics.png`: Baseline TF-IDF + Logistic Regression outperforms the proposed hybrid model on both accuracy and macro F1.
- `category_f1_scores.png`: Per-category F1 scores show that several categories remain difficult for the proposed model, especially low-sample or ambiguous classes.
- `validation_metrics.png`: PDF text extraction is highly similar to the CSV source text, while skill overlap is lower and more variable.
- `cluster_size_distribution.png`: PDF clustering is exploratory and imbalanced, with one dominant cluster and several singleton clusters.
- `association_summary.png`: Apriori found frequent itemsets, but no association rules met the configured confidence threshold.
