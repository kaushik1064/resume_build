import { useState, useRef, useEffect } from 'react';
import { Send, Download, FileText, AlertCircle } from 'lucide-react';
import { Button } from './ui/button';
import { ChatMessage } from './ChatMessage';
import { FileUploadStep } from './FileUploadStep';
import { URLInputStep } from './URLInputStep';
import { resumeAPI } from '../services/api';

type Message = {
  id: string;
  text: string;
  sender: 'bot' | 'user';
  timestamp: Date;
};

type ConversationStep = 
  | 'initial'
  | 'awaiting_resume'
  | 'awaiting_urls'
  | 'awaiting_missing_sections'
  | 'generating'
  | 'complete';

type ResumeData = {
  file?: File;
  fileText?: string;
  urls: string[];
  missingSections?: string;
  jobDescriptions?: any[];
  personalData?: any;
  projectsData?: any;
  templateContent?: string;
};

export function ChatInterface() {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      text: "Hi! I'm your Resume Assistant. I'll help you create a professional resume. Would you like to get started?",
      sender: 'bot',
      timestamp: new Date(),
    },
  ]);
  const [inputValue, setInputValue] = useState('');
  const [step, setStep] = useState<ConversationStep>('initial');
  const [resumeData, setResumeData] = useState<ResumeData>({
    urls: [],
  });
  const [downloadUrls, setDownloadUrls] = useState<string[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const chatContainerRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, step]);

  const addMessage = (text: string, sender: 'bot' | 'user') => {
    const newMessage: Message = {
      id: Date.now().toString(),
      text,
      sender,
      timestamp: new Date(),
    };
    setMessages((prev) => [...prev, newMessage]);
  };

  const handleSendMessage = async () => {
    if (!inputValue.trim() || isLoading) return;

    const userMessage = inputValue;
    addMessage(userMessage, 'user');
    setInputValue('');
    
    // Handle initial conversation start
    if (step === 'initial') {
      setTimeout(() => {
        addMessage(
          "Great! Let's start by getting your current resume. You can either upload a file (PDF, DOC, DOCX) or paste your resume text using the options below.",
          'bot'
        );
        setStep('awaiting_resume');
      }, 500);
      return;
    }
    
    // Special handling for missing sections step - this triggers resume generation
    if (step === 'awaiting_missing_sections') {
      setResumeData(prev => ({ ...prev, missingSections: userMessage }));
      addMessage("Perfect! I've noted that you want to add: " + userMessage + ". I'm now generating your resume. This will take just a moment...", 'bot');
      setStep('generating');
      
      // Trigger resume generation
      setTimeout(() => {
        generateResume();
      }, 500);
      return;
    }
    
    setIsLoading(true);
    setError(null);

    try {
      const response = await resumeAPI.sendChatMessage(userMessage, step);
      
      if (response.success) {
        addMessage(response.response, 'bot');
        
        if (response.nextStep) {
          setStep(response.nextStep as ConversationStep);
        }
        
        if (response.data) {
          setResumeData(prev => ({ ...prev, ...response.data }));
        }
      } else {
        setError(response.error || 'Failed to process message');
      }
    } catch (error) {
      console.error('Chat error:', error);
      setError('Failed to connect to backend. Please make sure the backend is running.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleFileUpload = async (file: File, text?: string) => {
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await resumeAPI.uploadResumeFile(file);
      
      if (response.success) {
        setResumeData((prev) => ({ 
          ...prev, 
          file, 
          fileText: response.data.extractedText 
        }));
        addMessage(`Uploaded: ${file.name}`, 'user');
        
        setTimeout(() => {
          addMessage(
            "Excellent! I've received your resume. Now, please provide any relevant URLs you'd like to include (LinkedIn, portfolio, GitHub, etc.). You can add them using the fields below.",
            'bot'
          );
          setStep('awaiting_urls');
        }, 500);
      } else {
        setError(response.error || 'Failed to upload resume');
      }
    } catch (error) {
      console.error('File upload error:', error);
      setError('Failed to upload resume file');
    } finally {
      setIsLoading(false);
    }
  };

  const handleURLsSubmit = async (urls: string[]) => {
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await resumeAPI.processJobURLs(urls);
      
      if (response.success) {
        setResumeData((prev) => ({ 
          ...prev, 
          urls,
          jobDescriptions: response.data.jobDescriptions 
        }));
        addMessage(`Added ${urls.length} URL(s)`, 'user');
        
        setTimeout(() => {
          addMessage(
            "Great! Are there any specific sections you'd like me to add or emphasize in your resume? (e.g., certifications, projects, skills, etc.) Type your response below.",
            'bot'
          );
          setStep('awaiting_missing_sections');
        }, 500);
      } else {
        setError(response.error || 'Failed to process URLs');
      }
    } catch (error) {
      console.error('URL processing error:', error);
      setError('Failed to process job URLs');
    } finally {
      setIsLoading(false);
    }
  };

  const generateResume = async () => {
    setIsLoading(true);
    setError(null);
    
    console.log('🎯 Starting resume generation...');
    console.log('📊 Current resumeData:', {
      hasFile: !!resumeData.file,
      hasFileText: !!resumeData.fileText,
      fileTextLength: resumeData.fileText?.length,
      urlsCount: resumeData.urls?.length,
      jobDescriptionsCount: resumeData.jobDescriptions?.length,
      hasMissingSections: !!resumeData.missingSections
    });
    
    try {
      // First, extract personal data and projects data
      console.log('📝 Extracting personal data...');
      const personalDataResponse = await resumeAPI.sendChatMessage(
        resumeData.fileText || '', 
        'extract_personal'
      );
      console.log('✅ Personal data extracted:', personalDataResponse);
      
      console.log('📝 Extracting projects data...');
      const projectsDataResponse = await resumeAPI.sendChatMessage(
        resumeData.fileText || '', 
        'extract_projects'
      );
      console.log('✅ Projects data extracted:', projectsDataResponse);

      // Prepare data for resume generation
      const generationData = {
        resumeText: resumeData.fileText || '',
        jobDescriptions: resumeData.jobDescriptions || [],
        sectionPreferences: {
          add_sections: resumeData.missingSections ? ['skills', 'projects', 'experience'] : [],
          skip_sections: []
        },
        templateContent: `% Professional Resume Template
\\documentclass[11pt,a4paper,sans]{article}
\\usepackage[utf8]{inputenc}
\\usepackage[margin=0.75in]{geometry}
\\usepackage{titlesec}
\\usepackage{enumitem}
\\usepackage{hyperref}
\\usepackage{xcolor}

% Custom section formatting
\\titleformat{\\section}{\\large\\scshape\\raggedright}{}{0em}{}[\\color{black}\\titlerule]
\\titleformat{\\subsection}{\\normalsize\\scshape\\raggedright}{}{0em}{}

% Remove page numbers
\\pagestyle{empty}

\\begin{document}

% Contact Information
\\section*{Contact Information}
Name: [Your Name] \\\\
Email: [your.email@example.com] \\\\
Phone: [Your Phone Number] \\\\
LinkedIn: [Your LinkedIn URL] \\\\
GitHub: [Your GitHub URL] \\\\
Location: [Your Location]

% Education
\\section*{Education}
\\textbf{[Degree]} in [Major] \\hfill [Year] \\\\
[University Name] \\hfill [Location] \\\\
GPA: [GPA if mentioned]

% Experience
\\section*{Professional Experience}
\\textbf{[Job Title]} \\hfill [Start Date - End Date] \\\\
[Company Name] \\hfill [Location]
\\begin{itemize}[leftmargin=*]
    \\item [Achievement or responsibility with metrics]
    \\item [Another achievement or responsibility]
    \\item [Third achievement highlighting relevant skills]
\\end{itemize}

\\textbf{[Previous Job Title]} \\hfill [Start Date - End Date] \\\\
[Previous Company Name] \\hfill [Location]
\\begin{itemize}[leftmargin=*]
    \\item [Achievement or responsibility]
    \\item [Another achievement or responsibility]
\\end{itemize}

% Projects
\\section*{Projects}
\\textbf{[Project Name]} \\hfill [Date] \\\\
[Brief description of the project and its impact]
\\begin{itemize}[leftmargin=*]
    \\item [Key feature or accomplishment with technologies used]
    \\item [Another feature highlighting relevant skills]
    \\item [Outcome or result achieved]
\\end{itemize}

\\textbf{[Another Project Name]} \\hfill [Date] \\\\
[Brief description of the project]
\\begin{itemize}[leftmargin=*]
    \\item [Key feature or accomplishment]
    \\item [Technologies and tools used]
\\end{itemize}

% Skills
\\section*{Technical Skills}
\\textbf{Programming Languages:} [List programming languages] \\\\
\\textbf{Frameworks \\& Libraries:} [List frameworks and libraries] \\\\
\\textbf{Tools \\& Technologies:} [List tools and technologies] \\\\
\\textbf{Databases:} [List databases] \\\\
\\textbf{Cloud Platforms:} [List cloud platforms]

% Certifications (if applicable)
\\section*{Certifications}
\\textbf{[Certification Name]} \\hfill [Date] \\\\
[Issuing Organization]

\\end{document}`,
        personalData: personalDataResponse.success ? personalDataResponse.data : {},
        projectsData: projectsDataResponse.success ? projectsDataResponse.data : {}
      };

      const response = await resumeAPI.generateResume(generationData);
      
      if (response.success) {
        const successfulResumes = response.data.successfulResumes;
        setDownloadUrls(successfulResumes.map((r: any) => r.downloadUrl));
        
        addMessage(
          `Your ${successfulResumes.length} resume(s) have been generated successfully! You can download them using the buttons below.`,
          'bot'
        );
        
        // Auto-download the first resume
        if (successfulResumes.length > 0) {
          try {
            await resumeAPI.downloadResume(successfulResumes[0].filename);
          } catch (downloadError) {
            console.error('Auto-download failed:', downloadError);
          }
        }
        
        setStep('complete');
      } else {
        setError(response.error || 'Failed to generate resume');
      }
    } catch (error) {
      console.error('❌ Resume generation error:', error);
      setError(`Failed to generate resume: ${error instanceof Error ? error.message : 'Unknown error'}`);
      addMessage(`Sorry, there was an error generating your resume: ${error instanceof Error ? error.message : 'Unknown error'}. Please try again.`, 'bot');
      setStep('awaiting_missing_sections');
    } finally {
      setIsLoading(false);
    }
  };

  const handleDownload = async (filename: string) => {
    try {
      await resumeAPI.downloadResume(filename);
    } catch (error) {
      console.error('Download error:', error);
      setError('Failed to download resume');
    }
  };

  return (
    <div className="w-full max-w-4xl mx-auto relative z-10">
      {/* Chat Container with Ultra Glass Effect */}
      <div
        ref={chatContainerRef}
        className="backdrop-blur-[80px] bg-white/[0.01] rounded-[2.5rem] border border-white/40 overflow-hidden transition-all duration-500 relative"
        style={{
          minHeight: step === 'awaiting_resume' || step === 'awaiting_urls' ? '600px' : '500px',
          background: 'linear-gradient(135deg, rgba(255, 255, 255, 0.1) 0%, rgba(255, 255, 255, 0.01) 50%, rgba(255, 255, 255, 0.05) 100%)',
          boxShadow: `
            0 8px 32px 0 rgba(0, 0, 0, 0.1),
            0 2px 16px 0 rgba(0, 0, 0, 0.06),
            inset 0 2px 4px 0 rgba(255, 255, 255, 0.6),
            inset 0 -2px 4px 0 rgba(0, 0, 0, 0.05),
            inset 2px 0 4px 0 rgba(255, 255, 255, 0.3),
            inset -2px 0 4px 0 rgba(0, 0, 0, 0.03)
          `,
        }}
      >
        {/* Primary glass reflection - top */}
        <div className="absolute inset-0 bg-gradient-to-b from-white/40 via-white/10 to-transparent pointer-events-none rounded-[2.5rem]" style={{ height: '35%' }} />
        
        {/* Secondary glass reflection - curved */}
        <div className="absolute inset-0 bg-gradient-to-br from-white/20 via-transparent to-transparent pointer-events-none rounded-[2.5rem]" style={{ width: '50%', height: '50%' }} />
        
        {/* Glass edge highlights */}
        <div className="absolute inset-0 rounded-[2.5rem] pointer-events-none" style={{
          boxShadow: `
            inset 0 2px 2px 0 rgba(255, 255, 255, 0.6),
            inset 0 -1px 2px 0 rgba(0, 0, 0, 0.1),
            inset 2px 0 2px 0 rgba(255, 255, 255, 0.4),
            inset -2px 0 2px 0 rgba(255, 255, 255, 0.2)
          `
        }} />
        
        {/* Subtle refraction effect */}
        <div className="absolute top-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-white/60 to-transparent" />
        
        {/* Header */}
        <div className="relative backdrop-blur-xl bg-white/[0.02] border-b border-white/30 p-6">
          <div className="absolute inset-0 bg-gradient-to-b from-white/20 via-transparent to-transparent pointer-events-none" style={{ height: '60%' }} />
          <div className="flex items-center gap-3 relative z-10">
            <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-orange-500 to-red-500 flex items-center justify-center shadow-lg">
              <FileText className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-gray-900">Resume Assistant</h1>
              <p className="text-sm text-gray-800">AI-powered resume creator</p>
            </div>
          </div>
        </div>

        {/* Messages Area */}
        <div className="h-96 overflow-y-auto p-6 space-y-4 relative">
          {messages.map((message) => (
            <ChatMessage key={message.id} message={message} />
          ))}

          {/* File Upload Step */}
          {step === 'awaiting_resume' && (
            <FileUploadStep onFileUpload={handleFileUpload} />
          )}

          {/* URL Input Step */}
          {step === 'awaiting_urls' && (
            <URLInputStep onSubmit={handleURLsSubmit} />
          )}

          {/* Generating indicator */}
          {step === 'generating' && (
            <div className="flex justify-start">
              <div className="backdrop-blur-xl bg-white/40 rounded-2xl p-4 max-w-md border border-white/50 relative" style={{
                boxShadow: `
                  0 4px 16px 0 rgba(0, 0, 0, 0.08),
                  inset 0 2px 3px 0 rgba(255, 255, 255, 0.6),
                  inset 0 -1px 2px 0 rgba(0, 0, 0, 0.05)
                `
              }}>
                <div className="absolute inset-0 bg-gradient-to-b from-white/30 via-transparent to-transparent pointer-events-none rounded-2xl" style={{ height: '50%' }} />
                <div className="absolute top-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-white/70 to-transparent rounded-t-2xl" />
                <div className="flex items-center gap-3 relative z-10">
                  <div className="flex gap-1">
                    <div className="w-2 h-2 bg-orange-500 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                    <div className="w-2 h-2 bg-orange-500 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                    <div className="w-2 h-2 bg-red-500 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
                  </div>
                  <span className="text-sm text-gray-900">Generating your resume...</span>
                </div>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Error Display */}
        {error && (
          <div className="border-t border-red-200 p-4 backdrop-blur-xl bg-red-50/[0.02] relative">
            <div className="flex items-center gap-3 text-red-600">
              <AlertCircle className="w-5 h-5" />
              <span className="text-sm">{error}</span>
            </div>
          </div>
        )}

        {/* Input Area */}
        {step !== 'awaiting_resume' && step !== 'awaiting_urls' && step !== 'generating' && (
          <div className="border-t border-white/30 p-4 backdrop-blur-xl bg-white/[0.02] relative">
            <div className="absolute inset-0 bg-gradient-to-b from-transparent via-transparent to-white/10 pointer-events-none" />
            <div className="flex gap-2 relative z-10">
              <div className="flex-1 relative">
                <input
                  type="text"
                  value={inputValue}
                  onChange={(e) => setInputValue(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && !isLoading && handleSendMessage()}
                  placeholder={isLoading ? "Processing..." : "Type your message..."}
                  disabled={isLoading}
                  className="w-full px-5 py-3 rounded-xl backdrop-blur-xl bg-white/40 border border-white/50 focus:outline-none focus:ring-2 focus:ring-orange-400 focus:border-orange-400 placeholder-gray-700 text-gray-900 disabled:opacity-50"
                  style={{
                    boxShadow: `
                      inset 0 2px 4px 0 rgba(0, 0, 0, 0.08),
                      inset 0 1px 2px 0 rgba(255, 255, 255, 0.5),
                      0 1px 3px 0 rgba(255, 255, 255, 0.6)
                    `
                  }}
                />
                <div className="absolute top-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-white/60 to-transparent rounded-t-xl" />
              </div>
              <Button
                onClick={handleSendMessage}
                disabled={isLoading || !inputValue.trim()}
                className="px-6 bg-gradient-to-br from-orange-500 to-red-500 hover:from-orange-600 hover:to-red-600 text-white rounded-xl shadow-lg border-0 disabled:opacity-50"
              >
                <Send className="w-5 h-5" />
              </Button>
            </div>
          </div>
        )}
      </div>

      {/* Download Buttons (appears after generation) */}
      {step === 'complete' && downloadUrls.length > 0 && (
        <div className="mt-6 flex flex-col items-center gap-4">
          <h3 className="text-lg font-semibold text-gray-900">Download Your Resumes</h3>
          <div className="flex flex-wrap gap-3 justify-center">
            {downloadUrls.map((url, index) => {
              const filename = url.split('/').pop() || `resume_${index + 1}.pdf`;
              return (
                <Button
                  key={index}
                  onClick={() => handleDownload(filename)}
                  className="px-6 py-3 bg-gradient-to-br from-orange-500 to-red-500 hover:from-orange-600 hover:to-red-600 text-white rounded-xl shadow-lg"
                >
                  <Download className="w-4 h-4 mr-2" />
                  Download Resume {index + 1}
                </Button>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}
