import React from 'react';

interface ResumeIconProps {
  className?: string;
  size?: number;
}

export function ResumeIcon({ className = "", size = 24 }: ResumeIconProps) {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill="none"
      className={className}
      xmlns="http://www.w3.org/2000/svg"
    >
      {/* Apple-style rounded square background */}
      <rect
        x="2"
        y="2"
        width="20"
        height="20"
        rx="4.5"
        ry="4.5"
        fill="url(#gradient)"
        stroke="rgba(255, 255, 255, 0.2)"
        strokeWidth="0.5"
      />
      
      {/* Gradient definition */}
      <defs>
        <linearGradient id="gradient" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stopColor="#FF6B35" />
          <stop offset="50%" stopColor="#F7931E" />
          <stop offset="100%" stopColor="#FFD23F" />
        </linearGradient>
        
        {/* Inner shadow gradient */}
        <linearGradient id="innerShadow" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stopColor="rgba(255, 255, 255, 0.3)" />
          <stop offset="50%" stopColor="rgba(255, 255, 255, 0.1)" />
          <stop offset="100%" stopColor="rgba(0, 0, 0, 0.1)" />
        </linearGradient>
      </defs>
      
      {/* Inner shadow overlay */}
      <rect
        x="2"
        y="2"
        width="20"
        height="20"
        rx="4.5"
        ry="4.5"
        fill="url(#innerShadow)"
      />
      
      {/* Letter R - Clean Single Path */}
      <path
        d="M8 6h4c1.5 0 2.5 1 2.5 2.5s-1 2.5-2.5 2.5h-2v1.5l2.5 3h-2.5l-2-2.5v2.5h-2V6zm2 2h2c0.5 0 1-0.5 1-1s-0.5-1-1-1h-2v2z"
        fill="white"
        stroke="rgba(255, 255, 255, 0.1)"
        strokeWidth="0.1"
      />
      
      {/* Highlight effect */}
      <rect
        x="3"
        y="3"
        width="18"
        height="18"
        rx="4"
        ry="4"
        fill="none"
        stroke="rgba(255, 255, 255, 0.4)"
        strokeWidth="0.5"
      />
    </svg>
  );
}

// Alternative simpler version
export function ResumeIconSimple({ className = "", size = 24 }: ResumeIconProps) {
  return (
    <div
      className={`flex items-center justify-center rounded-lg bg-gradient-to-br from-orange-500 to-red-500 text-white font-bold shadow-lg ${className}`}
      style={{ width: size, height: size }}
    >
      <span style={{ fontSize: size * 0.6 }}>R</span>
    </div>
  );
}
