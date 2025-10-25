import { useState } from 'react';
import { Plus, X, Link as LinkIcon } from 'lucide-react';
import { Button } from './ui/button';
import { Input } from './ui/input';

type URLInputStepProps = {
  onSubmit: (urls: string[]) => void;
};

export function URLInputStep({ onSubmit }: URLInputStepProps) {
  const [urls, setUrls] = useState<string[]>(['']);

  const addURLField = () => {
    setUrls([...urls, '']);
  };

  const removeURLField = (index: number) => {
    setUrls(urls.filter((_, i) => i !== index));
  };

  const updateURL = (index: number, value: string) => {
    const newUrls = [...urls];
    newUrls[index] = value;
    setUrls(newUrls);
  };

  const handleSubmit = () => {
    const validUrls = urls.filter((url) => url.trim() !== '');
    onSubmit(validUrls);
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
          <div className="flex items-center gap-2 mb-4">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-orange-500 to-red-500 flex items-center justify-center shadow-md">
              <LinkIcon className="w-4 h-4 text-white" />
            </div>
            <h3 className="text-gray-900">Add Your URLs</h3>
          </div>

          {/* URL Input Fields */}
          <div className="space-y-3 max-h-64 overflow-y-auto pr-2">
            {urls.map((url, index) => (
              <div key={index} className="flex gap-2">
                <div className="flex-1 relative">
                  <Input
                    type="url"
                    value={url}
                    onChange={(e) => updateURL(index, e.target.value)}
                    placeholder={`URL ${index + 1} (e.g., LinkedIn, Portfolio, GitHub)`}
                    className="w-full backdrop-blur-md bg-white/35 border-white/60 placeholder-gray-700 text-gray-900"
                    style={{
                      boxShadow: `
                        inset 0 2px 4px 0 rgba(0, 0, 0, 0.08),
                        inset 0 1px 2px 0 rgba(255, 255, 255, 0.5),
                        0 1px 3px 0 rgba(255, 255, 255, 0.5)
                      `
                    }}
                  />
                  <div className="absolute top-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-white/60 to-transparent rounded-t-md pointer-events-none" />
                </div>
                {urls.length > 1 && (
                  <Button
                    onClick={() => removeURLField(index)}
                    variant="outline"
                    size="icon"
                    className="backdrop-blur-md bg-white/35 border-white/60 hover:bg-red-100/50 text-gray-900"
                  >
                    <X className="w-4 h-4" />
                  </Button>
                )}
              </div>
            ))}
          </div>

          {/* Add More Button */}
          <Button
            onClick={addURLField}
            variant="outline"
            className="w-full backdrop-blur-md bg-white/30 border-white/60 hover:bg-white/40 text-gray-900"
          >
            <Plus className="w-4 h-4 mr-2" />
            Add Another URL
          </Button>

          {/* Submit Button */}
          <Button
            onClick={handleSubmit}
            className="w-full bg-gradient-to-br from-orange-500 to-red-500 hover:from-orange-600 hover:to-red-600 text-white py-6 rounded-xl shadow-lg"
          >
            Continue
          </Button>
        </div>
      </div>
    </div>
  );
}
