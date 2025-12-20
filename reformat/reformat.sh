#!/bin/bash

set -e

echo "=========================================="
echo "Installing dependencies..."
echo "=========================================="
pip install --upgrade pip
pip install .[dev]

echo ""
echo "=========================================="
echo "Running Black (code formatter)..."
echo "=========================================="
black create-or-restore-volume/ snapshot-and-destroy-volume/

echo ""
echo "=========================================="
echo "Running docformatter (docstring formatter)..."
echo "=========================================="
# First check
docformatter \
  --check \
  --recursive \
  --wrap-summaries 72 \
  --wrap-descriptions 72 \
  create-or-restore-volume/ \
  snapshot-and-destroy-volume/

# Then apply changes
docformatter \
  --in-place \
  --recursive \
  --wrap-summaries 72 \
  --wrap-descriptions 72 \
  create-or-restore-volume/ \
  snapshot-and-destroy-volume/

echo ""
echo "=========================================="
echo "Running isort (import sorter)..."
echo "=========================================="
isort create-or-restore-volume/ snapshot-and-destroy-volume/

echo ""
echo "=========================================="
echo "Formatting complete!"
echo "=========================================="
