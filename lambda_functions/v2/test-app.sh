#!/bin/sh
#echo "=== Listing Installed Package Versions ==="
#python -m pip freeze
#echo "=== Checking coding style using black ==="
#python -m black lambda_functions
#echo "=== Linting using flake8 ==="
#python -m flake8 --extend-ignore=Q000,E501 lambda_functions/v2/functions
echo "=== Running Unit Tests ==="
#pwd
#ls -alt
cd lambda_functions/v2/tests
python -m pytest
#-k test_checklist_put routes/test_checklist_endpoint.py
