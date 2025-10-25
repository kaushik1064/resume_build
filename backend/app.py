import os
import sys
import nest_asyncio
import asyncio
import base64
import subprocess
import re
from pathlib import Path
from PIL import Image as PILImage
from PyPDF2 import PdfReader
from pdf2image import convert_from_path
import google.generativeai as genai
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, CacheMode
from datetime import datetime
import logging
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from werkzeug.utils import secure_filename
import tempfile
import shutil
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Apply nest_asyncio for async support
nest_asyncio.apply()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
CORS(app, origins=os.getenv('CORS_ORIGINS', 'http://localhost:5173,http://localhost:3000,http://127.0.0.1:5173,http://127.0.0.1:3000').split(','))

# Configure rate limiting
limiter = Limiter(
    key_func=get_remote_address,
    app=app,
    default_limits=[f"{os.getenv('RATE_LIMIT_PER_MINUTE', '60')} per minute"]
)

# Configure file upload
app.config['MAX_CONTENT_LENGTH'] = int(os.getenv('MAX_FILE_SIZE', 10485760))  # 10MB
app.config['UPLOAD_FOLDER'] = os.getenv('UPLOAD_DIR', 'uploads')
app.config['TEMP_FOLDER'] = os.getenv('TEMP_DIR', 'temp')
app.config['PDF_OUTPUT_DIR'] = os.getenv('PDF_OUTPUT_DIR', 'generated_pdfs')
app.config['LATEX_TEMPLATE_DIR'] = os.getenv('LATEX_TEMPLATE_DIR', 'templates')

# Ensure directories exist
for directory in [app.config['UPLOAD_FOLDER'], app.config['TEMP_FOLDER'], 
                 app.config['PDF_OUTPUT_DIR'], app.config['LATEX_TEMPLATE_DIR']]:
    os.makedirs(directory, exist_ok=True)

# Configure Gemini AI
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    gemini_model = genai.GenerativeModel("gemini-2.5-flash")
else:
    gemini_model = None
    logger.warning("GEMINI_API_KEY not configured. AI features will be limited.")

