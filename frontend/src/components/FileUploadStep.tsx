import { useState, useRef } from 'react';
import { Upload, FileText, X } from 'lucide-react';
import { Button } from './ui/button';
import { Textarea } from './ui/textarea';

type FileUploadStepProps = {
  onFileUpload: (file: File, text?: string) => void;
};

export function FileUploadStep({ onFileUpload }: FileUploadStepProps) {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [textInput, setTextInput] = useState('');
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setSelectedFile(file);
    }
  };

  const handleSubmit = () => {
    if (selectedFile) {
      onFileUpload(selectedFile, textInput || undefined);
    } else if (textInput.trim()) {
      // Create a text file from the input
      const blob = new Blob([textInput], { type: 'text/plain' });
      const file = new File([blob], 'resume-details.txt', { type: 'text/plain' });
      onFileUpload(file, textInput);
    }
  };

  const clearFile = () => {
    setSelectedFile(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  return (
    <div className="flex justify-start animate-in fade-in slide-in-from-bottom-4 duration-500">
      <div className="backdrop-blur-xl bg-white/35 rounded-2xl p-6 max-w-xl w-full border border-white/50 relative" style={{
        boxShadow: `
          0 4px 20px 0 rgba(0, 0, 0, 0.1),
          inset 0 2px 4px 0 rgba(255, 255, 255, 0.6),
          inset 0 -1px 3px 0 rgba(0, 0, 0, 0.05),
          inset 2px 0 3px 0 rgba(255, 255, 255, 0.3)
        `
      }}>
        {/* Primary glass highlight */}
        <div className="absolute inset-0 bg-gradient-to-b from-white/35 via-white/10 to-transparent pointer-events-none rounded-2xl" style={{ height: '40%' }} />
        
        {/* Top edge reflection */}
        <div className="absolute top-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-white/70 to-transparent rounded-t-2xl" />
        
        {/* Corner highlights */}
        <div className="absolute inset-0 bg-gradient-to-br from-white/25 via-transparent to-transparent pointer-events-none rounded-2xl" style={{ width: '35%', height: '35%' }} />
        
        <div className="space-y-4 relative z-10">
          {/* File Upload Area */}
          <div>
            <label className="block text-sm mb-2 text-gray-900">Upload Resume File</label>
            <div
              onClick={() => fileInputRef.current?.click()}
              className="border-2 border-dashed border-white/60 rounded-xl p-6 cursor-pointer hover:border-white/80 hover:bg-white/15 transition-all backdrop-blur-md bg-white/[0.12] relative"
              style={{
                boxShadow: `
                  inset 0 2px 3px 0 rgba(255, 255, 255, 0.4),
                  inset 0 -1px 2px 0 rgba(0, 0, 0, 0.05)
                `
              }}
            >
              <div className="absolute top-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-white/50 to-transparent rounded-t-xl" />
              <input
                ref={fileInputRef}
                type="file"
                onChange={handleFileSelect}
                accept=".pdf,.doc,.docx,.txt"
                className="hidden"
              />
              <div className="flex flex-col items-center gap-2 text-center">
                <div className="w-12 h-12 rounded-lg bg-gradient-to-br from-orange-500 to-red-500 flex items-center justify-center shadow-md">
                  <Upload className="w-6 h-6 text-white" />
                </div>
                <p className="text-sm text-gray-900">
                  {selectedFile ? (
                    <span className="flex items-center gap-2">
                      <FileText className="w-4 h-4" />
                      {selectedFile.name}
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          clearFile();
                        }}
                        className="text-red-600 hover:text-red-800 transition-colors"
                      >
                        <X className="w-4 h-4" />
                      </button>
                    </span>
                  ) : (
                    <>
                      <span className="text-gray-900">Click to upload</span> or drag and drop
                    </>
                  )}
                </p>
                <p className="text-xs text-gray-800">PDF, DOC, DOCX or TXT</p>
              </div>
            </div>
          </div>

          {/* Text Input Area */}
          <div>
            <label className="block text-sm mb-2 text-gray-900">Or Paste Your Details</label>
            <div className="relative">
              <Textarea
                value={textInput}
                onChange={(e) => setTextInput(e.target.value)}
                placeholder="Paste your resume details here..."
                className="min-h-32 backdrop-blur-md bg-white/35 border-white/60 placeholder-gray-700 text-gray-900 resize-none"
                style={{
                  boxShadow: `
                    inset 0 2px 4px 0 rgba(0, 0, 0, 0.08),
                    inset 0 1px 2px 0 rgba(255, 255, 255, 0.5),
                    0 1px 3px 0 rgba(255, 255, 255, 0.5)
                  `
                }}
              />
              <div className="absolute top-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-white/60 to-transparent rounded-t-lg pointer-events-none" />
            </div>
          </div>

          {/* Submit Button */}
          <Button
            onClick={handleSubmit}
            disabled={!selectedFile && !textInput.trim()}
            className="w-full bg-gradient-to-br from-orange-500 to-red-500 hover:from-orange-600 hover:to-red-600 text-white py-6 rounded-xl disabled:opacity-50 shadow-lg"
          >
            Continue
          </Button>
        </div>
      </div>
    </div>
  );
}
