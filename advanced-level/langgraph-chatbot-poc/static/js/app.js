// LangGraph Chatbot POC - Enhanced Frontend JavaScript

const API_BASE = '';
const sessionId = 'session_' + Date.now();
let messageCount = 0;

// DOM Elements
const chatContainer = document.getElementById('chatContainer');
const messageInput = document.getElementById('messageInput');
const sendBtn = document.getElementById('sendBtn');
const clearBtn = document.getElementById('clearBtn');
const statusIndicator = document.getElementById('statusIndicator');
const sourceInfo = document.getElementById('sourceInfo');
const messageCountEl = document.getElementById('messageCount');
const exportBtn = document.getElementById('exportBtn');
const themeToggle = document.getElementById('themeToggle');
const examplesBtn = document.getElementById('examplesBtn');
const examplesModal = document.getElementById('examplesModal');
const closeModal = document.querySelector('.close');

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    checkHealth();
    loadTheme();
    updateMessageCount();
    
    // Event listeners
    sendBtn.addEventListener('click', handleSend);
    clearBtn.addEventListener('click', handleClear);
    exportBtn.addEventListener('click', handleExport);
    themeToggle.addEventListener('click', toggleTheme);
    examplesBtn.addEventListener('click', () => examplesModal.style.display = 'block');
    closeModal.addEventListener('click', () => examplesModal.style.display = 'none');
    
    // Close modal when clicking outside
    window.addEventListener('click', (e) => {
        if (e.target === examplesModal) {
            examplesModal.style.display = 'none';
        }
    });
    
    // Example item clicks
    document.querySelectorAll('.example-item').forEach(item => {
        item.addEventListener('click', () => {
            const example = item.getAttribute('data-example');
            messageInput.value = example;
            messageInput.focus();
            examplesModal.style.display = 'none';
        });
    });
    
    // Allow Enter to send (Shift+Enter for new line)
    messageInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSend();
        }
    });
    
    // Auto-resize textarea
    messageInput.addEventListener('input', () => {
        messageInput.style.height = 'auto';
        messageInput.style.height = messageInput.scrollHeight + 'px';
    });
});

// Theme management
function loadTheme() {
    const theme = localStorage.getItem('theme') || 'light';
    document.documentElement.setAttribute('data-theme', theme);
    updateThemeIcon(theme);
}

function toggleTheme() {
    const currentTheme = document.documentElement.getAttribute('data-theme');
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
    document.documentElement.setAttribute('data-theme', newTheme);
    localStorage.setItem('theme', newTheme);
    updateThemeIcon(newTheme);
}

function updateThemeIcon(theme) {
    themeToggle.textContent = theme === 'dark' ? '☀️' : '🌙';
}

// Check health status
async function checkHealth() {
    try {
        const response = await fetch(`${API_BASE}/api/health`);
        const health = await response.json();
        
        if (health.status === 'healthy') {
            statusIndicator.textContent = '● Ready';
            statusIndicator.style.color = '#4caf50';
        } else {
            statusIndicator.textContent = '● Error';
            statusIndicator.style.color = '#f44336';
        }
    } catch (error) {
        console.error('Health check failed:', error);
        statusIndicator.textContent = '● Error';
        statusIndicator.style.color = '#f44336';
    }
}

// Update message count
function updateMessageCount() {
    messageCountEl.textContent = `${messageCount} message${messageCount !== 1 ? 's' : ''}`;
}

