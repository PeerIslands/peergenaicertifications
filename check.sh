#!/bin/bash

set -e

echo "=================================="
echo "  Running All Code Quality Checks"
echo "=================================="
echo ""

FAILED=0

echo "📋 [1/4] Checking code formatting with Black..."
echo "--------------------------------------"
if black --check --exclude venv . 2>&1; then
    echo "✅ Black formatting check passed"
else
    echo "❌ Black formatting issues found"
    echo "   Run: black . --exclude venv"
    FAILED=$((FAILED + 1))
fi
echo ""

echo "🔍 [2/4] Running Flake8 linter..."
echo "--------------------------------------"
if flake8 . --exclude=venv,tests --statistics 2>&1; then
    echo "✅ Flake8 check passed"
else
    echo "❌ Flake8 found issues"
    FAILED=$((FAILED + 1))
fi
echo ""

echo "🔎 [3/4] Running Pylint..."
echo "--------------------------------------"
if pylint *.py --rcfile=.pylintrc --exit-zero 2>&1 | tee /tmp/pylint_output.txt; then
    SCORE=$(grep "Your code has been rated" /tmp/pylint_output.txt | awk '{print $7}' | cut -d'/' -f1 || echo "0")
    if (( $(echo "$SCORE >= 8.0" | bc -l) )); then
        echo "✅ Pylint check passed (Score: $SCORE/10)"
    else
        echo "⚠️  Pylint score is low (Score: $SCORE/10)"
        FAILED=$((FAILED + 1))
    fi
else
    echo "❌ Pylint found critical issues"
    FAILED=$((FAILED + 1))
fi
rm -f /tmp/pylint_output.txt
echo ""

echo "🧪 [4/4] Running pytest with coverage..."
echo "--------------------------------------"
if pytest tests/ --cov=. --cov-report=term-missing --cov-report=html --cov-config=.coveragerc -v 2>&1; then
    echo "✅ All tests passed"
else
    echo "❌ Some tests failed"
    FAILED=$((FAILED + 1))
fi
echo ""

echo "=================================="
echo "  Summary"
echo "=================================="
if [ $FAILED -eq 0 ]; then
    echo "✅ All checks passed successfully!"
    echo ""
    echo "📊 Coverage report: htmlcov/index.html"
    echo ""
    echo "🎉 Your code is ready!"
    exit 0
else
    echo "❌ $FAILED check(s) failed"
    echo ""
    echo "Please fix the issues above and run again."
    exit 1
fi

