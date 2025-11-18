#!/bin/bash

# Cleanup script for BacDive Assay Metadata project

echo "Cleaning up duplicate and unnecessary files..."

# Remove duplicate extraction directory
if [ -d "data/extract" ]; then
    echo "  ✓ Removing data/extract/ (duplicate)"
    rm -rf data/extract
fi

# Remove __pycache__ directories
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
echo "  ✓ Removed Python cache files"

# Remove .pyc files
find . -type f -name "*.pyc" -delete 2>/dev/null
echo "  ✓ Removed .pyc files"

echo ""
echo "✨ Cleanup complete!"
echo ""
echo "Remaining files in data/:"
ls -lh data/

