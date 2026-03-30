#!/bin/bash
# Quick setup script for this application

set -e

echo "==> Creating virtual environment..."
python -m venv env
source env/bin/activate

echo "==> Installing dependencies..."
pip install -e .

echo "==> Installing frontend dependencies..."
cd frontend
npm install
cd ..

echo "==> Setup complete!"
echo "    To run the backend:  source env/bin/activate && uvicorn src.api:app --reload --port 8000"
echo "    To run the frontend: cd frontend && npm run dev"