class ResumeProcessor:
    """Enhanced Resume Processing System - Python Backend Version"""
    
    def __init__(self):
        self.gemini_model = gemini_model
        self.output_dir = app.config['PDF_OUTPUT_DIR']
        self.template_dir = app.config['LATEX_TEMPLATE_DIR']
    
    def extract_text_from_pdf(self, pdf_path):
        """Extract text directly or via Vision fallback using Gemini if available."""
        text = ""
        try:
            reader = PdfReader(pdf_path)
            text = "".join(page.extract_text() or "" for page in reader.pages)
        except Exception as e:
            logger.error(f"PDF text extraction error: {e}")

        # If text extraction failed and we have Gemini, try OCR
        if len(text) < 200 and self.gemini_model:
            try:
                pages = convert_from_path(pdf_path, first_page=1, last_page=1)
                img_path = "first_page.png"
                pages[0].save(img_path, "PNG")
                resp = self.gemini_model.generate_content(["Extract text from this image:", PILImage.open(img_path)])
                text = resp.text or text
                # Clean up temporary image
                if os.path.exists(img_path):
                    os.remove(img_path)
            except Exception as e:
                logger.error(f"OCR fallback error: {e}")
        return text

    def extract_job_role_and_skills(self, jd_text, company_name=""):
        """Extract exact job role and ALL skills from JD for ATS optimization."""
        if not self.gemini_model:
            return {"job_title": "Unknown", "company": company_name, "all_skills": [], "raw_jd": jd_text}

        skill_extraction_prompt = f"""Analyze this job description and extract EVERY skill mentioned.

JOB DESCRIPTION:
{jd_text}

Provide structured extraction in this EXACT format:

## JOB TITLE
[Extract the exact job title: e.g., "Machine Learning Engineer", "Data Scientist", "AI Engineer"]

## COMPANY NAME
[Extract the company name if mentioned, else "Unknown Company"]

## REQUIRED TECHNICAL SKILLS
[List EVERY technical skill, tool, framework, library, programming language mentioned]
- Include variations (e.g., "Python", "ML", "Machine Learning", "TensorFlow", "PyTorch")
- Include both acronyms and full forms
- Include specific versions if mentioned (e.g., "Python 3.x", "AWS")

## REQUIRED SOFT SKILLS
[List ALL soft skills mentioned: communication, leadership, teamwork, problem-solving, etc.]

## REQUIRED CERTIFICATIONS
[List any certifications mentioned]

## EXPERIENCE REQUIREMENTS
[Years of experience, specific domains, industry experience]

## PRIORITY KEYWORDS FOR ATS
[List 30-40 most critical keywords that MUST appear in resume for ATS]
- Include job title variations
- Include all technical skills
- Include industry terms
- Include action verbs from JD

Be exhaustive - missing a skill could cause ATS rejection."""

        try:
            resp = self.gemini_model.generate_content(skill_extraction_prompt)
            analysis_text = resp.text

            # Parse job title
            job_title = "Unknown Role"
            if "## JOB TITLE" in analysis_text:
                title_section = analysis_text.split("## JOB TITLE")[1].split("##")[0].strip()
                lines = [l.strip() for l in title_section.split('\n') if l.strip()]
                if lines:
                    job_title = lines[0].strip('[]"\'')
            
            # Parse company name
            extracted_company = company_name
            if "## COMPANY NAME" in analysis_text:
                company_section = analysis_text.split("## COMPANY NAME")[1].split("##")[0].strip()
                lines = [l.strip() for l in company_section.split('\n') if l.strip()]
                if lines:
                    comp = lines[0].strip('[]"\'')
                    if comp and comp.lower() != "unknown company":
                        extracted_company = comp
            
            # Extract all skills
            skill_keywords = []
            for line in analysis_text.split('\n'):
                line = line.strip()
                if line.startswith('-') or line.startswith('•'):
                    skill_keywords.append(line.lstrip('-•').strip())
            
            return {
                "job_title": job_title,
                "company": extracted_company or "Unknown Company",
                "full_analysis": analysis_text,
                "all_skills": skill_keywords,
                "raw_jd": jd_text
            }
        except Exception as e:
            logger.error(f"JD skill extraction failed: {e}")
            return {"job_title": "Unknown", "company": company_name, "all_skills": [], "raw_jd": jd_text}

    def extract_candidate_personal_and_education(self, resume_text):
        """Extract personal details and education from candidate's resume - CRITICAL for accuracy."""
        if not self.gemini_model:
            return {"personal_and_education": "", "raw_resume": resume_text}

        personal_extraction_prompt = f"""Extract the candidate's ACTUAL personal information and education details from this resume.

RESUME TEXT:
{resume_text}

Provide structured extraction in this EXACT format:

## PERSONAL INFORMATION
- Full Name: [Exact name from resume - DO NOT CHANGE OR MODIFY]
- Phone: [Phone number - EXACTLY as written]
- Email: [Email address - EXACTLY as written]
- LinkedIn: [LinkedIn URL if present, else "Not provided"]
- GitHub: [GitHub URL if present, else "Not provided"]
- Location: [City, State/Country if present, else "Not provided"]
- Portfolio/Website: [If present, else "Not provided"]

## EDUCATION
For EACH degree/education entry, extract EXACTLY as written:
### [Degree] in [Major/Field]
- Institution: [University/College name - EXACTLY as written]
- Duration: [Start date - End date OR Expected graduation - EXACTLY as written]
- GPA: [If mentioned, else "Not provided"]
- Relevant Coursework: [If mentioned]
- Honors/Awards: [If mentioned]
- Activities: [If mentioned]

CRITICAL: Copy names, emails, phone numbers, institutions, dates, and all details EXACTLY as they appear in the original resume. Do not invent, modify, or change ANY information. Preserve the original formatting and wording completely."""

        try:
            resp = self.gemini_model.generate_content(personal_extraction_prompt)
            return {
                "personal_and_education": resp.text,
                "raw_resume": resume_text
            }
        except Exception as e:
            logger.error(f"Personal info extraction failed: {e}")
            return {"personal_and_education": "", "raw_resume": resume_text}

    def extract_candidate_projects_and_experience(self, resume_text):
        """Extract existing projects and work experience for transformation."""
        if not self.gemini_model:
            return {"projects_and_experience": "", "raw_resume": resume_text}

        extraction_prompt = f"""Extract ALL projects and work experiences from this resume.

RESUME TEXT:
{resume_text}

Provide structured extraction:

## WORK EXPERIENCES
For each work experience, extract:
- Company Name
- Job Title
- Duration
- Key Responsibilities (bullet points)
- Technologies Used
- Achievements/Impact

Format as:
### [Company] | [Job Title] | [Duration]
- Responsibility 1
- Responsibility 2
- Technologies: [list]

## PROJECTS
For each project, extract:
- Project Name
- Brief Description
- Technologies Used
- Key Features/Functionality
- Outcomes/Results

Format as:
### [Project Name]
- Description: [brief description]
- Technologies: [list]
- Feature 1
- Feature 2
- Outcome: [result]

## CORE TECHNICAL SKILLS
[List all technical skills candidate currently has]

Be comprehensive - extract every detail."""

        try:
            resp = self.gemini_model.generate_content(extraction_prompt)
            return {
                "projects_and_experience": resp.text,
                "raw_resume": resume_text
            }
        except Exception as e:
            logger.error(f"Resume extraction failed: {e}")
            return {"projects_and_experience": "", "raw_resume": resume_text}

    def analyze_domain_compatibility(self, resume_text, jd_data):
        """Analyze if resume domain matches JD domain and detect mismatches."""
        if not self.gemini_model:
            return {"compatible": True, "mismatch_detected": False, "analysis": ""}

        job_title = jd_data.get('job_title', 'Unknown Role')
        jd_text = jd_data.get('raw_jd', '')
        
        domain_analysis_prompt = f"""Analyze the domain compatibility between this resume and job description.

RESUME TEXT:
{resume_text[:2000]}  # Limit to first 2000 chars

JOB DESCRIPTION:
{job_title}
{jd_text[:2000]}  # Limit to first 2000 chars

Provide analysis in this EXACT format:

## DOMAIN COMPATIBILITY
[Compatible/Partially Compatible/Incompatible]

## RESUME DOMAIN
[Primary domain/field of the resume: e.g., "Machine Learning", "Web Development", "Data Science"]

## JD DOMAIN  
[Primary domain/field of the job: e.g., "Software Engineering", "AI/ML", "Backend Development"]

## COMPATIBILITY ANALYSIS
[Brief explanation of why they are compatible/incompatible]

## RECOMMENDATION
[Should proceed with reconstruction or ask user confirmation]"""

        try:
            resp = self.gemini_model.generate_content(domain_analysis_prompt)
            analysis_text = resp.text
            
            # Parse compatibility
            compatible = True
            mismatch_detected = False
            
            if "## DOMAIN COMPATIBILITY" in analysis_text:
                compatibility_section = analysis_text.split("## DOMAIN COMPATIBILITY")[1].split("##")[0].strip()
                if "incompatible" in compatibility_section.lower():
                    compatible = False
                    mismatch_detected = True
                elif "partially compatible" in compatibility_section.lower():
                    mismatch_detected = True
            
            return {
                "compatible": compatible,
                "mismatch_detected": mismatch_detected,
                "analysis": analysis_text,
                "job_title": job_title
            }
        except Exception as e:
            logger.error(f"Domain analysis failed: {e}")
            return {"compatible": True, "mismatch_detected": False, "analysis": "", "job_title": job_title}

    def validate_resume_sections(self, resume_text):
        resume_lower = resume_text.lower()

        required_sections = {
            "contact": ["contact", "phone", "email", "@", "linkedin", "github"],
            "skills": ["skills", "technical skills", "competencies", "proficiencies"],
            "experience": ["experience", "work history", "employment", "professional experience"],
            "education": ["education", "academic", "degree", "university", "college"],
            "projects": ["projects", "portfolio", "work samples"]
        }

        optional_sections = {
            "certifications": ["certification", "certified", "license"],
            "awards": ["awards", "honors", "achievements", "recognition"],
            "publications": ["publications", "papers", "research", "presented"],
            "languages": ["languages", "fluent", "proficient"]
        }

        present = {}
        missing_required = []
        missing_optional = []
        existing_sections = []

        for section, keywords in required_sections.items():
            found = any(keyword in resume_lower for keyword in keywords)
            present[section] = found
            if found:
                existing_sections.append(section)
            else:
                missing_required.append(section)

        for section, keywords in optional_sections.items():
            found = any(keyword in resume_lower for keyword in keywords)
            present[section] = found
            if found:
                existing_sections.append(section)
            else:
                missing_optional.append(section)

        return {
            "present": present,
            "missing_required": missing_required,
            "missing_optional": missing_optional,
            "existing_sections": existing_sections
        }

    async def scrape_job_description(self, url):
        """Scrape job description from URL using crawl4ai"""
        config = CrawlerRunConfig(
            cache_mode=CacheMode.BYPASS,
            screenshot=False,
            wait_for='js:() => document.body.innerText.length > 200'
        )
        async with AsyncWebCrawler() as crawler:
            result = await crawler.arun(url=url, config=config)
            if result.success:
                text = getattr(result.markdown, "raw_markdown", str(result.markdown))
                return text
            else:
                raise Exception(f"❌ Crawl error: {result.error_message}")

    def reconstruct_resume_with_jd(self, base_latex, personal_data, projects_data, jd_data, section_preferences):
        """Transform candidate's resume to match specific job while preserving personal details."""
        if not self.gemini_model:
            raise RuntimeError("Gemini API key not configured.")

        sections_to_add = section_preferences.get("add_sections", [])
        sections_to_skip = section_preferences.get("skip_sections", [])

        section_instructions = ""
        if sections_to_add:
            section_instructions += f"\n\n## SECTIONS TO ADD\n"
            for section in sections_to_add:
                if section == "contact":
                    section_instructions += "- **Contact Information**: Extract from PERSONAL INFORMATION. Use EXACT details.\n"
                elif section == "skills":
                    section_instructions += "- **Skills**: Include EVERY skill from JD analysis.\n"
                elif section == "experience":
                    section_instructions += "- **Experience**: 3-4 bullets per role (2-3 lines each)\n"
                elif section == "education":
                    section_instructions += "- **Education**: Use EXACT education details from PERSONAL INFORMATION.\n"
                elif section == "projects":
                    section_instructions += "- **Projects**: 3-4 bullets per project (2-3 lines each)\n"
                elif section == "certifications":
                    section_instructions += "- **Certifications**: 3 descriptive points per certification\n"
                elif section == "awards":
                    section_instructions += "- **Awards/Honors**: Add awards section\n"
                elif section == "publications":
                    section_instructions += "- **Publications**: Add publications section\n"
                elif section == "languages":
                    section_instructions += "- **Languages**: Add languages section\n"

        if sections_to_skip:
            section_instructions += f"\n## SECTIONS TO SKIP\nDo NOT include: {', '.join(sections_to_skip)}\n"

        job_title = jd_data.get('job_title', 'Unknown Role')
        company = jd_data.get('company', 'Unknown Company')
        all_jd_skills = jd_data.get('all_skills', [])
        skills_list = "\n".join([f"- {skill}" for skill in all_jd_skills[:20]])  # Limit to 20 skills

        prompt = f"""Transform this resume for {job_title} at {company}. 

TEMPLATE STRUCTURE (use exactly):
{base_latex}

PERSONAL INFO (use EXACTLY - never modify):
{personal_data.get('personal_and_education', '')}

EXISTING PROJECTS/EXPERIENCE (enhance bullet points only):
{projects_data.get('projects_and_experience', '')}

JOB REQUIREMENTS:
{skills_list}

INSTRUCTIONS:
1. Use EXACT personal details (name, email, phone, education)
2. Add "{job_title}" below the person's name in header
3. Keep existing project/experience structure but enhance bullet points for JD match
4. Ensure AT LEAST 4 bullet points for each project and work experience
5. Add metrics and JD keywords to bullet points (%, numbers, scale)
6. Transform work experience descriptions to match JD domain while keeping original company/job names
7. Use \\textbf{{}} for key terms
8. Follow template structure exactly
9. Return only LaTeX code

Generate resume:"""

        try:
            resp = self.gemini_model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.7,
                    top_p=0.9,
                    top_k=40,
                    max_output_tokens=8192,
                )
            )
            
            # Check if response is valid
            if not resp or not resp.text:
                logger.error(f"Gemini API returned empty response. Finish reason: {getattr(resp, 'finish_reason', 'unknown')}")
                raise Exception("AI response was empty or blocked")
                
            return resp.text.strip()
        except Exception as e:
            logger.error(f"Resume reconstruction failed: {e}")
            raise

    def local_sanitize_latex(self, latex_code: str) -> str:
        """Apply deterministic fixes for common LaTeX problems."""
        s = latex_code
        s = s.replace("```latex", "").replace("```", "")
        s = re.sub(r"(\\begin\{document\}\s*){2,}", r"\\begin{document}\n", s)
        s = re.sub(r"(\\resheading\{[^\}]*\})\s*(?:\\\\\[[^\]]*\]\s*)+(?:\\\\\s*)+", r"\1\n", s)
        s = re.sub(r"(\\resheading\{[^\}]*\})\s*\\\\\s*\\\\", r"\1\n", s)

        lines = s.splitlines()
        out_lines = []
        in_tabular = False
        tabular_envs = {"tabular", "tabular*", "array", "align", "align*", "matrix"}
        begin_re = re.compile(r"\\begin\{([^}]*)\}")
        end_re = re.compile(r"\\end\{([^}]*)\}")

        for ln in lines:
            bm = begin_re.search(ln)
            em = end_re.search(ln)
            if bm:
                env = bm.group(1).strip()
                if env in tabular_envs:
                    in_tabular = True
            if em:
                env = em.group(1).strip()
                if env in tabular_envs:
                    in_tabular = False

            if not in_tabular:
                if "&" in ln and ("\\&" not in ln):
                    if not any(x in ln for x in ["\\href", "http", "mailto:", "\\url"]):
                        ln = ln.replace("&", r"\&")
            out_lines.append(ln)
        s = "\n".join(out_lines)

        s = re.sub(r"(?<!\\)_", r"\_", s)

        open_braces = s.count("{")
        close_braces = s.count("}")
        if open_braces > close_braces:
            s += "}" * (open_braces - close_braces)

        s = s.strip() + "\n"
        return s

    def lint_latex_with_gemini(self, latex_code: str) -> str:
        """Enhanced LaTeX linting."""
        if not self.gemini_model:
            raise RuntimeError("Gemini model not configured.")

        prompt = f"""Fix ALL LaTeX compilation errors.

# LATEX SOURCE
```
{latex_code}
```

Return ONLY corrected LaTeX code. No explanations."""

        try:
            resp = self.gemini_model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.3,
                    top_p=0.95,
                    max_output_tokens=8192,
                )
            )
            cleaned = resp.text or ""

            if not cleaned.strip() or cleaned.count("\n") < 5 or "```" in cleaned:
                logger.warning("Lint fallback to local sanitizer")
                cleaned = self.local_sanitize_latex(latex_code)

            return cleaned
        except Exception as e:
            logger.error(f"Linting error: {e}")
            return self.local_sanitize_latex(latex_code)

    def compile_latex_to_pdf(self, latex_code, output_pdf="tailored_resume.pdf"):
        """Compile LaTeX to PDF using pdflatex"""
        tex_file = output_pdf.replace(".pdf", ".tex")
        latex_code = latex_code.replace("```latex", "").replace("```", "")

        # Write LaTeX file
        tex_path = os.path.join(self.output_dir, tex_file)
        with open(tex_path, "w", encoding="utf-8") as f:
            f.write(latex_code)

        try:
            # First compilation
            result1 = subprocess.run(
                ["pdflatex", "-interaction=nonstopmode", tex_file],
                cwd=self.output_dir,
                capture_output=True,
                text=True
            )
            
            if result1.returncode != 0:
                raise Exception(f"First compilation failed: {result1.stderr}")

            # Second compilation for references
            result2 = subprocess.run(
                ["pdflatex", "-interaction=nonstopmode", tex_file],
                cwd=self.output_dir,
                capture_output=True,
                text=True
            )
            
            if result2.returncode != 0:
                raise Exception(f"Second compilation failed: {result2.stderr}")

            pdf_path = os.path.join(self.output_dir, output_pdf)
            logger.info(f"✅ PDF generated: {output_pdf}")
            return pdf_path
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ Compilation failed for {output_pdf}")
            raise Exception(f"PDF compilation failed: {e}")

