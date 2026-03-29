#!/bin/bash
# Quick setup script for this application

set -e

echo "==> Creating virtual environment..."b
python3.12 -m venv env
source env/bin/activate

echo "==> Installing dependencies..."
pip install -e .