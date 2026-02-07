'use client';

import React, { useState, useEffect, useRef } from 'react';
import { useAuth } from './AuthProvider';
import { api } from '@/services/apiClient';
import LoadingSpinner from './LoadingSpinner';
import QuickActionButtons from './QuickActionButtons';

// Auto-resizing textarea hook
const useAutoResizeTextarea = () => {
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const adjustHeight = () => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 200)}px`;
    }
  };

  useEffect(() => {
    adjustHeight();
  }, []);

  return { textareaRef, adjustHeight };
};

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
}

interface ChatInterfaceProps {
  onTaskUpdate?: () => void; // Callback to trigger task list refresh
  isFullscreen?: boolean;
  onToggleFullscreen?: () => void;
  onClose?: () => void; // Callback to handle closing the chat
}

const ChatInterface: React.FC<ChatInterfaceProps> = ({ onTaskUpdate, isFullscreen = false, onToggleFullscreen, onClose }) => {
  const { user } = useAuth();
  const [inputMessage, setInputMessage] = useState<string>('');
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Use the auto-resize hook
  const { textareaRef, adjustHeight } = useAutoResizeTextarea();

  // Load initial messages when component mounts
  useEffect(() => {
    if (user) {
      loadInitialMessages();
    }
  }, [user]);

  // Scroll to bottom when new messages are added
  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const loadInitialMessages = async () => {
    try {
      // For now, we'll just initialize with a welcome message
      // In a real implementation, you might load recent conversation history
      setMessages([
        {
          id: 'welcome',
          role: 'assistant',
          content: 'Hello! I\'m your AI assistant. You can ask me to help you manage your tasks. Try using the quick action buttons below or type your request.',
          timestamp: new Date().toISOString()
        }
      ]);
    } catch (err) {
      console.error('Error loading initial messages:', err);
      setError('Failed to load chat history');
    }
  };

  const handleSendMessage = async () => {
    if (!inputMessage.trim() || !user) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: inputMessage,
      timestamp: new Date().toISOString()
    };

    // Add user message to the chat immediately
    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setIsLoading(true);
    setError(null);

    try {
      // Send message to backend API
      const response = await api.chatWithAI(inputMessage, user?.id);

      // Safely extract the response content
      let content = "I received your message.";
      if (response && typeof response === 'object') {
        if (response.response && typeof response.response === 'string') {
          content = response.response;
        } else if (response.response && typeof response.response === 'object' && response.response.content) {
          content = response.response.content;
        } else if (response.content) {
          content = response.content;
        } else if (response.detail) {
          content = response.detail;
        } else {
          // If we can't find content in expected fields, convert the response to string
          content = JSON.stringify(response);
        }
      } else {
        content = String(response);
      }

      const aiMessage: Message = {
        id: response.message_id || `ai-${Date.now()}`,
        role: 'assistant',
        content: content,
        timestamp: response.timestamp || new Date().toISOString()
      };

      setMessages(prev => [...prev, aiMessage]);

      // Trigger task list refresh if AI performed an action
      if (response && typeof response === 'object' && response.action_taken &&
        response.action_taken.details !== 'No todo operations performed') {
        onTaskUpdate?.();
      }
    } catch (err: any) {
      console.error('Error sending message:', err);
      setError(err.message || 'Failed to send message');

      // Add error message to chat
      const errorMessage: Message = {
        id: `error-${Date.now()}`,
        role: 'assistant',
        content: `Sorry, I encountered an error: ${err.message || 'Unable to process your request'}`,
        timestamp: new Date().toISOString()
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const handleQuickAction = (action: string) => {
    let message = '';
    
    switch (action) {
      case 'create-task':
        message = 'Create new task a name ';
        break;
      case 'view-tasks':
        message = 'Show me my tasks';
        break;
      case 'complete-task':
        message = 'mark task name as completed';
        break;
      case 'update-task':
        message = 'Update task name to new name';
        break;
      case 'delete-task':
        message = 'Delete name task';
        break;
      default:
        message = '';
    }
    
    if (message) {
      setInputMessage(message);
      // Focus the textarea and move cursor to end
      setTimeout(() => {
        if (textareaRef.current) {
          textareaRef.current.focus();
          const length = textareaRef.current.value.length;
          textareaRef.current.setSelectionRange(length, length);
        }
      }, 0);
    }
  };

  return (
    <div className={`flex flex-col h-full ${isFullscreen ? 'bg-white dark:bg-gray-900' : 'bg-white dark:bg-gray-900 rounded-lg'} ${isFullscreen ? '' : 'border border-gray-200 dark:border-gray-700'} overflow-hidden w-full max-w-full`}>
      <div className="p-2 border-b border-gray-100 dark:border-gray-800 bg-gradient-to-r from-indigo-500 to-purple-600 flex justify-between items-center">
        <div className="flex items-center space-x-1.5">
          <div className="bg-white/20 p-1 rounded-md">
            <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
            </svg>
          </div>
          <h2 className="text-sm font-medium text-white">AI Assistant</h2>
        </div>

        <div className="flex items-center space-x-1">
          {onToggleFullscreen && (
            <button
              onClick={onToggleFullscreen}
              className="text-white hover:text-gray-200 focus:outline-none p-1"
              aria-label={isFullscreen ? "Exit fullscreen" : "Enter fullscreen"}
            >
              {isFullscreen ? (
                <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" viewBox="0 0 20 20" fill="currentColor">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                </svg>
              ) : (
                <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" viewBox="0 0 20 20" fill="currentColor">
                  <path fillRule="evenodd" d="M3 4a1 1 0 011-1h4a1 1 0 010 2H6.414l2.293 2.293a1 1 0 11-1.414 1.414L5 6.414V8a1 1 0 01-2 0V4zm9 1a1 1 0 110-2h4a1 1 0 011 1v4a1 1 0 11-2 0V6.414l-2.293 2.293a1 1 0 11-1.414-1.414L13 6.414V8a1 1 0 11-2 0V4zm-9 7a1 1 0 012 0v1.586l2.293-2.293a1 1 0 111.414 1.414L6.414 15H8a1 1 0 110 2H4a1 1 0 01-1-1v-4zm13-1a1 1 0 011 1v4a1 1 0 01-1 1h-4a1 1 0 110-2h1.586l-2.293-2.293a1 1 0 111.414-1.414L15 13.586V12a1 1 0 011-1z" clipRule="evenodd" />
                </svg>
              )}
            </button>
          )}

          <button
            onClick={() => {
              // Close the chat regardless of fullscreen mode
              onClose?.(); // Call the onClose callback if provided
            }}
            className="text-white hover:text-gray-200 focus:outline-none p-1"
            aria-label="Close chat"
          >
            <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" viewBox="0 0 20 20" fill="currentColor">
              <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
            </svg>
          </button>
        </div>
      </div>

      <div className={`flex-1 overflow-y-auto p-2 space-y-2 ${isFullscreen ? 'max-h-[calc(100vh-100px)]' : 'max-h-[calc(100vh-200px)] sm:max-h-[300px]'} bg-white dark:bg-gray-900`}>
        {error && (
          <div className="bg-red-100 dark:bg-red-900/30 border-l-4 border-red-500 text-red-700 dark:text-red-300 p-2 rounded-r-md animate-pulse">
            <div className="flex items-start">
              <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4 mr-1.5 mt-0.5 flex-shrink-0" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
              </svg>
              <span className="text-xs">{error}</span>
            </div>
          </div>
        )}

        {messages.map((message) => (
          <div
            key={message.id}
            className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div
              className={`max-w-[85%] rounded-xl p-2 ${message.role === 'user'
                  ? 'bg-indigo-600 text-white rounded-br-none shadow-sm'
                  : 'bg-gray-100 dark:bg-gray-800 text-gray-800 dark:text-gray-200 rounded-bl-none border border-gray-200 dark:border-gray-700'
                }`}
            >
              <div className="flex items-start space-x-1.5">
                {message.role === 'assistant' && (
                  <div className="flex-shrink-0 mt-0.5">
                    <div className="bg-indigo-500 w-5 h-5 rounded-full flex items-center justify-center">
                      <svg xmlns="http://www.w3.org/2000/svg" className="h-2.5 w-2.5 text-white" viewBox="0 0 20 20" fill="currentColor">
                        <path fillRule="evenodd" d="M18 5v8a2 2 0 01-2 2h-5l-5 4v-4H4a2 2 0 01-2-2V5a2 2 0 012-2h12a2 2 0 012 2zM7 8H5v2h2V8zm2 0h2v2H9V8zm6 0h-2v2h2V8z" clipRule="evenodd" />
                      </svg>
                    </div>
                  </div>
                )}
                <div className="flex-1">
                  <div className="whitespace-pre-wrap break-words text-sm">{message.content}</div>
                  <div className={`text-[10px] mt-1 ${message.role === 'user' ? 'text-indigo-200' : 'text-gray-500 dark:text-gray-400'}`}>
                    {new Date(message.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                  </div>
                </div>
                {message.role === 'user' && (
                  <div className="flex-shrink-0 mt-0.5">
                    <div className="bg-white/30 w-5 h-5 rounded-full flex items-center justify-center">
                      <svg xmlns="http://www.w3.org/2000/svg" className="h-2.5 w-2.5 text-white" viewBox="0 0 20 20" fill="currentColor">
                        <path fillRule="evenodd" d="M10 9a3 3 0 100-6 3 3 0 000 6zm-7 9a7 7 0 1114 0H3z" clipRule="evenodd" />
                      </svg>
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
        ))}
        {isLoading && (
          <div className="flex justify-start">
            <div className="max-w-[85%] rounded-xl rounded-bl-none bg-gray-100 dark:bg-gray-700/80 text-gray-800 dark:text-gray-200 p-2 shadow-sm">
              <div className="flex items-center">
                <div className="bg-indigo-500 w-5 h-5 rounded-full flex items-center justify-center mr-2">
                  <svg xmlns="http://www.w3.org/2000/svg" className="h-2.5 w-2.5 text-white" viewBox="0 0 20 20" fill="currentColor">
                    <path fillRule="evenodd" d="M18 5v8a2 2 0 01-2 2h-5l-5 4v-4H4a2 2 0 01-2-2V5a2 2 0 012-2h12a2 2 0 012 2zM7 8H5v2h2V8zm2 0h2v2H9V8zm6 0h-2v2h2V8z" clipRule="evenodd" />
                  </svg>
                </div>
                <div className="flex items-center">
                  <LoadingSpinner size="small" />
                  <span className="ml-1 text-sm">Thinking...</span>
                </div>
              </div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      <div className="p-2 border-t border-gray-100 dark:border-gray-800 bg-white dark:bg-gray-900">
        <div className="flex flex-col gap-2">
          {/* Quick Action Buttons */}
          <QuickActionButtons
            onActionClick={handleQuickAction}
            disabled={isLoading}
          />

          {/* Simplified input container */}
          <div className="relative">
            <textarea
              ref={textareaRef}
              value={inputMessage}
              onChange={(e) => {
                setInputMessage(e.target.value);
                // Adjust height after state update
                setTimeout(adjustHeight, 0);
              }}
              onKeyDown={handleKeyPress}
              placeholder="Type a message..."
              className="w-full bg-gray-50 dark:bg-gray-800 text-gray-900 dark:text-gray-100 border border-gray-200 dark:border-gray-700 rounded-lg py-2 px-3 pr-10 resize-none min-h-[40px] max-h-[150px] focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 transition-all duration-200 placeholder-gray-400 dark:placeholder-gray-500 text-sm"
              rows={1}
              disabled={isLoading}
            />

            <div className="absolute right-1.5 bottom-1.5 flex gap-1">
              {inputMessage && (
                <button
                  type="button"
                  onClick={() => setInputMessage('')}
                  className="p-0.5 rounded-full bg-gray-700 hover:bg-gray-600 text-gray-400 transition-colors duration-200"
                  aria-label="Clear input"
                >
                  <svg xmlns="http://www.w3.org/2000/svg" className="h-3.5 w-3.5" viewBox="0 0 20 20" fill="currentColor">
                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                  </svg>
                </button>
              )}

              <button
                onClick={handleSendMessage}
                disabled={isLoading || !inputMessage.trim()}
                className="p-2 rounded-md bg-indigo-600 hover:bg-indigo-700 text-white disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 flex items-center justify-center shadow-sm"
              >
                <svg xmlns="http://www.w3.org/2000/svg" className="h-3.5 w-3.5" viewBox="0 0 20 20" fill="currentColor">
                  <path d="M10.894 2.553a1 1 0 00-1.788 0l-7 14a1 1 0 001.169 1.409l5-1.429A1 1 0 009 15.571V11a1 1 0 112 0v4.571a1 1 0 00.725.962l5 1.428a1 1 0 001.17-1.408l-7-14z" />
                </svg>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ChatInterface;