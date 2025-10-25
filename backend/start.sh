#!/bin/bash

# Resume Builder Backend Startup Script

echo "🚀 Starting Resume Builder Backend..."

# Run Python version checker
echo "🔍 Checking Python version..."
python3 check_python.py
if [ $? -ne 0 ]; then
    echo "❌ Python version check failed. Please install Python 3.11+ first."
    exit 1
fi

# Check if Python 3.11 is installed
if ! command -v python3.11 &> /dev/null; then
    if ! command -v python3 &> /dev/null; then
        echo "❌ Python 3 is not installed. Please install Python 3.11 or higher."
        exit 1
    else
        # Check if it's Python 3.11+
        python_version=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
        if [[ $(echo "$python_version < 3.11" | bc -l) -eq 1 ]]; then
            echo "❌ Python 3.11 or higher is required. Current version: $python_version"
            echo "   Please install Python 3.11 or higher."
            exit 1
        fi
    fi
fi

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 is not installed. Please install pip3."
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    if command -v python3.11 &> /dev/null; then
        python3.11 -m venv venv
    else
        python3 -m venv venv
    fi
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found. Creating from template..."
    cp env.example .env
    echo "📝 Please edit .env file and add your GEMINI_API_KEY"
    echo "   You can get your API key from: https://makersuite.google.com/app/apikey"
fi

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p uploads temp generated_pdfs templates

# Check if pdflatex is installed
if ! command -v pdflatex &> /dev/null; then
    echo "⚠️  pdflatex is not installed. Please install LaTeX distribution:"
    echo "   - Ubuntu/Debian: sudo apt-get install texlive-full"
    echo "   - macOS: brew install --cask mactex"
    echo "   - Windows: Install MiKTeX or TeX Live"
fi

# Start the Flask application
echo "🌟 Starting Flask application..."
if command -v python3.11 &> /dev/null; then
    python3.11 app.py
else
    python3 app.py
fi
