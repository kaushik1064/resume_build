# Resume Builder - Complete Setup Guide

This guide will help you set up the complete Resume Builder system with both frontend and backend components.

## System Overview

The Resume Builder consists of:
- **Frontend**: React/TypeScript chat interface (Port 5173)
- **Backend**: Python Flask API with AI processing (Port 5000)
- **AI Integration**: Google Gemini AI for resume analysis and generation
- **PDF Generation**: LaTeX compilation for professional resumes

## Prerequisites

### Required Software
1. **Node.js** (v16 or higher) - [Download](https://nodejs.org/)
2. **Python** (v3.11 or higher) - [Download](https://python.org/)
3. **LaTeX Distribution**:
   - **Windows**: [MiKTeX](https://miktex.org/) or [TeX Live](https://www.tug.org/texlive/)
   - **macOS**: `brew install --cask mactex`
   - **Ubuntu/Debian**: `sudo apt-get install texlive-full`

### Required API Keys
1. **Google Gemini API Key** - [Get from Google AI Studio](https://makersuite.google.com/app/apikey)

## Quick Start

### 1. Clone and Setup Backend

```bash
# Navigate to backend directory
cd backend

# Check Python version (optional but recommended)
python check_python.py

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Setup environment
cp env.example .env
# Edit .env and add your GEMINI_API_KEY

# Create directories
mkdir uploads temp generated_pdfs templates

# Start backend
python app.py
```

### 2. Setup Frontend (in new terminal)

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start frontend
npm run dev
```

### 3. Access the Application

- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:5000/api/health

## Detailed Setup Instructions

### Backend Setup (Python Flask)

1. **Environment Setup**:
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # or venv\Scripts\activate on Windows
   pip install -r requirements.txt
   ```

2. **Configuration**:
   ```bash
   cp env.example .env
   ```
   
   Edit `.env` file:
   ```env
   GEMINI_API_KEY=your_actual_api_key_here
   FLASK_ENV=development
   PORT=5000
   ```

3. **Directory Structure**:
   ```bash
   mkdir -p uploads temp generated_pdfs templates
   ```

4. **Start Backend**:
   ```bash
   python app.py
   ```

### Frontend Setup (React/TypeScript)

1. **Install Dependencies**:
   ```bash
   cd frontend
   npm install
   ```

2. **Start Development Server**:
   ```bash
   npm run dev
   ```

## Testing the System

### 1. Backend Health Check
```bash
curl http://localhost:5000/api/health
```

### 2. Run Backend Tests
```bash
cd backend
python test_backend.py
```

### 3. Frontend Integration Test
1. Open http://localhost:5173
2. Click "Yes" to start
3. Upload a resume file or paste text
4. Add job URLs
5. Specify additional sections
6. Generate and download resumes

## Usage Flow

### Complete User Journey

1. **Start Chat**: User opens frontend and initiates conversation
2. **Upload Resume**: User uploads PDF or pastes resume text
3. **Add Job URLs**: User provides job posting URLs
4. **Specify Sections**: User indicates additional sections needed
5. **AI Processing**: Backend analyzes resume and job descriptions
6. **Generate Resumes**: AI creates tailored resumes for each job
7. **Download PDFs**: User downloads generated resumes

### API Endpoints

- `GET /api/health` - Health check
- `POST /api/chat/message` - Chat interaction
- `POST /api/upload/resume` - File upload
- `POST /api/upload/text-resume` - Text upload
- `POST /api/upload/job-urls` - Job URL processing
- `POST /api/resume/generate` - Resume generation
- `GET /api/resume/download/<filename>` - Download resume
- `GET /api/resume/list` - List generated resumes

## Troubleshooting

### Common Issues

1. **Backend won't start**:
   - Check Python version: `python --version`
   - Verify virtual environment is activated
   - Check if port 5000 is available
   - Ensure all dependencies are installed

2. **Frontend won't connect**:
   - Verify backend is running on port 5000
   - Check CORS settings in backend
   - Ensure API_BASE_URL in frontend is correct

3. **PDF generation fails**:
   - Install LaTeX distribution
   - Verify `pdflatex` is in PATH
   - Check file permissions in generated_pdfs directory

4. **AI processing fails**:
   - Verify GEMINI_API_KEY is set correctly
   - Check API key permissions
   - Ensure internet connection

### Debug Mode

**Backend Debug**:
```bash
export FLASK_DEBUG=True
python app.py
```

**Frontend Debug**:
```bash
npm run dev -- --debug
```

## Production Deployment

### Backend Production

1. **Environment Setup**:
   ```env
   FLASK_ENV=production
   FLASK_DEBUG=False
   ```

2. **Use Production Server**:
   ```bash
   pip install gunicorn
   gunicorn -w 4 -b 0.0.0.0:5000 app:app
   ```

### Frontend Production

1. **Build for Production**:
   ```bash
   npm run build
   ```

2. **Serve Static Files**:
   ```bash
   npm install -g serve
   serve -s dist -l 3000
   ```

## File Structure

```
resume_build/
├── backend/
│   ├── app.py                 # Main Flask application
│   ├── requirements.txt       # Python dependencies
│   ├── test_backend.py       # Backend tests
│   ├── start.sh              # Linux/macOS startup script
│   ├── start.bat             # Windows startup script
│   ├── README.md             # Backend documentation
│   ├── env.example           # Environment template
│   ├── uploads/              # File upload directory
│   ├── temp/                 # Temporary files
│   ├── generated_pdfs/        # Generated resumes
│   └── templates/            # LaTeX templates
└── frontend/
    ├── src/
    │   ├── components/       # React components
    │   ├── services/         # API services
    │   └── utils/            # Utility functions
    ├── package.json          # Node.js dependencies
    └── vite.config.ts        # Vite configuration
```

## Support

### Getting Help

1. **Check Logs**: Look at console output for error messages
2. **Test Components**: Use individual API endpoints to isolate issues
3. **Verify Setup**: Ensure all prerequisites are installed correctly
4. **Check Configuration**: Verify environment variables and settings

### Development Tips

1. **Backend Development**:
   - Use `FLASK_DEBUG=True` for detailed error messages
   - Check logs in console for debugging
   - Test API endpoints with curl or Postman

2. **Frontend Development**:
   - Use browser developer tools for debugging
   - Check network tab for API call issues
   - Verify API service configuration

3. **AI Integration**:
   - Test with simple text first
   - Verify API key permissions
   - Check rate limits and quotas

## Next Steps

After successful setup:

1. **Customize Templates**: Modify LaTeX templates in `backend/templates/`
2. **Add Features**: Extend API endpoints and frontend components
3. **Improve AI Prompts**: Enhance resume analysis and generation
4. **Add Authentication**: Implement user accounts and data persistence
5. **Deploy**: Set up production environment with proper security

## Contributing

To contribute to this project:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

For major changes, please open an issue first to discuss the proposed changes.
