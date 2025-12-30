/**
 * RAG Explorer - Frontend Application with Azure OpenAI
 * Handles UI interactions and API communication
 */

// API Base URL
const API_BASE = '';

// DOM Elements
const elements = {
    apiKeyInput: document.getElementById('apiKeyInput'),
    configureBtn: document.getElementById('configureBtn'),
    configPanel: document.getElementById('configPanel'),
    configStatus: document.getElementById('configStatus'),
    queryInput: document.getElementById('queryInput'),
    queryBtn: document.getElementById('queryBtn'),
    ingestBtn: document.getElementById('ingestBtn'),
    loadBtn: document.getElementById('loadBtn'),
    clearBtn: document.getElementById('clearBtn'),
    responseContent: document.getElementById('responseContent'),
    sourcesSection: document.getElementById('sourcesSection'),
    sourcesList: document.getElementById('sourcesList'),
    statusIndicator: document.getElementById('statusIndicator'),
    loadingOverlay: document.getElementById('loadingOverlay'),
    loadingText: document.getElementById('loadingText'),
    // File upload elements
    dropzone: document.getElementById('dropzone'),
    fileInput: document.getElementById('fileInput'),
    fileList: document.getElementById('fileList'),
    fileItems: document.getElementById('fileItems'),
    fileCount: document.getElementById('fileCount'),
    clearFilesBtn: document.getElementById('clearFilesBtn'),
    clearStoreBtn: document.getElementById('clearStoreBtn')
};

// State
let isApiConfigured = false;
let isVectorStoreReady = false;
let uploadedFiles = [];

/**
 * Initialize the application
 */
async function init() {
    // Check system health
    await checkHealth();
    
    // Set up event listeners
    setupEventListeners();
    
    // Update UI state
    updateUIState();
}

/**
 * Set up event listeners
 */
function setupEventListeners() {
    // Configure button
    elements.configureBtn.addEventListener('click', handleConfigure);
    
    // Enter key in API key input
    elements.apiKeyInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') {
            handleConfigure();
        }
    });
    
    // Clear masked input on focus if it contains only dots
    elements.apiKeyInput.addEventListener('focus', () => {
        if (elements.apiKeyInput.value.match(/^•+$/)) {
            elements.apiKeyInput.value = '';
            elements.apiKeyInput.type = 'password';
            elements.apiKeyInput.placeholder = 'Enter new API key to reconfigure...';
        }
    });
    
    // Restore masked key if user clicks away without entering new key
    elements.apiKeyInput.addEventListener('blur', () => {
        if (isApiConfigured && elements.apiKeyInput.value === '') {
            elements.apiKeyInput.value = '•'.repeat(32);
            elements.apiKeyInput.type = 'text';
            elements.apiKeyInput.placeholder = 'Enter your Azure OpenAI API Key...';
        }
    });
    
    // Query button
    elements.queryBtn.addEventListener('click', handleQuery);
    
    // Enter key in textarea (Ctrl/Cmd + Enter to submit)
    elements.queryInput.addEventListener('keydown', (e) => {
        if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
            handleQuery();
        }
    });
    
    // Ingest button
    elements.ingestBtn.addEventListener('click', handleIngest);
    
    // Load button
    elements.loadBtn.addEventListener('click', handleLoad);
    
    // Clear store button
    elements.clearStoreBtn.addEventListener('click', handleClearStore);
    
    // Clear button
    elements.clearBtn.addEventListener('click', clearResponse);
    
    // Sample question chips
    document.querySelectorAll('.chip').forEach(chip => {
        chip.addEventListener('click', () => {
            elements.queryInput.value = chip.dataset.query;
            elements.queryInput.focus();
        });
    });
    
    // File upload event listeners
    setupFileUpload();
}

/**
 * Set up file upload drag-and-drop functionality
 */
