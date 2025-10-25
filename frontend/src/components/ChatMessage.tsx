import { Bot, User } from 'lucide-react';

type Message = {
  id: string;
  text: string;
  sender: 'bot' | 'user';
  timestamp: Date;
};

export function ChatMessage({ message }: { message: Message }) {
  const isBot = message.sender === 'bot';

  return (
    <div className={`flex ${isBot ? 'justify-start' : 'justify-end'} animate-in fade-in slide-in-from-bottom-2 duration-300`}>
      <div className={`flex gap-3 max-w-[80%] ${!isBot && 'flex-row-reverse'}`}>
        {/* Avatar */}
        <div
          className={`w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0 shadow-md ${
            isBot
              ? 'bg-gradient-to-br from-orange-500 to-red-500'
              : 'bg-gradient-to-br from-orange-600 to-red-600'
          }`}
        >
          {isBot ? (
            <Bot className="w-4 h-4 text-white" />
          ) : (
            <User className="w-4 h-4 text-white" />
          )}
        </div>

        {/* Message Bubble - Ultra Glass Effect */}
        <div
          className={`px-4 py-3 rounded-2xl backdrop-blur-xl border relative ${
            isBot
              ? 'bg-white/40 text-gray-900 rounded-tl-sm border-white/50'
              : 'bg-gradient-to-br from-orange-500 to-red-500 text-white rounded-tr-sm border-white/30'
          }`}
          style={isBot ? {
            boxShadow: `
              0 4px 16px 0 rgba(0, 0, 0, 0.08),
              inset 0 2px 3px 0 rgba(255, 255, 255, 0.6),
              inset 0 -1px 2px 0 rgba(0, 0, 0, 0.05),
              inset 1px 0 2px 0 rgba(255, 255, 255, 0.4)
            `
          } : {
            boxShadow: '0 4px 12px 0 rgba(255, 87, 34, 0.3)'
          }}
        >
          {isBot && (
            <>
              <div className="absolute inset-0 bg-gradient-to-b from-white/30 via-white/10 to-transparent pointer-events-none rounded-2xl" style={{ height: '50%' }} />
              <div className="absolute top-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-white/70 to-transparent rounded-t-2xl" />
              <div className="absolute inset-0 bg-gradient-to-br from-white/20 via-transparent to-transparent pointer-events-none rounded-2xl" style={{ width: '40%', height: '40%' }} />
            </>
          )}
          <p className="text-sm leading-relaxed relative z-10">{message.text}</p>
          <span className={`text-xs mt-1 block relative z-10 ${isBot ? 'text-gray-800' : 'text-white/90'}`}>
            {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
          </span>
        </div>
      </div>
    </div>
  );
}
