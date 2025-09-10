// Get DOM elements
const messagesContainer = document.getElementById('messages');
const messageInput = document.getElementById('messageInput');
const sendButton = document.getElementById('sendButton');
const loading = document.getElementById('loading');

// Configuration
const AI_AGENT_URL = 'http://localhost:9001';

/**
 * Add a message to the chat interface
 * @param {string} content - The message content
 * @param {boolean} isUser - Whether this is a user message
 */
function addMessage(content, isUser = false) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${isUser ? 'user-message' : 'bot-message'}`;
    
    // Support basic HTML in bot messages (like line breaks)
    if (isUser) {
        messageDiv.textContent = content;
    } else {
        messageDiv.innerHTML = content.replace(/\n/g, '<br>');
    }
    
    messagesContainer.appendChild(messageDiv);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

/**
 * Show or hide loading indicator
 * @param {boolean} show - Whether to show loading
 */
function showLoading(show) {
    loading.style.display = show ? 'block' : 'none';
    sendButton.disabled = show;
    messageInput.disabled = show;
}

/**
 * Send message to AI agent
 */
async function sendMessage() {
    const message = messageInput.value.trim();
    if (!message) return;

    // Add user message to chat
    addMessage(message, true);
    messageInput.value = '';
    showLoading(true);

    try {
        // Try the new structured endpoint first
        let response = await fetch(`${AI_AGENT_URL}/chat/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ message }),
        });

        // If that fails, try the legacy endpoint
        if (!response.ok && response.status === 404) {
            console.log('Trying legacy endpoint...');
            response = await fetch(`${AI_AGENT_URL}/chat`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ message }),
            });
        }

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status} - ${response.statusText}`);
        }

        const data = await response.json();
        const botResponse = data.response || 'Sorry, I could not process your request.';
        addMessage(botResponse);
        
    } catch (error) {
        console.error('Chat Error:', error);
        let errorMessage = '❌ Sorry, there was an error connecting to the AI agent. ';
        
        if (error.message.includes('Failed to fetch') || error.message.includes('NetworkError')) {
            errorMessage += 'Please make sure all services are running with: .\\run-app.ps1';
        } else {
            errorMessage += `Error: ${error.message}`;
        }
        
        addMessage(errorMessage);
    } finally {
        showLoading(false);
        messageInput.focus();
    }
}

/**
 * Check if AI agent is connected and responsive
 */
async function checkConnection() {
    try {
        console.log('Checking AI agent connection...');
        const response = await fetch(`${AI_AGENT_URL}/health`, {
            method: 'GET',
            timeout: 5000
        });
        
        if (response.ok) {
            const data = await response.json();
            addMessage('✅ Connected to AI Agent! You can start chatting.');
            console.log('AI Agent connected:', data);
        } else {
            addMessage('⚠️ AI Agent responded but may not be functioning properly. Please check the logs.');
        }
    } catch (error) {
        console.error('Connection check failed:', error);
        addMessage('❌ Cannot connect to AI Agent. Please make sure all services are running with: <strong>.\\run-app.ps1</strong>');
    }
}

/**
 * Initialize the chat interface
 */
function initializeChat() {
    // Focus input
    messageInput.focus();
    
    // Add event listeners
    sendButton.addEventListener('click', sendMessage);
    
    messageInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });
    
    // Check connection after a short delay
    setTimeout(checkConnection, 1000);
}

// Initialize when DOM is loaded
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeChat);
} else {
    initializeChat();
}
