// ==========================================
// EDITH Web UI - JavaScript
// ==========================================

const API_BASE_URL = 'http://localhost:5000/api';

// DOM Elements
const chatMessages = document.getElementById('chatMessages');
const userInput = document.getElementById('userInput');
const sendBtn = document.getElementById('sendBtn');
const clearBtn = document.getElementById('clearBtn');
const summaryBtn = document.getElementById('summaryBtn');
const statsBtn = document.getElementById('statsBtn');
const statsPanel = document.getElementById('statsPanel');
const typingIndicator = document.getElementById('typingIndicator');
const toastContainer = document.getElementById('toastContainer');

// State
let isProcessing = false;

// ==========================================
// INITIALIZATION
// ==========================================

document.addEventListener('DOMContentLoaded', () => {
    setupEventListeners();
    checkAPIHealth();
    autoResizeTextarea();
});

function setupEventListeners() {
    // Send message
    sendBtn.addEventListener('click', handleSendMessage);
    userInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSendMessage();
        }
    });
    
    // Auto-resize textarea
    userInput.addEventListener('input', autoResizeTextarea);
    
    // Clear chat
    clearBtn.addEventListener('click', clearChat);
    
    // Summary
    summaryBtn.addEventListener('click', handleSummary);
    
    // Stats toggle
    statsBtn.addEventListener('click', toggleStats);
}

// ==========================================
// MESSAGE HANDLING
// ==========================================

async function handleSendMessage() {
    const message = userInput.value.trim();
    
    if (!message || isProcessing) return;
    
    // Add user message to chat
    addMessage(message, 'user');
    
    // Clear input
    userInput.value = '';
    autoResizeTextarea();
    
    // Show typing indicator
    showTyping();
    isProcessing = true;
    sendBtn.disabled = true;
    
    try {
        // Send to API
        const response = await fetch(`${API_BASE_URL}/query`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ query: message })
        });
        
        if (!response.ok) {
            throw new Error('Failed to get response from EDITH');
        }
        
        const data = await response.json();
        
        // Hide typing and add response
        hideTyping();
        addMessage(
            data.answer,
            'assistant',
            {
                mode: data.mode,
                confidence: data.confidence,
                sources: data.sources,
                num_sources: data.num_sources
            }
        );
        
    } catch (error) {
        console.error('Error:', error);
        hideTyping();
        addMessage(
            "Sorry, I encountered an error. Please make sure the EDITH API server is running.",
            'assistant',
            { mode: 'error' }
        );
        showToast('Connection error. Is the API server running?', 'error');
    } finally {
        isProcessing = false;
        sendBtn.disabled = false;
        userInput.focus();
    }
}

