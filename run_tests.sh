#!/bin/bash

echo "Running pytest with coverage..."
pytest tests/ --cov=. --cov-report=html --cov-report=term-missing --cov-config=.coveragerc

echo ""
echo "Test execution completed!"
echo "Coverage report generated in htmlcov/index.html"

