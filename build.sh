#!/usr/bin/env bash
# exit on error
set -o errexit

pip install -r requirements.txt

python manage.py collectstatic --no-input

# Wait for database to be ready
echo "Waiting for database to be ready..."
python manage.py migrate --run-syncdb 