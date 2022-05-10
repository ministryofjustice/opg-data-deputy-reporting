#!/bin/sh
echo "=== Listing Installed Package Versions ==="
pip freeze
echo "=== Checking coding style using black ==="
black lambda_functions
echo "=== Linting using flake8 ==="
flake8 --extend-ignore=Q000,E501 lambda_functions/v2/functions
echo "=== Running Unit Tests ==="
python -m pytest lambda_functions/v2/
