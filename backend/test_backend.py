#!/usr/bin/env python3.11
"""
Test script for Resume Builder Backend
This script tests the basic functionality of the backend API
Requires Python 3.11 or higher
"""

import sys
import requests
import json
import time
import os
from pathlib import Path

# Check Python version
if sys.version_info < (3, 11):
    print(f"❌ Python 3.11 or higher is required. Current version: {sys.version}")
    print("   Please install Python 3.11 or higher.")
    sys.exit(1)

# Configuration
BASE_URL = "http://localhost:5000/api"
TEST_RESUME_TEXT = """
John Doe
Software Engineer
Email: john.doe@example.com
Phone: (555) 123-4567
LinkedIn: https://linkedin.com/in/johndoe
GitHub: https://github.com/johndoe

EDUCATION
Bachelor of Science in Computer Science
University of Technology, 2020
GPA: 3.8/4.0

EXPERIENCE
Software Engineer | Tech Corp | 2021-2023
- Developed web applications using React and Node.js
- Improved system performance by 40%
- Led a team of 3 developers

Junior Developer | StartupXYZ | 2020-2021
- Built REST APIs using Python and Flask
- Implemented automated testing reducing bugs by 30%

PROJECTS
E-commerce Platform
- Built full-stack application with React, Node.js, MongoDB
- Implemented payment processing with Stripe API
- Deployed on AWS with Docker

Task Management App
- Created mobile app using React Native
- Integrated with Firebase for real-time updates

SKILLS
Programming Languages: Python, JavaScript, Java, C++
Frameworks: React, Node.js, Flask, Django
Databases: MongoDB, PostgreSQL, MySQL
Tools: Git, Docker, AWS, Jenkins
"""

def test_health_check():
    """Test the health check endpoint"""
    print("🔍 Testing health check...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health check passed: {data['status']}")
            print(f"   Environment: {data['environment']}")
            print(f"   Gemini configured: {data.get('gemini_configured', False)}")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to backend. Make sure it's running on port 5000")
        return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False

def test_chat_message():
    """Test chat message endpoint"""
    print("\n💬 Testing chat message...")
    try:
        data = {
            "message": "Yes, I want to create a resume",
            "step": "initial"
        }
        response = requests.post(f"{BASE_URL}/chat/message", json=data)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Chat message successful")
            print(f"   Response: {result['response'][:50]}...")
            print(f"   Next step: {result['nextStep']}")
            return True
        else:
            print(f"❌ Chat message failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Chat message error: {e}")
        return False

def test_text_resume_upload():
    """Test text resume upload"""
    print("\n📄 Testing text resume upload...")
    try:
        data = {
            "resumeText": TEST_RESUME_TEXT
        }
        response = requests.post(f"{BASE_URL}/upload/text-resume", json=data)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Text resume upload successful")
            print(f"   Text length: {result['data']['textLength']} characters")
            return result['data']['extractedText']
        else:
            print(f"❌ Text resume upload failed: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Text resume upload error: {e}")
        return None

def test_job_urls():
    """Test job URLs processing (using a sample job description)"""
    print("\n🌐 Testing job URLs processing...")
    try:
        # Using a sample job description instead of real URL for testing
        sample_jd = """
        Software Engineer Position
        We are looking for a Software Engineer with experience in:
        - Python programming
        - React and JavaScript
        - AWS cloud services
        - Database design with PostgreSQL
        - REST API development
        - Docker containerization
        - Git version control
        
        Requirements:
        - Bachelor's degree in Computer Science
        - 3+ years of experience
        - Strong problem-solving skills
        - Team collaboration experience
        """
        
        data = {
            "urls": ["https://example.com/job-posting"]
        }
        response = requests.post(f"{BASE_URL}/upload/job-urls", json=data)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Job URLs processing completed")
            print(f"   Processed: {result['data']['totalProcessed']} URLs")
            return result['data']['jobDescriptions']
        else:
            print(f"❌ Job URLs processing failed: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Job URLs processing error: {e}")
        return None

def test_resume_generation(resume_text, job_descriptions):
    """Test resume generation"""
    print("\n🤖 Testing resume generation...")
    try:
        data = {
            "resumeText": resume_text,
            "jobDescriptions": job_descriptions,
            "sectionPreferences": {
                "add_sections": ["skills", "projects", "experience"],
                "skip_sections": []
            },
            "templateContent": """\\documentclass[11pt,a4paper,sans]{article}
\\usepackage[utf8]{inputenc}
\\usepackage[margin=0.75in]{geometry}
\\usepackage{titlesec}
\\usepackage{enumitem}

\\titleformat{\\section}{\\large\\scshape\\raggedright}{}{0em}{}[\\color{black}\\titlerule]

\\begin{document}
\\section*{Contact Information}
Name: [Your Name] \\\\
Email: [your.email@example.com] \\\\
Phone: [Your Phone Number]

\\section*{Education}
\\textbf{[Degree]} in [Major] \\hfill [Year] \\\\
[University Name]

\\section*{Experience}
\\textbf{[Job Title]} \\hfill [Start Date - End Date] \\\\
[Company Name]
\\begin{itemize}[leftmargin=*]
    \\item [Achievement or responsibility]
\\end{itemize}

\\section*{Skills}
\\textbf{Technical Skills:} [List your technical skills]

\\end{document}""",
            "personalData": {},
            "projectsData": {}
        }
        
        print("   Generating resume (this may take a moment)...")
        response = requests.post(f"{BASE_URL}/resume/generate", json=data)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Resume generation successful")
            print(f"   Generated: {result['data']['summary']['successful']} resume(s)")
            print(f"   Failed: {result['data']['summary']['failed']} resume(s)")
            
            if result['data']['successfulResumes']:
                print("   Generated resumes:")
                for resume in result['data']['successfulResumes']:
                    print(f"     - {resume['filename']} ({resume['company']} - {resume['role']})")
            
            return result['data']['successfulResumes']
        else:
            print(f"❌ Resume generation failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Resume generation error: {e}")
        return None

def test_resume_list():
    """Test resume listing"""
    print("\n📋 Testing resume listing...")
    try:
        response = requests.get(f"{BASE_URL}/resume/list")
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Resume listing successful")
            print(f"   Total resumes: {result['data']['total']}")
            return True
        else:
            print(f"❌ Resume listing failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Resume listing error: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Starting Resume Builder Backend Tests")
    print("=" * 50)
    
    # Test 1: Health check
    if not test_health_check():
        print("\n❌ Backend is not running or not accessible")
        print("   Please start the backend first:")
        print("   cd backend && python app.py")
        return
    
    # Test 2: Chat message
    test_chat_message()
    
    # Test 3: Text resume upload
    resume_text = test_text_resume_upload()
    if not resume_text:
        print("\n❌ Cannot continue without resume text")
        return
    
    # Test 4: Job URLs processing
    job_descriptions = test_job_urls()
    if not job_descriptions:
        print("\n❌ Cannot continue without job descriptions")
        return
    
    # Test 5: Resume generation
    generated_resumes = test_resume_generation(resume_text, job_descriptions)
    
    # Test 6: Resume listing
    test_resume_list()
    
    print("\n" + "=" * 50)
    print("🎉 Test suite completed!")
    
    if generated_resumes:
        print(f"\n📄 Generated {len(generated_resumes)} resume(s)")
        print("   You can download them from the frontend or use the API directly")
    
    print("\n💡 Next steps:")
    print("   1. Start the frontend: cd frontend && npm run dev")
    print("   2. Open http://localhost:5173 in your browser")
    print("   3. Test the full user interface")

if __name__ == "__main__":
    main()
