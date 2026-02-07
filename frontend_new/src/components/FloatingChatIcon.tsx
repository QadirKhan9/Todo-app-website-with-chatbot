'use client';

import { useState, useEffect } from 'react';
import { useAuth } from './AuthProvider';
import ChatInterface from './ChatInterface';

const FloatingChatIcon = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [showIcon, setShowIcon] = useState(true);
  const [isFullscreen, setIsFullscreen] = useState(false);
  const { isAuthenticated } = useAuth();

  // Only show the chat icon if the user is authenticated
  useEffect(() => {
    setShowIcon(isAuthenticated);
  }, [isAuthenticated]);

  const toggleChat = () => {
    setIsOpen(!isOpen);
    if (!isOpen) {
      setIsFullscreen(false); // Reset fullscreen when opening chat
    }
  };

  const toggleFullscreen = () => {
    setIsFullscreen(!isFullscreen);
  };

  if (!showIcon) {
    return null;
  }

  return (
    <>
      {isOpen && !isFullscreen && (
        <>
          {/* Backdrop for mobile to indicate focus on chat */}
          <div 
            className="fixed inset-0 bg-black bg-opacity-30 z-40 sm:hidden"
            onClick={() => setIsOpen(false)}
          ></div>
          
          <div className="fixed bottom-20 left-1/2 transform -translate-x-1/2 z-50 w-[95vw] max-w-[95vw] sm:left-auto sm:right-4 sm:w-72 sm:h-[60vh] sm:max-h-[500px] h-[50vh] max-h-[400px] bg-white dark:bg-gray-800 rounded-lg shadow-lg border border-gray-200 dark:border-gray-700 overflow-hidden transform transition-all duration-300 ease-in-out">
            <div className="h-full flex flex-col">
              <div className="flex-1 overflow-hidden">
                <ChatInterface
                  onTaskUpdate={() => {
                    // Dispatch a custom event to notify other components to refresh tasks
                    window.dispatchEvent(new CustomEvent('refreshTasks'));
                  }}
                  isFullscreen={isFullscreen}
                  onToggleFullscreen={toggleFullscreen}
                  onClose={() => setIsOpen(false)} // Pass the close handler to ChatInterface
                />
              </div>
            </div>
          </div>
        </>
      )}
      
      {isFullscreen ? (
        <div className="fixed inset-0 z-50 bg-white dark:bg-gray-900 flex flex-col">
          <div className="flex-1 overflow-hidden">
            <ChatInterface
              onTaskUpdate={() => {
                // Dispatch a custom event to notify other components to refresh tasks
                window.dispatchEvent(new CustomEvent('refreshTasks'));
              }}
              isFullscreen={isFullscreen}
              onToggleFullscreen={toggleFullscreen}
              onClose={() => setIsOpen(false)} // Pass the close handler to ChatInterface
            />
          </div>
        </div>
      ) : null}

      {!isOpen && (
        <button
          onClick={toggleChat}
          className="fixed bottom-4 right-4 z-50 bg-gradient-to-r from-indigo-500 to-purple-600 text-white rounded-full p-3 shadow-md hover:shadow-lg transform transition-all duration-300 ease-in-out hover:scale-105 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 border border-white dark:border-gray-800"
          aria-label="Open chat"
        >
          <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
          </svg>
          <span className="absolute top-0 right-0 -mt-0.5 -mr-0.5 bg-red-500 rounded-full h-2.5 w-2.5 flex items-center justify-center"></span>
        </button>
      )}
    </>
  );
};

export default FloatingChatIcon;