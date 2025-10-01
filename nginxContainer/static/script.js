// Global state
let isAgentRunning = false;
let currentTask = null;

// API endpoints
const API_BASE = '/api/v1';
const ENDPOINTS = {
    health: `${API_BASE}/health`,
    status: `${API_BASE}/status`,
    agentRun: `${API_BASE}/agent/run`,
    notebooks: `${API_BASE}/notebooks`,
    agentDownload: `${API_BASE}/agent/download`,
    agentNotebook: `${API_BASE}/agent/notebook`
};

// DOM elements
const elements = {
    taskInput: document.getElementById('task-input'),
    filenameInput: document.getElementById('filename-input'),
    runAgentBtn: document.getElementById('run-agent-btn'),
    clearTaskBtn: document.getElementById('clear-task-btn'),
    progressSection: document.getElementById('progress-section'),
    progressFill: document.getElementById('progress-fill'),
    progressText: document.getElementById('progress-text'),
    resultsSection: document.getElementById('results-section'),
    resultsContent: document.getElementById('results-content'),
    notebooksGrid: document.getElementById('notebooks-grid'),
    refreshNotebooksBtn: document.getElementById('refresh-notebooks-btn'),
    loadingModal: document.getElementById('loading-modal'),
    agentStatus: document.getElementById('agent-status'),
    mcpStatus: document.getElementById('mcp-status'),
    agentStatusText: document.getElementById('agent-status-text'),
    mcpStatusText: document.getElementById('mcp-status-text')
};

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
    setupEventListeners();
    checkSystemStatus();
    loadNotebooks();
});

function initializeApp() {
    console.log('🚀 MCP Notebook Agent Dashboard initialized');
    
    // Set default task if empty
    if (!elements.taskInput.value.trim()) {
        elements.taskInput.value = "Create a comprehensive data analysis notebook with pandas, matplotlib, and seaborn. Include examples of data loading, cleaning, exploratory data analysis, and visualization techniques.";
    }
}

function setupEventListeners() {
    // Agent task buttons
    elements.runAgentBtn.addEventListener('click', runAgentTask);
    elements.clearTaskBtn.addEventListener('click', clearTask);
    
    // Notebook management
    elements.refreshNotebooksBtn.addEventListener('click', loadNotebooks);
    
    // Quick action buttons
    document.querySelectorAll('.action-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const task = this.getAttribute('data-task');
            elements.taskInput.value = task;
            elements.taskInput.focus();
        });
    });
    
    // Enter key in task input
    elements.taskInput.addEventListener('keydown', function(e) {
        if (e.ctrlKey && e.key === 'Enter') {
            runAgentTask();
        }
    });
}

async function checkSystemStatus() {
    try {
        // Check agent health
        const healthResponse = await fetch(ENDPOINTS.health);
        const healthData = await healthResponse.json();
        
        updateStatusIndicator(elements.agentStatus, elements.agentStatusText, 
            healthData.status === 'healthy', 'Connected', 'Disconnected');
        
        // Check detailed status
        const statusResponse = await fetch(ENDPOINTS.status);
        const statusData = await statusResponse.json();
        
        updateStatusIndicator(elements.mcpStatus, elements.mcpStatusText,
            statusData.mcp_connected, 'Connected', 'Disconnected');
            
        console.log('📊 System Status:', { healthData, statusData });
        
    } catch (error) {
        console.error('❌ Failed to check system status:', error);
        updateStatusIndicator(elements.agentStatus, elements.agentStatusText, false, 'Connected', 'Error');
        updateStatusIndicator(elements.mcpStatus, elements.mcpStatusText, false, 'Connected', 'Error');
    }
}

function updateStatusIndicator(element, textElement, isOnline, onlineText, offlineText) {
    element.classList.remove('online', 'offline', 'checking');
    textElement.textContent = isOnline ? onlineText : offlineText;
    element.classList.add(isOnline ? 'online' : 'offline');
}

