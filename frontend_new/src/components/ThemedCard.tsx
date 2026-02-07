'use client';

import React from 'react';
import { useTheme } from '@/context/ThemeContext';

interface ThemedCardProps {
  children: React.ReactNode;
  className?: string;
}

export default function ThemedCard({ children, className = '' }: ThemedCardProps) {
  const { theme } = useTheme();
  
  const baseClasses = "rounded-lg shadow-md p-6 transition-all duration-300";
  const themeClasses = theme === 'dark' 
    ? "bg-gray-800 text-white border border-gray-700" 
    : "bg-white text-gray-900 border border-gray-200";
  
  return (
    <div className={`${baseClasses} ${themeClasses} ${className}`}>
      {children}
    </div>
  );
}