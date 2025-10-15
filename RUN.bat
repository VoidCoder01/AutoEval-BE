@echo off
cls
echo.
echo ========================================
echo    AutoEval - Starting Server
echo ========================================
echo.
cd /d "%~dp0"
cd ..
call venv\Scripts\activate
cd AutoEval
echo Starting application...
echo.
python app.py
pause

