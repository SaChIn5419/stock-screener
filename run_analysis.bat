@echo off
REM Automated Fundamental Analyzer Launcher
REM Uses the hardcoded Anaconda Python path to avoid environment issues.

set PYTHON_EXE="C:\Users\Sachin D B\anaconda3\python.exe"

echo Checking if Python is accessible...
if not exist %PYTHON_EXE% (
    echo [ERROR] Python not found at %PYTHON_EXE%
    echo Please check your Anaconda installation path.
    pause
    exit /b
)

echo.
echo ===================================================
echo   Automated Stock Fundamental Analyzer
echo ===================================================
echo 1. Analyze Nifty 50 (Fast)
echo 2. Analyze All NSE Stocks (Slow)
echo.

set /p choice="Enter choice (1 or 2): "

if "%choice%"=="1" (
    %PYTHON_EXE% main.py --mode nifty50
) else if "%choice%"=="2" (
    %PYTHON_EXE% main.py --mode all
) else (
    echo Invalid choice. Defaulting to Nifty 50.
    %PYTHON_EXE% main.py --mode nifty50
)

echo.
echo Analysis complete. check the 'reports' folder.
pause
