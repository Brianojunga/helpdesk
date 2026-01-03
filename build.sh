#!/usr/bin/env bash
# exit on error
set -o errexit


# Install dependencies
pip install -r requirements.txt

cd helpdesk
# Collect static files for production
python manage.py collectstatic --no-input

# Run migrations
python manage.py migrate