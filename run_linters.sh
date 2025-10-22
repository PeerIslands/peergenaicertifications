#!/bin/bash

echo "Running linters..."
echo ""

echo "=== Running flake8 ==="
flake8 . --exclude=venv,tests --statistics || true
echo ""

echo "=== Running pylint ==="
pylint *.py --rcfile=.pylintrc || true
echo ""

echo "=== Running black (check only) ==="
black --check --exclude venv . || true
echo ""

echo "Linting completed!"