# Initialize processor
resume_processor = ResumeProcessor()

# API Routes
@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'OK',
        'timestamp': datetime.now().isoformat(),
        'environment': os.getenv('FLASK_ENV', 'development'),
        'gemini_configured': bool(GEMINI_API_KEY)
    })

@app.route('/api/chat/message', methods=['POST'])
@limiter.limit("10 per minute")
def chat_message():
    """Handle chat messages"""
    try:
        data = request.get_json()
        message = data.get('message', '')
        step = data.get('step', 'initial')

        # Process different conversation steps
        if step == 'initial':
            if any(word in message.lower() for word in ['yes', 'start', 'create', 'sure']):
                response = "Great! Let's begin. First, please upload your existing resume or paste your details in text format. You can upload a file using the upload button below."
                next_step = 'awaiting_resume'
            else:
                response = "No problem! Whenever you're ready to create your resume, just let me know!"
                next_step = 'initial'
        elif step == 'awaiting_missing_sections':
            response = "Perfect! I'm now generating your resume. This will take just a moment..."
            next_step = 'generating'
        else:
            response = "I understand. Let me help you with that."
            next_step = step

        return jsonify({
            'success': True,
            'response': response,
            'nextStep': next_step
        })

    except Exception as e:
        logger.error(f"Chat error: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to process chat message'
        }), 500

