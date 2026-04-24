#!/bin/bash
# Example usage script for Smart Resume Screening System
# This script demonstrates the complete workflow

set -e  # Exit on error

echo "=========================================="
echo "Smart Resume Screening System - Demo"
echo "=========================================="
echo ""

# Configuration
OUTPUT_DIR="output"
CSV_FILE="archive/Resume/Resume.csv"
PDF_DIR="archive/data/data"
CONFIG="config/config.yaml"

# Create output directory
mkdir -p "$OUTPUT_DIR"

echo "Step 1: Processing CSV data..."
echo "--------------------------------------"
python main.py process-csv \
    --csv-file "$CSV_FILE" \
    --output-dir "$OUTPUT_DIR" \
    --log-level INFO

echo ""
echo "Step 2: Training ML models..."
echo "--------------------------------------"
python main.py train \
    --csv-file "$CSV_FILE" \
    --output-dir "$OUTPUT_DIR" \
    --log-level INFO

echo ""
echo "Step 3: Evaluating models..."
echo "--------------------------------------"
python main.py evaluate \
    --csv-file "$CSV_FILE" \
    --output-dir "$OUTPUT_DIR" \
    --log-level INFO

echo ""
echo "Step 4: Mining skill associations..."
echo "--------------------------------------"
python main.py mine \
    --csv-file "$CSV_FILE" \
    --output-dir "$OUTPUT_DIR" \
    --log-level INFO

echo ""
echo "Step 5: Processing PDF data (sample)..."
echo "--------------------------------------"
# Note: Processing all PDFs takes time, so this is optional
# Uncomment to run full PDF processing
# python main.py process-pdf \
#     --pdf-dir "$PDF_DIR" \
#     --output-dir "$OUTPUT_DIR" \
#     --log-level INFO

echo ""
echo "Step 6: Cross-source validation (sample)..."
echo "--------------------------------------"
# Note: Validation requires both CSV and PDF data
# Uncomment to run validation
# python main.py validate \
#     --csv-file "$CSV_FILE" \
#     --pdf-dir "$PDF_DIR" \
#     --output-dir "$OUTPUT_DIR" \
#     --log-level INFO

echo ""
echo "=========================================="
echo "Demo complete! Check the output directory:"
echo "  $OUTPUT_DIR/"
echo "=========================================="
