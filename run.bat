@echo off
echo Starting Motion Controller...
echo.
python src\main.py
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo Error: Failed to start application.
    echo Make sure all dependencies are installed: pip install -r requirements.txt
)
pause