@app.route('/api/upload/resume', methods=['POST'])
@limiter.limit("5 per minute")
def upload_resume():
    """Upload and process resume file"""
    try:
        if 'file' not in request.files:
            return jsonify({
                'success': False,
                'error': 'No file uploaded'
            }), 400

        file = request.files['file']
        if file.filename == '':
            return jsonify({
                'success': False,
                'error': 'No file selected'
            }), 400

        if file:
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)

            try:
                # Extract text from PDF
                if file.content_type == 'application/pdf':
                    extracted_text = resume_processor.extract_text_from_pdf(file_path)
                else:
                    # For text files
                    with open(file_path, 'r', encoding='utf-8') as f:
                        extracted_text = f.read()

                # Clean up uploaded file
                os.remove(file_path)

                return jsonify({
                    'success': True,
                    'message': 'Resume uploaded and processed successfully',
                    'data': {
                        'filename': filename,
                        'extractedText': extracted_text,
                        'fileSize': len(extracted_text)
                    }
                })

            except Exception as e:
                # Clean up file on error
                if os.path.exists(file_path):
                    os.remove(file_path)
                raise e

    except Exception as e:
        logger.error(f"Resume upload error: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to process uploaded resume'
        }), 500

@app.route('/api/upload/text-resume', methods=['POST'])
@limiter.limit("10 per minute")
def upload_text_resume():
    """Upload resume as text"""
    try:
        data = request.get_json()
        resume_text = data.get('resumeText', '')

        if not resume_text or resume_text.strip() == '':
            return jsonify({
                'success': False,
                'error': 'Resume text is required'
            }), 400

        return jsonify({
            'success': True,
            'message': 'Resume text received successfully',
            'data': {
                'extractedText': resume_text.strip(),
                'textLength': len(resume_text)
            }
        })

    except Exception as e:
        logger.error(f"Text resume upload error: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to process resume text'
        }), 500

