#!/usr/bin/env bash
# exit on error
set -o errexit


# Install dependencies
pip install -r requirements.txt

cd helpdesk

# Run migrations first
python manage.py migrate

# Collect static files (including drf-yasg)
python manage.py collectstatic --no-input --clear