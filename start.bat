@echo off
echo ========================================
echo    Ruua Backend - Embedded Finance
echo ========================================
echo.

echo Installing dependencies...
pip install -r requirements.txt

echo.
echo Starting Ruua API server...
echo API will be available at: http://localhost:8000
echo Documentation: http://localhost:8000/docs
echo.

python main.py

pause
