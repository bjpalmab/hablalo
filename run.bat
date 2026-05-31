@echo off
REM Run script for hablalo

echo Activating virtual environment...
call venv\Scripts\activate.bat

echo Starting application...
python main.py

pause
