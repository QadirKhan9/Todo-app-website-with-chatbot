import React, { useState, useEffect, useRef } from 'react';
import { useChat } from '@openai/chatkit';

const ChatKitIntegration = ({ userId }) => {
  const [input, setInput] = useState('');
  const messagesEndRef = useRef(null);
  const { messages, sendMessage, isSending, connectToChat, disconnectFromChat } = useChat();

  // Initialize chat connection
  useEffect(() => {
    if (userId) {
      connectToChat({ userId });
    }

    return () => {
      disconnectFromChat();
    };
  }, [userId]);

  // Scroll to bottom when new messages arrive
  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (input.trim() === '') return;

    try {
      await sendMessage({ text: input });
      setInput('');
    } catch (error) {
      console.error('Error sending message:', error);
      // Handle error appropriately
    }
  };

  return (
    <div className="chat-container">
      <div className="messages">
        {messages.map((message) => (
          <div key={message.id} className={`message ${message.senderId === userId ? 'sent' : 'received'}`}>
            <div className="message-content">{message.text}</div>
            <div className="message-sender">{message.senderId}</div>
          </div>
        ))}
        <div ref={messagesEndRef} />
      </div>
      
      <form onSubmit={handleSubmit} className="input-form">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Type your message..."
          disabled={isSending}
        />
        <button type="submit" disabled={isSending}>
          {isSending ? 'Sending...' : 'Send'}
        </button>
      </form>
    </div>
  );
};

export default ChatKitIntegration;