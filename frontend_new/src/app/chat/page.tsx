'use client';

import { useState } from 'react';
import { useAuth } from '@/components/AuthProvider';
import FullscreenChatInterface from '@/components/FullscreenChatInterface';
import PrivateRoute from '@/components/PrivateRoute';

const ChatPage = () => {
  const { user } = useAuth();
  const [isFullscreen, setIsFullscreen] = useState(true);

  const toggleFullscreen = () => {
    setIsFullscreen(!isFullscreen);
  };

  return (
    <PrivateRoute>
      <div className="fixed inset-0 z-50 bg-white dark:bg-gray-900 flex flex-col">
        <FullscreenChatInterface 
          onTaskUpdate={() => {
            // Dispatch a custom event to notify other components to refresh tasks
            window.dispatchEvent(new CustomEvent('refreshTasks'));
          }} 
          onToggleFullscreen={toggleFullscreen}
        />
      </div>
    </PrivateRoute>
  );
};

export default ChatPage;