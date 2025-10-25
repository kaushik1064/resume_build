// API service for communicating with Python backend
const API_BASE_URL = 'http://localhost:5000/api';

class ResumeAPIService {
  // Health check
  async checkHealth() {
    try {
      const response = await fetch(`${API_BASE_URL}/health`);
      return await response.json();
    } catch (error) {
      console.error('Health check failed:', error);
      throw new Error('Backend service unavailable');
    }
  }

  // Chat message handling
  async sendChatMessage(message: string, step: string) {
    try {
      const response = await fetch(`${API_BASE_URL}/chat/message`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ message, step }),
      });
      return await response.json();
    } catch (error) {
      console.error('Chat message failed:', error);
      throw new Error('Failed to send chat message');
    }
  }

  // Upload resume file
  async uploadResumeFile(file: File) {
    try {
      const formData = new FormData();
      formData.append('file', file);

      const response = await fetch(`${API_BASE_URL}/upload/resume`, {
        method: 'POST',
        body: formData,
      });
      return await response.json();
    } catch (error) {
      console.error('Resume upload failed:', error);
      throw new Error('Failed to upload resume');
    }
  }

  // Upload resume as text
  async uploadResumeText(resumeText: string) {
    try {
      const response = await fetch(`${API_BASE_URL}/upload/text-resume`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ resumeText }),
      });
      return await response.json();
    } catch (error) {
      console.error('Resume text upload failed:', error);
      throw new Error('Failed to upload resume text');
    }
  }

  // Process job URLs
  async processJobURLs(urls: string[]) {
    try {
      const response = await fetch(`${API_BASE_URL}/upload/job-urls`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ urls }),
      });
      return await response.json();
    } catch (error) {
      console.error('Job URLs processing failed:', error);
      throw new Error('Failed to process job URLs');
    }
  }

  // Generate resume
  async generateResume(data: {
    resumeText: string;
    jobDescriptions: any[];
    sectionPreferences: any;
    templateContent: string;
    personalData?: any;
    projectsData?: any;
  }) {
    try {
      console.log('🚀 Calling backend API:', `${API_BASE_URL}/resume/generate`);
      console.log('📦 Request data:', {
        resumeTextLength: data.resumeText?.length,
        jobDescriptionsCount: data.jobDescriptions?.length,
        hasPersonalData: !!data.personalData,
        hasProjectsData: !!data.projectsData
      });
      
      const response = await fetch(`${API_BASE_URL}/resume/generate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
      });
      
      console.log('📡 Response status:', response.status);
      const result = await response.json();
      console.log('📥 Response data:', result);
      
      return result;
    } catch (error) {
      console.error('❌ Resume generation failed:', error);
      throw new Error('Failed to generate resume');
    }
  }

  // Download resume
  async downloadResume(filename: string) {
    try {
      const response = await fetch(`${API_BASE_URL}/resume/download/${filename}`);
      if (!response.ok) {
        throw new Error('Download failed');
      }
      
      const blob = await response.blob();
      const url = URL.createObjectURL(blob);
      
      // Create download link
      const link = document.createElement('a');
      link.href = url;
      link.download = filename;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      
      // Clean up
      URL.revokeObjectURL(url);
      
      return { success: true };
    } catch (error) {
      console.error('Resume download failed:', error);
      throw new Error('Failed to download resume');
    }
  }

  // List generated resumes
  async listResumes() {
    try {
      const response = await fetch(`${API_BASE_URL}/resume/list`);
      return await response.json();
    } catch (error) {
      console.error('List resumes failed:', error);
      throw new Error('Failed to list resumes');
    }
  }

  // Extract personal data from resume text
  async extractPersonalData(resumeText: string) {
    try {
      const response = await fetch(`${API_BASE_URL}/extract/personal`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ resumeText }),
      });
      return await response.json();
    } catch (error) {
      console.error('Personal data extraction failed:', error);
      throw new Error('Failed to extract personal data');
    }
  }

  // Extract projects data from resume text
  async extractProjectsData(resumeText: string) {
    try {
      const response = await fetch(`${API_BASE_URL}/extract/projects`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ resumeText }),
      });
      return await response.json();
    } catch (error) {
      console.error('Projects data extraction failed:', error);
      throw new Error('Failed to extract projects data');
    }
  }

  // Get template content
  async getTemplate() {
    try {
      const response = await fetch(`${API_BASE_URL}/template`);
      return await response.json();
    } catch (error) {
      console.error('Template fetch failed:', error);
      throw new Error('Failed to get template');
    }
  }

  // Analyze resume sections
  async analyzeResumeSections(resumeText: string) {
    try {
      const response = await fetch(`${API_BASE_URL}/analyze/sections`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ resumeText }),
      });
      return await response.json();
    } catch (error) {
      console.error('Section analysis failed:', error);
      throw new Error('Failed to analyze resume sections');
    }
  }

  // Analyze domain compatibility
  async analyzeDomainCompatibility(resumeText: string, jobDescriptions: any[]) {
    try {
      const response = await fetch(`${API_BASE_URL}/analyze/domain`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ resumeText, jobDescriptions }),
      });
      return await response.json();
    } catch (error) {
      console.error('Domain analysis failed:', error);
      throw new Error('Failed to analyze domain compatibility');
    }
  }
}

export const resumeAPI = new ResumeAPIService();
