import React, { useEffect, useRef } from 'react';
import PropTypes from 'prop-types';

const ChatWindow = ({ messages, isLoading }) => {
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading]);

  return (
    <div className="chat-window">
      {messages.length === 0 && !isLoading && (
        <div className="loading-message">
          <p>Start a conversation by asking a question about the loaded documents.</p>
          <p className="loading-text-small">Documents are automatically loaded from the files directory.</p>
        </div>
      )}
      
      <div className="chat-messages">
        {messages.map((message, index) => (
          <div
            key={`${message.sender}-${index}-${message.text.slice(0, 20)}`}
            className={`message ${message.sender === 'user' ? 'user' : 'assistant'}`}
          >
            <div className="message-content">
              <div>{message.text}</div>
              {message.sources && message.sources.length > 0 && (
                <div className="message-sources">
                  <div>Sources:</div>
                  <div>
                    {message.sources.map((source, idx) => (
                      <span key={`source-${idx}-${source.slice(0, 10)}`}>
                        {source}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        ))}
        
        {isLoading && (
          <div className="message assistant">
            <div className="message-content">
              <div className="loading-animation">
                <div className="loading-dots">
                  <div className="loading-dot"></div>
                  <div className="loading-dot"></div>
                  <div className="loading-dot"></div>
                </div>
                <span>AI is thinking...</span>
              </div>
            </div>
          </div>
        )}
      </div>
      
      <div ref={messagesEndRef} />
    </div>
  );
};

ChatWindow.propTypes = {
  messages: PropTypes.arrayOf(PropTypes.shape({
    sender: PropTypes.string.isRequired,
    text: PropTypes.string.isRequired,
    sources: PropTypes.arrayOf(PropTypes.string)
  })).isRequired,
  isLoading: PropTypes.bool.isRequired
};

export default ChatWindow;