// Handle send message
async function handleSend() {
    const message = messageInput.value.trim();
    
    if (!message) {
        return;
    }
    
    // Disable input and show loading
    messageInput.disabled = true;
    sendBtn.disabled = true;
    sendBtn.querySelector('.btn-text').style.display = 'none';
    sendBtn.querySelector('.btn-loader').style.display = 'inline-flex';
    sendBtn.querySelector('.btn-loader').style.alignItems = 'center';
    sendBtn.querySelector('.btn-loader').style.gap = '8px';
    
    // Remove welcome message if present
    const welcomeMsg = chatContainer.querySelector('.welcome-message');
    if (welcomeMsg) {
        welcomeMsg.remove();
    }
    
    // Add user message to chat
    addMessage(message, 'user');
    messageCount++;
    updateMessageCount();
    
    // Clear input
    messageInput.value = '';
    messageInput.style.height = 'auto';
    
    // Show loading message
    const loadingId = addMessage('Thinking...', 'assistant', 'loading');
    
    try {
        // Send to API
        const response = await fetch(`${API_BASE}/api/chat`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                message: message,
                session_id: sessionId
            })
        });
        
        const result = await response.json();
        
        // Remove loading message
        const loadingMsg = document.getElementById(loadingId);
        if (loadingMsg) {
            loadingMsg.remove();
        }
        
        if (result.success) {
            // Add assistant response
            addMessage(
                result.response,
                'assistant',
                result.source,
                result.tool_used
            );
            
            // Update source info
            updateSourceInfo(result.source, result.tool_used);
        } else {
            // Show error
            addMessage(
                result.error || 'An error occurred',
                'assistant',
                'error'
            );
        }
    } catch (error) {
        console.error('Error:', error);
        
        // Remove loading message
        const loadingMsg = document.getElementById(loadingId);
        if (loadingMsg) {
            loadingMsg.remove();
        }
        
        addMessage(
            'Sorry, I encountered an error. Please try again.',
            'assistant',
            'error'
        );
    } finally {
        // Re-enable input
        messageInput.disabled = false;
        sendBtn.disabled = false;
        sendBtn.querySelector('.btn-text').style.display = 'inline';
        sendBtn.querySelector('.btn-loader').style.display = 'none';
        messageInput.focus();
    }
}

// Add message to chat
function addMessage(content, role, source = null, toolUsed = null) {
    const messageId = 'msg_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
    const messageDiv = document.createElement('div');
    messageDiv.id = messageId;
    messageDiv.className = `message ${role}`;
    
    const bubble = document.createElement('div');
    bubble.className = 'message-bubble';
    
    // Format content (support markdown-like formatting)
    const formattedContent = formatMessage(content);
    bubble.innerHTML = formattedContent;
    
    messageDiv.appendChild(bubble);
    
    // Add source badge
    if (source && source !== 'loading') {
        const sourceBadge = document.createElement('div');
        sourceBadge.className = `message-source ${source}`;
        
        const toolIcons = {
            'calculator': '🔢',
            'weather': '🌤️',
            'time_date': '🕐',
            'unit_converter': '📏',
            'wikipedia': '📚',
            'translation': '🌐'
        };
        
        if (source === 'tool' && toolUsed) {
            const icon = toolIcons[toolUsed] || '🔧';
            sourceBadge.textContent = `${icon} Tool: ${toolUsed}`;
        } else if (source === 'tool') {
            sourceBadge.textContent = '🔧 Tool';
        } else if (source === 'llm') {
            sourceBadge.textContent = '🤖 LLM';
        } else if (source === 'error') {
            sourceBadge.textContent = '❌ Error';
        }
        
        messageDiv.appendChild(sourceBadge);
    }
    
    chatContainer.appendChild(messageDiv);
    
    // Scroll to bottom
    chatContainer.scrollTop = chatContainer.scrollHeight;
    
    return messageId;
}

// Format message content (basic markdown support)
function formatMessage(content) {
    // Escape HTML first
    let formatted = content
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;');
    
    // Convert **text** to <strong>text</strong>
    formatted = formatted.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    
    // Convert line breaks
    formatted = formatted.replace(/\n/g, '<br>');
    
    // Convert URLs to links
    formatted = formatted.replace(/(https?:\/\/[^\s]+)/g, '<a href="$1" target="_blank" rel="noopener">$1</a>');
    
    return formatted;
}

