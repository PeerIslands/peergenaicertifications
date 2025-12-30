// MCP MongoDB Search - Frontend JavaScript

const API_BASE = '';

// DOM Elements
const queryInput = document.getElementById('queryInput');
const submitBtn = document.getElementById('submitBtn');
const clearBtn = document.getElementById('clearBtn');
const resultsContainer = document.getElementById('resultsContainer');
const examplesContainer = document.getElementById('examplesContainer');
const statusIndicator = document.getElementById('statusIndicator');

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    loadExamples();
    checkHealth();
    
    // Event listeners
    submitBtn.addEventListener('click', handleSubmit);
    clearBtn.addEventListener('click', handleClear);
    
    // Allow Enter+Shift for new line, Enter alone to submit
    queryInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSubmit();
        }
    });
});

// Load example queries
async function loadExamples() {
    try {
        const response = await fetch(`${API_BASE}/api/examples`);
        const examples = await response.json();
        
        examplesContainer.innerHTML = examples.map(example => `
            <div class="example-card" onclick="useExample('${escapeHtml(example.query)}')">
                <div class="example-desc">${escapeHtml(example.description)}</div>
                <div class="example-query">${escapeHtml(example.query)}</div>
            </div>
        `).join('');
    } catch (error) {
        console.error('Error loading examples:', error);
    }
}

// Use example query
function useExample(query) {
    queryInput.value = query;
    queryInput.focus();
    // Optionally auto-submit
    // handleSubmit();
}

// Handle query submission
async function handleSubmit() {
    const query = queryInput.value.trim();
    
    if (!query) {
        showError('Please enter a query');
        return;
    }
    
    // Disable button and show loading
    submitBtn.disabled = true;
    submitBtn.querySelector('.btn-text').style.display = 'none';
    submitBtn.querySelector('.btn-loader').style.display = 'inline';
    
    // Show loading in results
    resultsContainer.innerHTML = '<div class="loading">Processing query</div>';
    
    try {
        const response = await fetch(`${API_BASE}/api/query`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ query })
        });
        
        const result = await response.json();
        displayResult(result, query);
    } catch (error) {
        console.error('Error:', error);
        showError(`Error: ${error.message}`);
    } finally {
        // Re-enable button
        submitBtn.disabled = false;
        submitBtn.querySelector('.btn-text').style.display = 'inline';
        submitBtn.querySelector('.btn-loader').style.display = 'none';
    }
}

// Display query result
function displayResult(result, query) {
    if (result.success) {
        let html = `
            <div class="result-card">
                <div class="result-header">
                    <div class="result-title">Query Result</div>
                    <span class="result-badge badge-success">Success</span>
                </div>
                <div class="result-info">
                    <strong>Operation:</strong> ${escapeHtml(result.operation || 'N/A')}<br>
                    <strong>Collection:</strong> ${escapeHtml(result.collection || 'N/A')}
                </div>
        `;
        
        if (result.documents && result.documents.length > 0) {
            html += `
                <div class="result-info">
                    <strong>Found:</strong> ${result.count || result.documents.length} document(s)
                </div>
                <div class="documents-list">
                    <h4>Documents:</h4>
            `;
            
            result.documents.forEach((doc, index) => {
                html += `
                    <div class="document-item">
                        <strong>Document ${index + 1}:</strong>
                        <pre>${JSON.stringify(doc, null, 2)}</pre>
                    </div>
                `;
            });
            
            html += `</div>`;
        }
        
        if (result.filters) {
            html += `
                <div class="result-info">
                    <strong>Filters Applied:</strong>
                    <pre style="margin-top: 8px;">${JSON.stringify(result.filters, null, 2)}</pre>
                </div>
            `;
        }
        
        if (result.updates) {
            html += `
                <div class="result-info">
                    <strong>Updates Applied:</strong>
                    <pre style="margin-top: 8px;">${JSON.stringify(result.updates, null, 2)}</pre>
                </div>
            `;
        }
        
        if (result.result) {
            html += `
                <div class="result-info">
                    <strong>Result:</strong>
                    <pre style="margin-top: 8px;">${JSON.stringify(result.result, null, 2)}</pre>
                </div>
            `;
        }
        
        // Show success message for insert operations
        if (result.operation === 'insert' && result.success) {
            html += `
                <div class="result-info" style="background: #d4edda; border-left: 4px solid #28a745; padding: 15px; margin-top: 15px; border-radius: 6px;">
                    <strong style="color: #155724;">✓ Record inserted successfully!</strong>
                    <p style="margin: 10px 0 0 0; color: #155724;">You can verify by querying: "find all documents from ${result.collection} collection"</p>
                </div>
            `;
        }
        
        // Show success message for update operations
        if (result.operation === 'update' && result.success) {
            html += `
                <div class="result-info" style="background: #d4edda; border-left: 4px solid #28a745; padding: 15px; margin-top: 15px; border-radius: 6px;">
                    <strong style="color: #155724;">✓ Record updated successfully!</strong>
                </div>
            `;
        }
        
        // Show success message for delete operations
        if (result.operation === 'delete' && result.success) {
            html += `
                <div class="result-info" style="background: #d4edda; border-left: 4px solid #28a745; padding: 15px; margin-top: 15px; border-radius: 6px;">
                    <strong style="color: #155724;">✓ Record(s) deleted successfully!</strong>
                </div>
            `;
        }
        
        html += `</div>`;
        resultsContainer.innerHTML = html;
    } else {
        showError(result.error || 'Unknown error occurred');
    }
}

// Show error message
function showError(message) {
    resultsContainer.innerHTML = `
        <div class="result-card">
            <div class="result-header">
                <div class="result-title">Error</div>
                <span class="result-badge badge-error">Failed</span>
            </div>
            <div class="error-message">
                ${escapeHtml(message)}
            </div>
        </div>
    `;
}

// Clear input and results
function handleClear() {
    queryInput.value = '';
    resultsContainer.innerHTML = `
        <div class="welcome-message">
            <h2>Welcome! 👋</h2>
            <p>Enter a natural language query above to search your MongoDB database.</p>
            <p>Try clicking on one of the example queries to get started.</p>
        </div>
    `;
    queryInput.focus();
}

// Check health status
async function checkHealth() {
    try {
        const response = await fetch(`${API_BASE}/api/health`);
        const health = await response.json();
        
        if (health.initialized) {
            statusIndicator.textContent = '● Ready';
            statusIndicator.style.color = '#28a745';
        } else {
            statusIndicator.textContent = '● Not Initialized';
            statusIndicator.style.color = '#dc3545';
        }
        
        // Always update database name from API
        const dbNameElement = document.getElementById('databaseName');
        if (health.database && dbNameElement) {
            dbNameElement.textContent = health.database;
        }
    } catch (error) {
        console.error('Health check failed:', error);
        statusIndicator.textContent = '● Error';
        statusIndicator.style.color = '#dc3545';
    }
}

// Escape HTML to prevent XSS
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