async function runAgentTask() {
    const task = elements.taskInput.value.trim();
    if (!task) {
        showNotification('Please enter a task description', 'error');
        return;
    }
    
    if (isAgentRunning) {
        showNotification('Agent is already running a task', 'warning');
        return;
    }
    
    try {
        isAgentRunning = true;
        currentTask = task;
        
        // Update UI
        elements.runAgentBtn.disabled = true;
        elements.runAgentBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Running...';
        showProgressSection();
        hideResultsSection();
        
        // Prepare request
        const filename = elements.filenameInput.value.trim() || generateFilename(task);
        const requestData = {
            task: task,
            save_notebook: true,
            notebook_filename: filename
        };
        
        console.log('🤖 Starting agent task:', requestData);
        
        // Simulate progress updates
        updateProgress(10, 'Initializing agent...');
        
        setTimeout(() => updateProgress(30, 'Analyzing task requirements...'), 500);
        setTimeout(() => updateProgress(50, 'Generating notebook structure...'), 1500);
        setTimeout(() => updateProgress(70, 'Creating cells and content...'), 3000);
        setTimeout(() => updateProgress(90, 'Finalizing and saving...'), 5000);
        
        // Make API call
        const response = await fetch(ENDPOINTS.agentRun, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(requestData)
        });
        
        const result = await response.json();
        console.log('📋 Agent result:', result);
        
        updateProgress(100, 'Task completed!');
        
        setTimeout(() => {
            hideProgressSection();
            displayResults(result, filename);
            loadNotebooks(); // Refresh notebooks list
        }, 1000);
        
    } catch (error) {
        console.error('❌ Agent task failed:', error);
        hideProgressSection();
        showNotification('Failed to run agent task: ' + error.message, 'error');
    } finally {
        isAgentRunning = false;
        elements.runAgentBtn.disabled = false;
        elements.runAgentBtn.innerHTML = '<i class="fas fa-play"></i> Run Agent';
    }
}

function generateFilename(task) {
    const words = task.toLowerCase().split(' ').slice(0, 3);
    const cleanWords = words.map(word => word.replace(/[^a-z0-9]/g, '')).filter(word => word);
    return cleanWords.join('_') + '_notebook.ipynb';
}

function showProgressSection() {
    elements.progressSection.style.display = 'block';
    elements.progressFill.style.width = '0%';
}

function hideProgressSection() {
    elements.progressSection.style.display = 'none';
}

function updateProgress(percentage, text) {
    elements.progressFill.style.width = percentage + '%';
    elements.progressText.textContent = text;
}

function displayResults(result, filename) {
    elements.resultsSection.style.display = 'block';
    
    const success = result.success;
    const className = success ? 'text-success' : 'text-error';
    const icon = success ? 'fa-check-circle' : 'fa-exclamation-circle';
    
    let html = `
        <div class="result-item">
            <h4 class="${className}">
                <i class="fas ${icon}"></i> 
                ${success ? 'Task Completed Successfully!' : 'Task Failed'}
            </h4>
            <p><strong>Task:</strong> ${result.task}</p>
            <p><strong>Attempts:</strong> ${result.attempts}</p>
            <p><strong>Outputs:</strong> ${result.outputs ? result.outputs.length : 0} steps</p>
    `;
    
    if (result.outputs && result.outputs.length > 0) {
        html += '<div class="mt-20"><strong>Agent Steps:</strong><ul>';
        result.outputs.forEach((output, index) => {
            html += `<li><strong>Step ${index + 1}:</strong> ${output.substring(0, 200)}${output.length > 200 ? '...' : ''}</li>`;
        });
        html += '</ul></div>';
    }
    
    if (success && filename) {
        html += `
            <div class="mt-20">
                <a href="${ENDPOINTS.agentDownload}/${filename}" class="download-btn" download>
                    <i class="fas fa-download"></i> Download Notebook
                </a>
            </div>
        `;
    }
    
    if (result.error) {
        html += `<div class="mt-20 text-error"><strong>Error:</strong> ${result.error}</div>`;
    }
    
    html += '</div>';
    elements.resultsContent.innerHTML = html;
}

function hideResultsSection() {
    elements.resultsSection.style.display = 'none';
}

function clearTask() {
    elements.taskInput.value = '';
    elements.filenameInput.value = '';
    hideProgressSection();
    hideResultsSection();
    elements.taskInput.focus();
}

async function loadNotebooks() {
    try {
        elements.refreshNotebooksBtn.disabled = true;
        elements.refreshNotebooksBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Loading...';
        
        const response = await fetch(ENDPOINTS.notebooks);
        const data = await response.json();
        
        console.log('📚 Notebooks loaded:', data);
        displayNotebooks(data.notebooks || []);
        
    } catch (error) {
        console.error('❌ Failed to load notebooks:', error);
        elements.notebooksGrid.innerHTML = '<p class="text-error">Failed to load notebooks</p>';
    } finally {
        elements.refreshNotebooksBtn.disabled = false;
        elements.refreshNotebooksBtn.innerHTML = '<i class="fas fa-sync"></i> Refresh';
    }
}