@app.route('/api/upload/job-urls', methods=['POST'])
@limiter.limit("5 per minute")
def process_job_urls():
    """Process job description URLs"""
    try:
        data = request.get_json()
        urls = data.get('urls', [])

        if not urls or not isinstance(urls, list) or len(urls) == 0:
            return jsonify({
                'success': False,
                'error': 'At least one URL is required'
            }), 400

        job_descriptions = []

        for url in urls:
            try:
                # Use asyncio to run the async scraping function
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                jd_text = loop.run_until_complete(resume_processor.scrape_job_description(url))
                loop.close()

                jd_data = resume_processor.extract_job_role_and_skills(jd_text)
                
                job_descriptions.append({
                    'url': url,
                    'text': jd_text,
                    'analysis': jd_data
                })
            except Exception as e:
                logger.error(f"Failed to process URL {url}: {e}")
                job_descriptions.append({
                    'url': url,
                    'error': 'Failed to process this URL',
                    'text': '',
                    'analysis': None
                })

        return jsonify({
            'success': True,
            'message': 'Job descriptions processed',
            'data': {
                'jobDescriptions': job_descriptions,
                'totalProcessed': len(job_descriptions)
            }
        })

    except Exception as e:
        logger.error(f"Job URLs processing error: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to process job URLs'
        }), 500