// Update source info panel
function updateSourceInfo(source, toolUsed) {
    let html = '';
    
    const toolNames = {
        'calculator': 'Calculator',
        'weather': 'Weather',
        'time_date': 'Time & Date',
        'unit_converter': 'Unit Converter',
        'wikipedia': 'Wikipedia',
        'translation': 'Translation'
    };
    
    if (source === 'tool') {
        const toolName = toolNames[toolUsed] || toolUsed || 'Unknown Tool';
        html = `
            <div class="source-badge tool">🔧 Tool Response</div>
            ${toolUsed ? `<p><strong>Tool Used:</strong> ${toolName}</p>` : ''}
            <p>This response was generated by a tool.</p>
        `;
    } else if (source === 'llm') {
        html = `
            <div class="source-badge llm">🤖 LLM Response</div>
            <p>This response was generated by the AI language model (Azure OpenAI GPT-4o).</p>
        `;
    } else {
        html = '<p class="placeholder">Source information will appear here</p>';
    }
    
    sourceInfo.innerHTML = html;
}

// Export conversation
function handleExport() {
    const messages = chatContainer.querySelectorAll('.message');
    if (messages.length === 0) {
        alert('No conversation to export');
        return;
    }
    
    let exportText = 'LangGraph Chatbot Conversation Export\n';
    exportText += '='.repeat(50) + '\n\n';
    exportText += `Exported: ${new Date().toLocaleString()}\n`;
    exportText += `Total Messages: ${messageCount}\n\n`;
    exportText += '-'.repeat(50) + '\n\n';
    
    messages.forEach(msg => {
        const role = msg.classList.contains('user') ? 'User' : 'Assistant';
        const bubble = msg.querySelector('.message-bubble');
        const source = msg.querySelector('.message-source');
        
        exportText += `[${role}]`;
        if (source) {
            exportText += ` ${source.textContent}`;
        }
        exportText += '\n';
        exportText += bubble.textContent + '\n\n';
    });
    
    // Create download
    const blob = new Blob([exportText], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `chatbot-conversation-${Date.now()}.txt`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
}

// Clear conversation
async function handleClear() {
    if (!confirm('Are you sure you want to clear the conversation?')) {
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/api/clear`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                session_id: sessionId
            })
        });
        
        // Clear chat container
        chatContainer.innerHTML = `
            <div class="welcome-message">
                <h2>Welcome! 👋</h2>
                <p>I'm an intelligent chatbot powered by LangGraph. I can help you with:</p>
                <div class="tools-grid">
                    <div class="tool-card">
                        <div class="tool-icon">🔢</div>
                        <div class="tool-name">Calculator</div>
                        <div class="tool-desc">Math calculations</div>
                    </div>
                    <div class="tool-card">
                        <div class="tool-icon">🌤️</div>
                        <div class="tool-name">Weather</div>
                        <div class="tool-desc">Weather forecasts</div>
                    </div>
                    <div class="tool-card">
                        <div class="tool-icon">🕐</div>
                        <div class="tool-name">Time & Date</div>
                        <div class="tool-desc">Current time/date</div>
                    </div>
                    <div class="tool-card">
                        <div class="tool-icon">📏</div>
                        <div class="tool-name">Unit Converter</div>
                        <div class="tool-desc">Unit conversions</div>
                    </div>
                    <div class="tool-card">
                        <div class="tool-icon">📚</div>
                        <div class="tool-name">Wikipedia</div>
                        <div class="tool-desc">Search Wikipedia</div>
                    </div>
                    <div class="tool-card">
                        <div class="tool-icon">🌐</div>
                        <div class="tool-name">Translation</div>
                        <div class="tool-desc">Language translation</div>
                    </div>
                </div>
                <p class="welcome-note">💡 I'll automatically route your query to the right tool or LLM!</p>
            </div>
        `;
        
        // Clear source info
        sourceInfo.innerHTML = '<p class="placeholder">Source information will appear here</p>';
        
        // Reset message count
        messageCount = 0;
        updateMessageCount();
        
        messageInput.focus();
    } catch (error) {
        console.error('Error clearing conversation:', error);
    }
}
