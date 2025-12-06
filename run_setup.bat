@echo off
echo ========================================
echo Healthcare Portal Setup
echo ========================================

echo Installing dependencies...
pip install -r requirements.txt

echo.
echo Running migrations...
python manage.py makemigrations accounts
python manage.py makemigrations patients
python manage.py makemigrations vitals
python manage.py makemigrations medications
python manage.py makemigrations appointments
python manage.py makemigrations reports
python manage.py makemigrations notifications
python manage.py migrate

echo.
echo Creating sample data...
python setup_data.py

echo.
echo ========================================
echo Setup Complete!
echo ========================================
echo.
echo To start the server, run:
echo   python manage.py runserver
echo.
echo Then open http://127.0.0.1:8000 in your browser
echo.
pause