@app.route('/api/resume/generate', methods=['POST'])
@limiter.limit("3 per minute")
def generate_resume():
    """Generate tailored resume"""
    try:
        logger.info("🚀 Resume generation endpoint called")
        data = request.get_json()
        resume_text = data.get('resumeText', '')
        job_descriptions = data.get('jobDescriptions', [])
        section_preferences = data.get('sectionPreferences', {})
        template_content = data.get('templateContent', '')
        personal_data = data.get('personalData', {})
        projects_data = data.get('projectsData', {})

        logger.info(f"📦 Received data: resume_text_length={len(resume_text)}, job_descriptions_count={len(job_descriptions)}")
        logger.info(f"📋 Job descriptions structure: {[jd.get('analysis', {}).get('job_title', 'Unknown') if isinstance(jd, dict) else 'Invalid' for jd in job_descriptions]}")

        # Validate required fields
        if not resume_text or not job_descriptions or not template_content:
            logger.error(f"❌ Missing required fields: resume_text={bool(resume_text)}, job_descriptions={bool(job_descriptions)}, template_content={bool(template_content)}")
            return jsonify({
                'success': False,
                'error': 'Missing required fields: resumeText, jobDescriptions, and templateContent are required'
            }), 400

        results = []

        # Process each job description
        for i, jd in enumerate(job_descriptions):
            try:
                # Generate tailored resume for this job
                tailored_latex = resume_processor.reconstruct_resume_with_jd(
                    template_content,
                    personal_data or {'personal_and_education': '', 'raw_resume': resume_text},
                    projects_data or {'projects_and_experience': '', 'raw_resume': resume_text},
                    jd.get('analysis', {}),
                    section_preferences or {'add_sections': [], 'skip_sections': []}
                )

                # Sanitize LaTeX
                sanitized_latex = resume_processor.local_sanitize_latex(tailored_latex)

                # Lint with Gemini if available
                if GEMINI_API_KEY:
                    try:
                        cleaned_latex = resume_processor.lint_latex_with_gemini(sanitized_latex)
                    except Exception as e:
                        logger.warning(f"Linting failed, using sanitized version: {e}")
                        cleaned_latex = sanitized_latex
                else:
                    cleaned_latex = sanitized_latex

                # Generate unique filename
                safe_company = re.sub(r'[^\w\s-]', '', jd.get('analysis', {}).get('company', 'Unknown'))[:30]
                safe_role = re.sub(r'[^\w\s-]', '', jd.get('analysis', {}).get('job_title', 'Unknown'))[:30]
                output_name = f"resume_{i + 1}_{safe_company}_{safe_role}.pdf".replace(' ', '_')

                # Compile to PDF
                pdf_path = resume_processor.compile_latex_to_pdf(cleaned_latex, output_name)

                results.append({
                    'index': i + 1,
                    'company': jd.get('analysis', {}).get('company', 'Unknown Company'),
                    'role': jd.get('analysis', {}).get('job_title', 'Unknown Role'),
                    'pdfPath': pdf_path,
                    'filename': output_name,
                    'success': True
                })

            except Exception as e:
                logger.error(f"Failed to generate resume for job {i + 1}: {e}")
                results.append({
                    'index': i + 1,
                    'company': jd.get('analysis', {}).get('company', 'Unknown Company'),
                    'role': jd.get('analysis', {}).get('job_title', 'Unknown Role'),
                    'success': False,
                    'error': str(e)
                })

        # Prepare response
        successful = [r for r in results if r['success']]
        failed = [r for r in results if not r['success']]

        return jsonify({
            'success': True,
            'message': f'Processed {len(job_descriptions)} job descriptions',
            'data': {
                'results': results,
                'summary': {
                    'total': len(results),
                    'successful': len(successful),
                    'failed': len(failed)
                },
                'successfulResumes': [{
                    'index': r['index'],
                    'company': r['company'],
                    'role': r['role'],
                    'filename': r['filename'],
                    'downloadUrl': f'/api/resume/download/{r["filename"]}'
                } for r in successful]
            }
        })

    except Exception as e:
        logger.error(f"Resume generation error: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to generate resume'
        }), 500

