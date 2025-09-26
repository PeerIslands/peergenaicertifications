#!/bin/bash

# PDF Ingestion Tool - Activation Script
echo "PDF Ingestion Tool - Activating Environment"
echo "=========================================="

# Activate virtual environment
source venv/bin/activate

echo "✓ Virtual environment activated"
echo "✓ Python path: $(which python)"
echo "✓ Pip path: $(which pip)"
echo ""
echo "Available commands:"
echo "  python pdf_ingestion_tool.py  - Run the main ingestion tool"
echo "  python test_installation.py   - Test the installation"
echo "  python example_usage.py       - Run example usage"
echo ""
echo "To deactivate, run: deactivate"
echo ""

# Keep the shell active
exec bash