function setupFileUpload() {
    const dropzone = elements.dropzone;
    const fileInput = elements.fileInput;
    
    // Click to browse
    dropzone.addEventListener('click', () => {
        fileInput.click();
    });
    
    // File input change
    fileInput.addEventListener('change', (e) => {
        handleFiles(e.target.files);
        fileInput.value = ''; // Reset input
    });
    
    // Drag events
    dropzone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropzone.classList.add('dragover');
    });
    
    dropzone.addEventListener('dragleave', (e) => {
        e.preventDefault();
        dropzone.classList.remove('dragover');
    });
    
    dropzone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropzone.classList.remove('dragover');
        
        const files = Array.from(e.dataTransfer.files).filter(f => f.type === 'application/pdf');
        if (files.length > 0) {
            handleFiles(files);
        } else {
            showMessage('Please drop only PDF files.', 'warning');
        }
    });
    
    // Clear all files
    elements.clearFilesBtn.addEventListener('click', () => {
        uploadedFiles = [];
        updateFileList();
    });
}

/**
 * Handle uploaded files
 */
function handleFiles(files) {
    const newFiles = Array.from(files).filter(f => f.type === 'application/pdf');
    
    // Avoid duplicates
    newFiles.forEach(file => {
        if (!uploadedFiles.some(f => f.name === file.name && f.size === file.size)) {
            uploadedFiles.push(file);
        }
    });
    
    updateFileList();
}

/**
 * Update the file list UI
 */
function updateFileList() {
    elements.fileCount.textContent = uploadedFiles.length;
    
    if (uploadedFiles.length > 0) {
        elements.fileList.classList.add('has-files');
        elements.fileItems.innerHTML = uploadedFiles.map((file, index) => `
            <div class="file-item" data-index="${index}">
                <div class="file-item-icon">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
                        <polyline points="14,2 14,8 20,8"/>
                    </svg>
                </div>
                <div class="file-item-info">
                    <div class="file-item-name">${file.name}</div>
                    <div class="file-item-size">${formatFileSize(file.size)}</div>
                </div>
                <button class="file-item-remove" onclick="removeFile(${index})" title="Remove file">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <line x1="18" y1="6" x2="6" y2="18"/>
                        <line x1="6" y1="6" x2="18" y2="18"/>
                    </svg>
                </button>
            </div>
        `).join('');
    } else {
        elements.fileList.classList.remove('has-files');
        elements.fileItems.innerHTML = '';
    }
    
    updateUIState();
}

/**
 * Remove a file from the list
 */
function removeFile(index) {
    uploadedFiles.splice(index, 1);
    updateFileList();
}

/**
 * Format file size for display
 */
function formatFileSize(bytes) {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
}

/**
 * Check API health status
 */
async function checkHealth() {
    try {
        const response = await fetch(`${API_BASE}/api/health`);
        const data = await response.json();
        
        isApiConfigured = data.api_configured;
        isVectorStoreReady = data.vector_store_loaded;
        
        updateStatus();
        updateUIState();
    } catch (error) {
        console.error('Health check failed:', error);
        updateStatus('error');
    }
}

/**
 * Update status indicator
 */
function updateStatus(override = null) {
    const dot = elements.statusIndicator.querySelector('.status-dot');
    const text = elements.statusIndicator.querySelector('.status-text');
    
    dot.className = 'status-dot';
    
    if (override === 'error') {
        dot.classList.add('error');
        text.textContent = 'Connection error. Check if server is running.';
        return;
    }
    
    if (!isApiConfigured) {
        text.textContent = 'Please configure your Azure OpenAI API key above.';
    } else if (isVectorStoreReady) {
        dot.classList.add('ready');
        text.textContent = 'Vector store loaded & ready';
    } else {
        text.textContent = 'API configured. Ingest or load documents to continue.';
    }
}

/**
 * Update UI state based on configuration
 */