@app.route('/api/resume/download/<filename>', methods=['GET'])
def download_resume(filename):
    """Download generated resume"""
    try:
        file_path = os.path.join(app.config['PDF_OUTPUT_DIR'], filename)

        if not os.path.exists(file_path):
            return jsonify({
                'success': False,
                'error': 'File not found'
            }), 404

        return send_file(file_path, as_attachment=True, download_name=filename)

    except Exception as e:
        logger.error(f"Download error: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to download resume'
        }), 500

@app.route('/api/resume/list', methods=['GET'])
def list_resumes():
    """List generated resumes"""
    try:
        output_dir = app.config['PDF_OUTPUT_DIR']
        
        if not os.path.exists(output_dir):
            return jsonify({
                'success': True,
                'data': {
                    'resumes': [],
                    'total': 0
                }
            })

        files = os.listdir(output_dir)
        pdf_files = [f for f in files if f.endswith('.pdf')]

        resume_list = []
        for file in pdf_files:
            file_path = os.path.join(output_dir, file)
            stats = os.stat(file_path)
            
            resume_list.append({
                'filename': file,
                'size': stats.st_size,
                'created': datetime.fromtimestamp(stats.st_ctime).isoformat(),
                'modified': datetime.fromtimestamp(stats.st_mtime).isoformat(),
                'downloadUrl': f'/api/resume/download/{file}'
            })

        return jsonify({
            'success': True,
            'data': {
                'resumes': resume_list,
                'total': len(resume_list)
            }
        })

    except Exception as e:
        logger.error(f"List resumes error: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to list resumes'
        }), 500

@app.route('/api/extract/personal', methods=['POST'])
@limiter.limit("10 per minute")
def extract_personal_data():
    """Extract personal data from resume text"""
    try:
        data = request.get_json()
        resume_text = data.get('resumeText', '')

        if not resume_text or resume_text.strip() == '':
            return jsonify({
                'success': False,
                'error': 'Resume text is required'
            }), 400

        # Extract personal data using the processor
        personal_data = resume_processor.extract_candidate_personal_and_education(resume_text)

        return jsonify({
            'success': True,
            'message': 'Personal data extracted successfully',
            'data': personal_data
        })

    except Exception as e:
        logger.error(f"Personal data extraction error: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to extract personal data'
        }), 500

