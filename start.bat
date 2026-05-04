@echo off
title Dynamic Resource Allocator

echo =========================================
echo   Starting Dynamic Resource Allocator
echo =========================================
echo.

echo [1/3] Checking dependencies...
pip install -r requirements.txt --quiet

echo [2/3] Starting the Backend Engine...
:: Start the backend engine in a new, separate command prompt window
start "Backend Engine" cmd /c "title Backend Engine & python -m src.main"

:: Wait a couple of seconds to make sure the backend starts and creates state files
timeout /t 2 /nobreak >nul

echo [3/3] Starting the Control Center Dashboard...
:: Run the Streamlit dashboard in this window
python -m streamlit run dashboard/app.py
