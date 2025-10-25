@echo off
REM Resume Builder Backend Startup Script for Windows

echo 🚀 Starting Resume Builder Backend...

REM Run Python version checker
echo 🔍 Checking Python version...
python check_python.py
if errorlevel 1 (
    echo ❌ Python version check failed. Please install Python 3.11+ first.
    pause
    exit /b 1
)

REM Check if Python 3.11 is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed. Please install Python 3.11 or higher.
    pause
    exit /b 1
)

REM Check Python version
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo Current Python version: %PYTHON_VERSION%

REM Check if it's Python 3.11+
python -c "import sys; exit(0 if sys.version_info >= (3, 11) else 1)" >nul 2>&1
if errorlevel 1 (
    echo ❌ Python 3.11 or higher is required. Current version: %PYTHON_VERSION%
    echo    Please install Python 3.11 or higher.
    pause
    exit /b 1
)

REM Check if pip is installed
pip --version >nul 2>&1
if errorlevel 1 (
    echo ❌ pip is not installed. Please install pip.
    pause
    exit /b 1
)

REM Create virtual environment if it doesn't exist
if not exist "venv" (
    echo 📦 Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo 🔧 Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies
echo 📥 Installing dependencies...
pip install -r requirements.txt

REM Check if .env file exists
if not exist ".env" (
    echo ⚠️  .env file not found. Creating from template...
    copy env.example .env
    echo 📝 Please edit .env file and add your GEMINI_API_KEY
    echo    You can get your API key from: https://makersuite.google.com/app/apikey
)

REM Create necessary directories
echo 📁 Creating directories...
if not exist "uploads" mkdir uploads
if not exist "temp" mkdir temp
if not exist "generated_pdfs" mkdir generated_pdfs
if not exist "templates" mkdir templates

REM Check if pdflatex is installed
pdflatex --version >nul 2>&1
if errorlevel 1 (
    echo ⚠️  pdflatex is not installed. Please install LaTeX distribution:
    echo    - Windows: Install MiKTeX or TeX Live
    echo    - Download from: https://miktex.org/ or https://www.tug.org/texlive/
)

REM Start the Flask application
echo 🌟 Starting Flask application...
python app.py

pause