function displayNotebooks(notebooks) {
    if (!notebooks || notebooks.length === 0) {
        elements.notebooksGrid.innerHTML = `
            <div class="notebook-card">
                <h4><i class="fas fa-info-circle"></i> No Notebooks Yet</h4>
                <p>Create your first notebook using the AI agent above!</p>
            </div>
        `;
        return;
    }
    
    const notebooksHtml = notebooks.map(notebook => `
        <div class="notebook-card">
            <h4><i class="fas fa-book"></i> ${notebook}</h4>
            <p>Created: ${new Date().toLocaleDateString()}</p>
            <div class="notebook-actions">
                <a href="${ENDPOINTS.agentDownload}/${notebook}" class="btn btn-primary" download>
                    <i class="fas fa-download"></i> Download
                </a>
                <button class="btn btn-secondary" onclick="deleteNotebook('${notebook}')">
                    <i class="fas fa-trash"></i> Delete
                </button>
            </div>
        </div>
    `).join('');
    
    elements.notebooksGrid.innerHTML = notebooksHtml;
}

async function deleteNotebook(filename) {
    if (!confirm(`Are you sure you want to delete "${filename}"?`)) {
        return;
    }
    
    try {
        const response = await fetch(`${ENDPOINTS.notebooks}/${filename}`, {
            method: 'DELETE'
        });
        
        if (response.ok) {
            showNotification('Notebook deleted successfully', 'success');
            loadNotebooks();
        } else {
            throw new Error('Failed to delete notebook');
        }
    } catch (error) {
        console.error('❌ Failed to delete notebook:', error);
        showNotification('Failed to delete notebook: ' + error.message, 'error');
    }
}

function showNotification(message, type = 'info') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.innerHTML = `
        <div class="notification-content">
            <i class="fas ${getNotificationIcon(type)}"></i>
            <span>${message}</span>
        </div>
    `;
    
    // Add styles
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: ${getNotificationColor(type)};
        color: white;
        padding: 15px 20px;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        z-index: 1001;
        opacity: 0;
        transform: translateX(100%);
        transition: all 0.3s ease;
    `;
    
    document.body.appendChild(notification);
    
    // Animate in
    setTimeout(() => {
        notification.style.opacity = '1';
        notification.style.transform = 'translateX(0)';
    }, 100);
    
    // Auto remove
    setTimeout(() => {
        notification.style.opacity = '0';
        notification.style.transform = 'translateX(100%)';
        setTimeout(() => {
            document.body.removeChild(notification);
        }, 300);
    }, 4000);
}

function getNotificationIcon(type) {
    const icons = {
        success: 'fa-check-circle',
        error: 'fa-exclamation-circle',
        warning: 'fa-exclamation-triangle',
        info: 'fa-info-circle'
    };
    return icons[type] || icons.info;
}

function getNotificationColor(type) {
    const colors = {
        success: '#4CAF50',
        error: '#f44336',
        warning: '#ff9800',
        info: '#2196F3'
    };
    return colors[type] || colors.info;
}

// Auto-refresh status every 30 seconds
setInterval(checkSystemStatus, 30000);

// Auto-refresh notebooks every 2 minutes
setInterval(loadNotebooks, 120000);

// Keyboard shortcuts
document.addEventListener('keydown', function(e) {
    // Ctrl+Enter to run agent
    if (e.ctrlKey && e.key === 'Enter' && !isAgentRunning) {
        runAgentTask();
    }
    
    // Ctrl+R to refresh notebooks
    if (e.ctrlKey && e.key === 'r') {
        e.preventDefault();
        loadNotebooks();
    }
    
    // Escape to clear task
    if (e.key === 'Escape') {
        clearTask();
    }
});

// Console welcome message
console.log(`
🤖 MCP Notebook Agent Dashboard
================================
Shortcuts:
- Ctrl+Enter: Run agent task
- Ctrl+R: Refresh notebooks  
- Escape: Clear task

API Endpoints:
${Object.entries(ENDPOINTS).map(([key, url]) => `- ${key}: ${url}`).join('\n')}
`);

// Export for debugging
window.MCPDashboard = {
    elements,
    API_BASE,
    ENDPOINTS,
    runAgentTask,
    loadNotebooks,
    checkSystemStatus,
    deleteNotebook
};