import React, { useState, useEffect } from 'react';
import ChatWindow from './components/ChatWindow';
import ChatInput from './components/ChatInput';
import { getStatus } from './services/api';
import './App.css';

function App() {
  const [messages, setMessages] = useState([]);
  const [sessionId, setSessionId] = useState(null);
  const [isReady, setIsReady] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    checkStatus();
  }, []);

  const checkStatus = async () => {
    try {
      const status = await getStatus();
      setIsReady(status.total_chunks > 0);
    } catch (error) {
      console.error('Error checking status:', error);
    }
  };


  const handleNewMessage = (message) => {
    setMessages(prev => [...prev, message]);
  };

  const handleClearChat = () => {
    setMessages([]);
  };

  return (
    <div className="app">
      <div className="container">
        <header className="header">
          <h1>RAG Chat App</h1>
          <p>Chat with pre-loaded PDF documents using AI</p>
        </header>

        <div className="main-content">
          {isReady ? (
            <div className="chat-container">
              <div className="chat-header">
                <div className="chat-header-content">
                  <h2 className="chat-title">Chat to ask questions about the loaded documents</h2>
                  <button
                    onClick={handleClearChat}
                    className="clear-button"
                  >
                    Clear Chat
                  </button>
                </div>
              </div>
              <ChatWindow messages={messages} isLoading={isLoading} />
              <ChatInput 
                onNewMessage={handleNewMessage}
                sessionId={sessionId}
                setSessionId={setSessionId}
                setIsLoading={setIsLoading}
              />
            </div>
          ) : (
            <div className="loading-container">
              <h2 className="loading-title">Loading Documents</h2>
              <p className="loading-text">
                Documents are being processed from the files directory. This may take a moment...
              </p>
              <div className="spinner"></div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default App;
