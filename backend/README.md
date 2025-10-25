# Resume Builder Backend

A Python Flask backend for the AI-powered resume builder that processes resumes and generates tailored PDFs based on job descriptions.

## Features

- **Resume Processing**: Extract text from PDF files and analyze resume content
- **Job Description Analysis**: Scrape and analyze job postings from URLs
- **AI-Powered Generation**: Use Google Gemini AI to tailor resumes for specific jobs
- **LaTeX Compilation**: Generate professional PDF resumes using LaTeX
- **Multi-Job Support**: Process multiple job descriptions and generate tailored resumes for each

## Prerequisites

- Python 3.11 or higher
- pip (Python package installer)
- LaTeX distribution (for PDF compilation)
  - **Ubuntu/Debian**: `sudo apt-get install texlive-full`
  - **macOS**: `brew install --cask mactex`
  - **Windows**: Install MiKTeX or TeX Live

## Installation

1. **Clone the repository** (if not already done):
   ```bash
   git clone <repository-url>
   cd resume_build/backend
   ```

2. **Create virtual environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**:
   ```bash
   cp env.example .env
   ```
   
   Edit `.env` file and add your Gemini API key:
   ```
   GEMINI_API_KEY=your_gemini_api_key_here
   ```
   
   Get your API key from: https://makersuite.google.com/app/apikey

5. **Create necessary directories**:
   ```bash
   mkdir -p uploads temp generated_pdfs templates
   ```

## Running the Backend

### Option 1: Using the startup script (Recommended)

**Linux/macOS**:
```bash
chmod +x start.sh
./start.sh
```

**Windows**:
```cmd
start.bat
```

### Option 2: Manual startup

1. **Activate virtual environment**:
   ```bash
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Start the Flask application**:
   ```bash
   python app.py
   ```

The backend will start on `http://localhost:5000` by default.

## API Endpoints

### Health Check
- **GET** `/api/health` - Check if the backend is running

### Chat Interface
- **POST** `/api/chat/message` - Send chat messages and handle conversation flow

### File Upload
- **POST** `/api/upload/resume` - Upload resume file (PDF, DOC, DOCX, TXT)
- **POST** `/api/upload/text-resume` - Upload resume as text
- **POST** `/api/upload/job-urls` - Process job description URLs

### Resume Generation
- **POST** `/api/resume/generate` - Generate tailored resumes
- **GET** `/api/resume/download/<filename>` - Download generated resume
- **GET** `/api/resume/list` - List all generated resumes
- **DELETE** `/api/resume/<filename>` - Delete a generated resume

## Configuration

Edit the `.env` file to customize:

```env
# Server Configuration
FLASK_ENV=development
FLASK_DEBUG=True
PORT=5000

# File Upload Configuration
MAX_FILE_SIZE=10485760  # 10MB
UPLOAD_DIR=uploads
TEMP_DIR=temp

# Rate Limiting
RATE_LIMIT_PER_MINUTE=60

# CORS Configuration
CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173

# PDF Generation
PDF_OUTPUT_DIR=generated_pdfs
LATEX_TEMPLATE_DIR=templates
```

## Usage Flow

1. **Start the backend** using one of the methods above
2. **Start the frontend** (in a separate terminal):
   ```bash
   cd ../frontend
   npm run dev
   ```
3. **Open your browser** to `http://localhost:5173`
4. **Follow the chat interface** to:
   - Upload your resume
   - Provide job URLs
   - Specify additional sections
   - Generate and download tailored resumes

## Troubleshooting

### Common Issues

1. **"pdflatex not found"**:
   - Install LaTeX distribution (see Prerequisites)
   - Make sure `pdflatex` is in your PATH

2. **"GEMINI_API_KEY not configured"**:
   - Add your API key to the `.env` file
   - Get API key from Google AI Studio

3. **"Failed to connect to backend"**:
   - Make sure the backend is running on port 5000
   - Check if the frontend is trying to connect to the correct URL

4. **File upload errors**:
   - Check file size limits (default: 10MB)
   - Ensure file format is supported (PDF, DOC, DOCX, TXT)

### Logs

The backend logs important information to the console. Check the terminal where you started the backend for error messages and debugging information.

## Development

### Adding New Features

1. **New API endpoints**: Add routes in `app.py`
2. **Resume processing**: Extend the `ResumeProcessor` class
3. **Frontend integration**: Update the API service in `frontend/src/services/api.ts`

### Testing

Test individual components:
```bash
# Test PDF extraction
python -c "from app import resume_processor; print(resume_processor.extract_text_from_pdf('test.pdf'))"

# Test API health
curl http://localhost:5000/api/health
```

## Production Deployment

For production deployment:

1. **Set production environment**:
   ```env
   FLASK_ENV=production
   FLASK_DEBUG=False
   ```

2. **Use a production WSGI server**:
   ```bash
   pip install gunicorn
   gunicorn -w 4 -b 0.0.0.0:5000 app:app
   ```

3. **Set up reverse proxy** (nginx/Apache) for better performance and security

## Support

If you encounter issues:

1. Check the console logs for error messages
2. Verify all prerequisites are installed
3. Ensure environment variables are set correctly
4. Test individual components using the API endpoints

For additional help, check the frontend documentation or create an issue in the repository.
