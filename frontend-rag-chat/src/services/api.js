import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
});

// Send chat message
export const sendMessage = async (query, sessionId = null) => {
  const response = await api.post('/chat', {
    query,
    session_id: sessionId,
  });
  return response.data;
};

// Get document status
export const getStatus = async () => {
  const response = await api.get('/status');
  return response.data;
};

// Health check
export const healthCheck = async () => {
  const response = await api.get('/health');
  return response.data;
};

export default api;
