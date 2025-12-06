#!/usr/bin/env bash
set -o errexit

echo "Installing dependencies..."
pip install -r requirements.txt

echo "Running migrations..."
python manage.py makemigrations accounts --no-input
python manage.py makemigrations patients --no-input
python manage.py makemigrations vitals --no-input
python manage.py makemigrations medications --no-input
python manage.py makemigrations appointments --no-input
python manage.py makemigrations reports --no-input
python manage.py makemigrations notifications --no-input
python manage.py migrate --no-input

echo "Collecting static files..."
python manage.py collectstatic --no-input

echo "Creating sample data..."
python setup_data.py
