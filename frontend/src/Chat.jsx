import React, { useState, useRef, useEffect } from 'react';
import './Chat.css';

const Chat = () => {
  const [messages, setMessages] = useState([
    { 
      role: 'assistant', 
      content: 'Hello there! 💙 I\'m Amal, your companion here at An-Nisa Hope Center. I\'m here to support you with warmth and care - whether you\'re seeking information about our programs, looking for volunteer opportunities, or need guidance on how we can help. Please know that you\'re not alone, and I\'m here to listen. What can I help you with today?'
    }
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const messagesEndRef = useRef(null);

  const API_BASE_URL = 'http://localhost:5001';

  // Scroll to bottom when messages change
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const sendMessage = async (message) => {
    try {
      const response = await fetch(`${API_BASE_URL}/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ message }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Error sending message:', error);
      throw error;
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!input.trim()) return;

    const userMessage = input.trim();
    setInput('');
    setError('');

    // Add user message
    setMessages(prev => [...prev, { role: 'user', content: userMessage }]);
    setIsLoading(true);

    try {
      const response = await sendMessage(userMessage);
      
      // Add assistant response
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: response.response
      }]);
    } catch (error) {
      setError('Failed to send message. Please check if the backend is running.');
      // Add error message
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: 'Sorry, I\'m having trouble connecting to the server. Please make sure the backend is running and try again.'
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  const formatMessage = (content) => {
    // Simple formatting for URLs
    const urlRegex = /(https?:\/\/[^\s]+)/g;
    return content.replace(urlRegex, '<a href="$1" target="_blank" rel="noopener noreferrer">$1</a>');
  };

  return (
    <div className="chat-container">
      <div className="chat-header">
        <h1>Meet Amal</h1>
        <p>Your companion at AnNisa.org • Here to support you with compassion and hope</p>
      </div>

      {error && (
        <div className="error-banner">
          <p>⚠️ {error}</p>
        </div>
      )}

      <div className="chat-messages">
        {messages.map((message, index) => (
          <div key={index} className={`message ${message.role}`}>
            <div className="message-content">
              <div 
                dangerouslySetInnerHTML={{ 
                  __html: formatMessage(message.content) 
                }} 
              />
            </div>
          </div>
        ))}

        {isLoading && (
          <div className="message assistant">
            <div className="message-content">
              <div className="typing-indicator">
                <div className="typing-dot"></div>
                <div className="typing-dot"></div>
                <div className="typing-dot"></div>
              </div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      <form className="chat-input-form" onSubmit={handleSubmit}>
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask about AnNisa.org programs, volunteer opportunities, donations..."
          disabled={isLoading}
          className="chat-input"
        />
        <button type="submit" disabled={isLoading || !input.trim()} className="send-button">
          {isLoading ? '...' : 'Send'}
        </button>
      </form>

      <div className="chat-footer">
        <p>
          Powered by AI • Information sourced from{' '}
          <a href="https://annisa.org" target="_blank" rel="noopener noreferrer">
            annisa.org
          </a>
        </p>
      </div>
    </div>
  );
};

export default Chat; 