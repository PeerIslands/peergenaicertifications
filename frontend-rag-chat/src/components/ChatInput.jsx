import React, { useState } from 'react';
import PropTypes from 'prop-types';
import { sendMessage } from '../services/api';

const ChatInput = ({ onNewMessage, sessionId, setSessionId, setIsLoading }) => {
  const [inputText, setInputText] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!inputText.trim()) return;

    const userMessage = {
      sender: 'user',
      text: inputText,
      timestamp: new Date().toISOString()
    };

    onNewMessage(userMessage);
    setInputText('');
    setIsLoading(true);

    try {
      const response = await sendMessage(inputText, sessionId);
      
      const aiMessage = {
        sender: 'ai',
        text: response.response,
        sources: response.sources,
        timestamp: new Date().toISOString()
      };

      onNewMessage(aiMessage);
      
      if (!sessionId) {
        setSessionId(response.session_id);
      }
    } catch (error) {
      console.error('Chat error:', error);
      const errorMessage = {
        sender: 'ai',
        text: `Error: ${error.response?.data?.detail || error.message}`,
        timestamp: new Date().toISOString()
      };
      onNewMessage(errorMessage);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  return (
    <div className="chat-input-container">
      <form onSubmit={handleSubmit} className="chat-form">
        <input
          type="text"
          value={inputText}
          onChange={(e) => setInputText(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Ask a question about the loaded documents..."
          className="chat-input"
          disabled={setIsLoading}
        />
        <button
          type="submit"
          disabled={!inputText.trim() || setIsLoading}
          className="send-button"
        >
          Send
        </button>
      </form>
    </div>
  );
};

ChatInput.propTypes = {
  onNewMessage: PropTypes.func.isRequired,
  sessionId: PropTypes.string,
  setSessionId: PropTypes.func.isRequired,
  setIsLoading: PropTypes.func.isRequired
};

export default ChatInput;