@app.route('/api/extract/projects', methods=['POST'])
@limiter.limit("10 per minute")
def extract_projects_data():
    """Extract projects data from resume text"""
    try:
        data = request.get_json()
        resume_text = data.get('resumeText', '')

        if not resume_text or resume_text.strip() == '':
            return jsonify({
                'success': False,
                'error': 'Resume text is required'
            }), 400

        # Extract projects data using the processor
        projects_data = resume_processor.extract_candidate_projects_and_experience(resume_text)

        return jsonify({
            'success': True,
            'message': 'Projects data extracted successfully',
            'data': projects_data
        })

    except Exception as e:
        logger.error(f"Projects data extraction error: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to extract projects data'
        }), 500

@app.route('/api/template', methods=['GET'])
def get_template():
    """Get the default LaTeX template"""
    try:
        template_path = os.path.join(app.config['LATEX_TEMPLATE_DIR'], 'default_template.tex')
        
        if not os.path.exists(template_path):
            return jsonify({
                'success': False,
                'error': 'Template file not found'
            }), 404

        with open(template_path, 'r', encoding='utf-8') as f:
            template_content = f.read()

        return jsonify({
            'success': True,
            'message': 'Template retrieved successfully',
            'data': {
                'template': template_content
            }
        })

    except Exception as e:
        logger.error(f"Template retrieval error: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to retrieve template'
        }), 500

@app.route('/api/analyze/sections', methods=['POST'])
@limiter.limit("10 per minute")
def analyze_resume_sections():
    """Analyze resume sections and provide enhancement suggestions"""
    try:
        data = request.get_json()
        resume_text = data.get('resumeText', '')

        if not resume_text or resume_text.strip() == '':
            return jsonify({
                'success': False,
                'error': 'Resume text is required'
            }), 400

        # Analyze sections
        section_analysis = resume_processor.validate_resume_sections(resume_text)
        
        # Create enhancement suggestions
        missing_sections = section_analysis['missing_required'] + section_analysis['missing_optional']
        existing_sections = section_analysis['existing_sections']
        
        enhancement_suggestions = []
        if 'skills' in existing_sections:
            enhancement_suggestions.append("Enhance skills section to better match job requirements")
        if 'projects' in existing_sections:
            enhancement_suggestions.append("Improve project descriptions with metrics and JD keywords")
        if 'experience' in existing_sections:
            enhancement_suggestions.append("Enhance work experience bullet points for better JD alignment")

        return jsonify({
            'success': True,
            'message': 'Section analysis completed',
            'data': {
                'missing_sections': missing_sections,
                'existing_sections': existing_sections,
                'enhancement_suggestions': enhancement_suggestions,
                'analysis': section_analysis
            }
        })

    except Exception as e:
        logger.error(f"Section analysis error: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to analyze resume sections'
        }), 500

@app.route('/api/analyze/domain', methods=['POST'])
@limiter.limit("10 per minute")
def analyze_domain_compatibility():
    """Analyze domain compatibility between resume and job descriptions"""
    try:
        data = request.get_json()
        resume_text = data.get('resumeText', '')
        job_descriptions = data.get('jobDescriptions', [])

        if not resume_text or not job_descriptions:
            return jsonify({
                'success': False,
                'error': 'Resume text and job descriptions are required'
            }), 400

        domain_analyses = []
        overall_compatible = True
        any_mismatch = False

        for jd in job_descriptions:
            if jd.get('analysis'):
                domain_analysis = resume_processor.analyze_domain_compatibility(resume_text, jd['analysis'])
                domain_analyses.append({
                    'job_title': domain_analysis.get('job_title', 'Unknown'),
                    'compatible': domain_analysis.get('compatible', True),
                    'mismatch_detected': domain_analysis.get('mismatch_detected', False),
                    'analysis': domain_analysis.get('analysis', '')
                })
                
                if not domain_analysis.get('compatible', True):
                    overall_compatible = False
                if domain_analysis.get('mismatch_detected', False):
                    any_mismatch = True

        return jsonify({
            'success': True,
            'message': 'Domain analysis completed',
            'data': {
                'domain_analyses': domain_analyses,
                'overall_compatible': overall_compatible,
                'any_mismatch_detected': any_mismatch,
                'needs_confirmation': any_mismatch
            }
        })

    except Exception as e:
        logger.error(f"Domain analysis error: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to analyze domain compatibility'
        }), 500

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    
    logger.info(f"🚀 Starting Resume Builder Backend on port {port}")
    logger.info(f"📊 Environment: {os.getenv('FLASK_ENV', 'development')}")
    logger.info(f"🔗 Health check: http://localhost:{port}/api/health")
    
    app.run(host='0.0.0.0', port=port, debug=debug)
