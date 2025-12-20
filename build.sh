#!/usr/bin/env bash
# Exit on any error
set -o errexit

# Upgrade pip and install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Collect static files and run migrations
python manage.py collectstatic --noinput
python manage.py migrate