function addMessage(text, sender, metadata = {}) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${sender}-message`;
    
    // Avatar
    const avatar = document.createElement('div');
    avatar.className = 'message-avatar';
    avatar.textContent = sender === 'user' ? '👤' : '🤖';
    
    // Content container
    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    
    // Message text
    const textDiv = document.createElement('div');
    textDiv.className = 'message-text';
    
    // Format text with markdown-like features
    const formattedText = formatMessage(text);
    textDiv.innerHTML = formattedText;
    
    contentDiv.appendChild(textDiv);
    
    // Add metadata for assistant messages
    if (sender === 'assistant' && metadata.mode) {
        const metaDiv = document.createElement('div');
        metaDiv.className = 'message-meta';
        
        // Mode badge
        const modeBadge = document.createElement('span');
        modeBadge.className = `mode-badge mode-${metadata.mode}`;
        const modeEmoji = metadata.mode === 'rag' ? '🔍' : '💬';
        modeBadge.textContent = `${modeEmoji} ${metadata.mode}`;
        metaDiv.appendChild(modeBadge);
        
        // Confidence (for RAG)
        if (metadata.mode === 'rag' && metadata.confidence) {
            const confidence = document.createElement('span');
            confidence.textContent = `Confidence: ${(metadata.confidence * 100).toFixed(0)}%`;
            metaDiv.appendChild(confidence);
        }
        
        contentDiv.appendChild(metaDiv);
        
        // Sources
        if (metadata.sources && metadata.sources.length > 0) {
            const sourcesDiv = document.createElement('div');
            sourcesDiv.className = 'sources';
            
            const sourcesTitle = document.createElement('div');
            sourcesTitle.className = 'sources-title';
            sourcesTitle.textContent = `📎 Sources (${metadata.num_sources}):`;
            sourcesDiv.appendChild(sourcesTitle);
            
            metadata.sources.slice(0, 3).forEach(source => {
                const sourceItem = document.createElement('div');
                sourceItem.className = 'source-item';
                sourceItem.textContent = `• ${source.filename}`;
                sourcesDiv.appendChild(sourceItem);
            });
            
            contentDiv.appendChild(sourcesDiv);
        }
    }
    
    messageDiv.appendChild(avatar);
    messageDiv.appendChild(contentDiv);
    
    chatMessages.appendChild(messageDiv);
    scrollToBottom();
}

function formatMessage(text) {
    // Simple markdown-like formatting
    let formatted = text
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')  // Bold
        .replace(/\*(.*?)\*/g, '<em>$1</em>')  // Italic
        .replace(/`(.*?)`/g, '<code>$1</code>')  // Inline code
        .replace(/\n/g, '<br>');  // Line breaks
    
    return formatted;
}

function showTyping() {
    typingIndicator.style.display = 'flex';
    scrollToBottom();
}

function hideTyping() {
    typingIndicator.style.display = 'none';
}

function scrollToBottom() {
    setTimeout(() => {
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }, 100);
}

// ==========================================
// SUMMARY
// ==========================================

async function handleSummary() {
    if (isProcessing) return;
    
    showToast('Generating summary...', 'info');
    showTyping();
    isProcessing = true;
    summaryBtn.disabled = true;
    
    try {
        const response = await fetch(`${API_BASE_URL}/summary`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ style: 'comprehensive' })
        });
        
        if (!response.ok) {
            throw new Error('Failed to generate summary');
        }
        
        const data = await response.json();
        
        hideTyping();
        addMessage(
            `📊 **Summary of Your Notes:**\n\n${data.summary}`,
            'assistant',
            { mode: 'rag' }
        );
        
        showToast('Summary generated!', 'success');
        
    } catch (error) {
        console.error('Error:', error);
        hideTyping();
        showToast('Failed to generate summary', 'error');
    } finally {
        isProcessing = false;
        summaryBtn.disabled = false;
    }
}

// ==========================================
// STATS
// ==========================================

async function toggleStats() {
    const isVisible = statsPanel.style.display !== 'none';
    
    if (isVisible) {
        statsPanel.style.display = 'none';
    } else {
        await loadStats();
        statsPanel.style.display = 'block';
    }
}

async function loadStats() {
    try {
        const response = await fetch(`${API_BASE_URL}/stats`);
        
        if (!response.ok) {
            throw new Error('Failed to load stats');
        }
        
        const data = await response.json();
        
        document.getElementById('statVectors').textContent = data.total_vectors || 0;
        document.getElementById('statDimension').textContent = data.dimension || 0;
        document.getElementById('statFullness').textContent = 
            `${((data.index_fullness || 0) * 100).toFixed(1)}%`;
        
    } catch (error) {
        console.error('Error loading stats:', error);
        showToast('Failed to load stats', 'error');
    }
}

// ==========================================
// UTILITIES
// ==========================================

function clearChat() {
    // Keep only the welcome message
    const messages = chatMessages.querySelectorAll('.message');
    messages.forEach((msg, index) => {
        if (index > 0) {  // Skip first (welcome) message
            msg.remove();
        }
    });
    showToast('Chat cleared!', 'success');
}

function autoResizeTextarea() {
    userInput.style.height = 'auto';
    userInput.style.height = userInput.scrollHeight + 'px';
}

async function checkAPIHealth() {
    try {
        const response = await fetch(`${API_BASE_URL}/health`);
        if (response.ok) {
            const data = await response.json();
            console.log('✅ API Health:', data);
        } else {
            throw new Error('API unhealthy');
        }
    } catch (error) {
        console.error('❌ API Connection Failed:', error);
        showToast('Warning: Cannot connect to EDITH API', 'error');
    }
}

function showToast(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    
    const icon = type === 'success' ? '✅' : 
                 type === 'error' ? '❌' : 
                 'ℹ️';
    
    toast.innerHTML = `
        <span style="font-size: 20px;">${icon}</span>
        <span>${message}</span>
    `;
    
    toastContainer.appendChild(toast);
    
    // Auto remove after 3 seconds
    setTimeout(() => {
        toast.style.opacity = '0';
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

// ==========================================
// KEYBOARD SHORTCUTS
// ==========================================

document.addEventListener('keydown', (e) => {
    // Ctrl/Cmd + K to focus input
    if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault();
        userInput.focus();
    }
    
    // Ctrl/Cmd + L to clear chat
    if ((e.ctrlKey || e.metaKey) && e.key === 'l') {
        e.preventDefault();
        clearChat();
    }
});
