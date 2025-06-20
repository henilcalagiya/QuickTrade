#!/usr/bin/env bash
# exit on error
set -o errexit

echo "Installing dependencies..."
pip install -r requirements.txt

echo "Checking environment variables..."
echo "DATABASE_URL exists: $([ -n "$DATABASE_URL" ] && echo "YES" || echo "NO")"
echo "DEBUG: $DEBUG"

echo "Creating sessions directory..."
mkdir -p sessions

echo "Testing database connection..."
# Add retry logic for database connection
max_attempts=5
attempt=1
while [ $attempt -le $max_attempts ]; do
    echo "Database connection attempt $attempt of $max_attempts..."
    if python manage.py check --database default; then
        echo "Database connection successful!"
        break
    else
        echo "Database connection failed. Attempt $attempt of $max_attempts"
        if [ $attempt -eq $max_attempts ]; then
            echo "All database connection attempts failed. Continuing with build..."
        else
            echo "Waiting 10 seconds before retry..."
            sleep 10
        fi
    fi
    attempt=$((attempt + 1))
done

echo "Running database migrations..."
python manage.py migrate --noinput

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Build completed successfully!" 