function updateUIState() {
    // Update config panel
    if (isApiConfigured) {
        elements.configPanel.classList.add('configured');
        elements.configStatus.textContent = '✓ Azure OpenAI configured successfully';
        elements.configStatus.className = 'config-status success';
        
        // Show masked API key if input is empty (e.g., on page load)
        if (elements.apiKeyInput.value === '') {
            elements.apiKeyInput.value = '•'.repeat(32);
            elements.apiKeyInput.type = 'text';
        }
    } else {
        elements.configPanel.classList.remove('configured');
        elements.apiKeyInput.value = '';
        elements.apiKeyInput.type = 'password';
    }
    
    // Enable/disable buttons based on state
    // Ingest button requires API configured AND files uploaded
    elements.ingestBtn.disabled = !isApiConfigured || uploadedFiles.length === 0;
    elements.loadBtn.disabled = !isApiConfigured;
    elements.clearStoreBtn.disabled = !isVectorStoreReady;
    elements.queryBtn.disabled = !isApiConfigured || !isVectorStoreReady;
}

/**
 * Show loading overlay
 */
function showLoading(message = 'Processing...') {
    elements.loadingText.textContent = message;
    elements.loadingOverlay.classList.add('visible');
}

/**
 * Hide loading overlay
 */
function hideLoading() {
    elements.loadingOverlay.classList.remove('visible');
}

/**
 * Handle API key configuration
 */
async function handleConfigure() {
    const apiKey = elements.apiKeyInput.value.trim();
    
    // If already configured and showing masked key, don't re-configure with dots
    if (apiKey.match(/^•+$/)) {
        elements.configStatus.textContent = 'API key already configured. Enter a new key to reconfigure.';
        elements.configStatus.className = 'config-status';
        return;
    }
    
    if (!apiKey) {
        elements.configStatus.textContent = 'Please enter an API key.';
        elements.configStatus.className = 'config-status error';
        return;
    }
    
    showLoading('Configuring Azure OpenAI...');
    elements.configureBtn.disabled = true;
    
    // Store the key length for masking
    const keyLength = apiKey.length;
    
    try {
        const response = await fetch(`${API_BASE}/api/configure`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ api_key: apiKey })
        });
        
        const data = await response.json();
        
        if (data.success) {
            isApiConfigured = true;
            elements.configPanel.classList.add('configured');
            elements.configStatus.textContent = '✓ ' + data.message;
            elements.configStatus.className = 'config-status success';
            
            // Show masked API key (dots)
            elements.apiKeyInput.value = '•'.repeat(Math.min(keyLength, 32));
            elements.apiKeyInput.type = 'text'; // Show dots visually
            
            // Refresh health status
            await checkHealth();
        } else {
            elements.configStatus.textContent = '✗ ' + data.message;
            elements.configStatus.className = 'config-status error';
        }
    } catch (error) {
        console.error('Configuration error:', error);
        elements.configStatus.textContent = '✗ Failed to configure. Please try again.';
        elements.configStatus.className = 'config-status error';
    } finally {
        hideLoading();
        elements.configureBtn.disabled = false;
        updateUIState();
    }
}

/**
 * Handle query submission
 */
async function handleQuery() {
    const question = elements.queryInput.value.trim();
    
    if (!question) {
        showMessage('Please enter a question.', 'warning');
        return;
    }
    
    if (!isApiConfigured) {
        showMessage('Please configure your Azure OpenAI API key first.', 'warning');
        return;
    }
    
    if (!isVectorStoreReady) {
        showMessage('Please ingest or load documents first.', 'warning');
        return;
    }
    
    showLoading('Searching documents with GPT-4o...');
    
    try {
        const response = await fetch(`${API_BASE}/api/query`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ question })
        });
        
        const data = await response.json();
        
        if (data.error) {
            showMessage(data.error, 'error');
        } else {
            displayResponse(data.answer, data.sources);
        }
    } catch (error) {
        console.error('Query error:', error);
        showMessage('Failed to process query. Please try again.', 'error');
    } finally {
        hideLoading();
    }
}

/**
 * Handle document ingestion
 */
