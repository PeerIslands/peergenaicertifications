#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

if [ ! -d .venv ]; then
  python3 -m venv .venv
fi

source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

echo "Creating directories..."
mkdir -p uploads chroma_db app/static app/templates

echo "Done. Activate with: source .venv/bin/activate"
echo "Run with: uvicorn app.main:app --reload --port 8000"


