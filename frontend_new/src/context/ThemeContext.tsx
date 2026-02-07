'use client';

import React, { createContext, useContext, useEffect, useState } from 'react';
import { getStorageItem, setStorageItem } from '../utils/storage';

type Theme = 'light' | 'dark' | 'system';

interface ThemeContextType {
  theme: Theme;
  setTheme: (theme: Theme) => void;
}

const ThemeContext = createContext<ThemeContextType | undefined>(undefined);

export function ThemeProvider({ children }: { children: React.ReactNode }) {
  const [theme, setTheme] = useState<Theme>('system');
  const [resolvedTheme, setResolvedTheme] = useState<'light' | 'dark'>('light');
  const [isMounted, setIsMounted] = useState(false);

  // Get saved theme from localStorage or default to 'system'
  useEffect(() => {
    const savedTheme = getStorageItem('theme') as Theme | null;
    if (savedTheme) {
      setTheme(savedTheme);
    }
    setIsMounted(true);
  }, []);

  // Apply theme changes
  useEffect(() => {
    if (typeof window === 'undefined' || !isMounted) return;

    const root = window.document.documentElement;

    // Determine the actual theme based on user preference or system
    let actualTheme: 'light' | 'dark' = 'light';

    if (theme === 'system') {
      actualTheme = window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
    } else {
      actualTheme = theme;
    }

    // Update the DOM
    root.classList.remove('light', 'dark');
    root.classList.add(actualTheme);
    root.setAttribute('data-theme', actualTheme);

    // Store the resolved theme for consumers
    setResolvedTheme(actualTheme);

    // Save to localStorage
    setStorageItem('theme', theme);
  }, [theme, isMounted]);

  // Listen for system theme changes
  useEffect(() => {
    if (theme !== 'system' || !isMounted) return;

    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
    const handleChange = () => {
      const newTheme = mediaQuery.matches ? 'dark' : 'light';
      setResolvedTheme(newTheme);
    };

    mediaQuery.addEventListener('change', handleChange);
    return () => mediaQuery.removeEventListener('change', handleChange);
  }, [theme, isMounted]);

  return (
    <ThemeContext.Provider value={{ theme, setTheme }}>
      {children}
    </ThemeContext.Provider>
  );
}

export function useTheme() {
  const context = useContext(ThemeContext);
  if (context === undefined) {
    throw new Error('useTheme must be used within a ThemeProvider');
  }
  return context;
}