async function handleIngest() {
    if (!isApiConfigured) {
        showMessage('Please configure your Azure OpenAI API key first.', 'warning');
        return;
    }
    
    if (uploadedFiles.length === 0) {
        showMessage('Please upload PDF files first.', 'warning');
        return;
    }
    
    if (!confirm(`This will ingest ${uploadedFiles.length} PDF file(s) into the vector store. Continue?`)) {
        return;
    }
    
    showLoading(`Uploading and ingesting ${uploadedFiles.length} PDF(s)... This may take a few minutes.`);
    elements.ingestBtn.disabled = true;
    
    try {
        // Create FormData with all files
        const formData = new FormData();
        uploadedFiles.forEach(file => {
            formData.append('files', file);
        });
        
        const response = await fetch(`${API_BASE}/api/ingest`, {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (data.success) {
            showMessage(data.message, 'success');
            isVectorStoreReady = true;
            // Clear uploaded files after successful ingestion
            uploadedFiles = [];
            updateFileList();
            updateStatus();
            updateUIState();
        } else {
            showMessage(data.message, 'error');
        }
    } catch (error) {
        console.error('Ingestion error:', error);
        showMessage('Failed to ingest documents. Check console for details.', 'error');
    } finally {
        hideLoading();
        updateUIState();
    }
}

/**
 * Handle loading existing vector store
 */
async function handleLoad() {
    if (!isApiConfigured) {
        showMessage('Please configure your Azure OpenAI API key first.', 'warning');
        return;
    }
    
    showLoading('Loading vector store...');
    
    try {
        const response = await fetch(`${API_BASE}/api/load`, {
            method: 'POST'
        });
        
        const data = await response.json();
        
        if (data.success) {
            showMessage(data.message, 'success');
            isVectorStoreReady = true;
            updateStatus();
            updateUIState();
        } else {
            showMessage(data.message, 'warning');
        }
    } catch (error) {
        console.error('Load error:', error);
        showMessage('Failed to load vector store.', 'error');
    } finally {
        hideLoading();
    }
}

/**
 * Handle clearing the vector store
 */
async function handleClearStore() {
    if (!confirm('This will delete the vector store and all ingested documents. Are you sure?')) {
        return;
    }
    
    showLoading('Clearing vector store...');
    
    try {
        const response = await fetch(`${API_BASE}/api/clear`, {
            method: 'POST'
        });
        
        const data = await response.json();
        
        if (data.success) {
            showMessage(data.message, 'success');
            isVectorStoreReady = false;
            updateStatus();
            updateUIState();
        } else {
            showMessage(data.message, 'error');
        }
    } catch (error) {
        console.error('Clear error:', error);
        showMessage('Failed to clear vector store.', 'error');
    } finally {
        hideLoading();
    }
}

/**
 * Display query response
 */
function displayResponse(answer, sources) {
    // Format the answer with markdown-like styling
    let formattedAnswer = answer
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        .replace(/\n\n/g, '</p><p>')
        .replace(/\n/g, '<br>');
    
    elements.responseContent.innerHTML = `<p>${formattedAnswer}</p>`;
    
    // Display sources
    if (sources && sources.length > 0) {
        elements.sourcesList.innerHTML = sources.map(source => `
            <span class="source-tag">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
                    <polyline points="14,2 14,8 20,8"/>
                </svg>
                ${source}
            </span>
        `).join('');
        elements.sourcesSection.classList.add('visible');
    } else {
        elements.sourcesSection.classList.remove('visible');
    }
}

/**
 * Clear the response area
 */
function clearResponse() {
    elements.responseContent.innerHTML = '<p class="placeholder-text">Your answer will appear here...</p>';
    elements.sourcesSection.classList.remove('visible');
    elements.sourcesList.innerHTML = '';
}

/**
 * Show a temporary message in the response area
 */
function showMessage(message, type = 'info') {
    const colors = {
        success: '#10b981',
        warning: '#f59e0b',
        error: '#ef4444',
        info: '#0078d4'
    };
    
    elements.responseContent.innerHTML = `
        <p style="color: ${colors[type]}">
            ${message}
        </p>
    `;
    elements.sourcesSection.classList.remove('visible');
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', init);
