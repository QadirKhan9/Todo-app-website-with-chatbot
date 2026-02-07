'use client';

import React, { useState, useRef, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from './AuthProvider';

interface DropdownItem {
  label: string;
  onClick?: () => void;
  disabled?: boolean;
}

interface DropdownProps {
  triggerElement: React.ReactNode;
  items: DropdownItem[];
  position?: 'left' | 'right';
}

const Dropdown: React.FC<DropdownProps> = ({
  triggerElement,
  items,
  position = 'right'
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);
  const { user, logout } = useAuth();
  const router = useRouter();

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, []);

  // Handle keyboard accessibility
  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.key === 'Escape' && isOpen) {
        setIsOpen(false);
      }
    };

    document.addEventListener('keydown', handleKeyDown);
    return () => {
      document.removeEventListener('keydown', handleKeyDown);
    };
  }, [isOpen]);

  const handleLogout = () => {
    logout();
    router.push('/login'); // Redirect to login page after logout
    setIsOpen(false);
  };

  return (
    <div className="relative inline-block text-left" ref={dropdownRef}>
      <div
        onClick={() => setIsOpen(!isOpen)}
        className="cursor-pointer flex items-center"
        role="button"
        tabIndex={0}
        onKeyDown={(e) => {
          if (e.key === 'Enter' || e.key === ' ') {
            setIsOpen(!isOpen);
          }
        }}
      >
        {triggerElement}
      </div>

      {isOpen && (
        <div
          className={`
            origin-top-right absolute z-50 mt-2 w-56 rounded-md shadow-lg
            bg-white dark:bg-gray-800 ring-1 ring-black ring-opacity-5
            focus:outline-none transition-all duration-200 ease-in-out
            ${position === 'right' ? 'right-0' : 'left-0'}
          `}
          role="menu"
          aria-orientation="vertical"
          aria-labelledby="options-menu"
        >
          <div className="py-1">
            {/* User email item */}
            <div
              className="block px-4 py-2 text-sm text-gray-700 dark:text-gray-300 cursor-default"
              role="menuitem"
            >
              {user?.email || 'Account'}
            </div>

            {/* Divider */}
            <div className="border-t border-gray-200 dark:border-gray-700 my-1"></div>

            {/* Logout button */}
            <button
              onClick={handleLogout}
              className="block w-full text-left px-4 py-2 text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700"
              role="menuitem"
            >
              Logout
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default Dropdown;