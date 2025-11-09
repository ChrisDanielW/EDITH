// ==========================================
// EDITH Web UI - JavaScript
// ==========================================

const API_BASE_URL = 'http://localhost:5000/api';

// DOM Elements
const chatMessages = document.getElementById('chatMessages');
const userInput = document.getElementById('userInput');
const sendBtn = document.getElementById('sendBtn');
const clearBtn = document.getElementById('clearBtn');
const statsBtn = document.getElementById('statsBtn');
const uploadBtn = document.getElementById('uploadBtn');
const statsPanel = document.getElementById('statsPanel');
const typingIndicator = document.getElementById('typingIndicator');
const toastContainer = document.getElementById('toastContainer');
const uploadModal = document.getElementById('uploadModal');
const closeUploadModal = document.getElementById('closeUploadModal');
const uploadArea = document.getElementById('uploadArea');
const fileInput = document.getElementById('fileInput');
const uploadProgress = document.getElementById('uploadProgress');
const progressFill = document.getElementById('progressFill');
const uploadStatus = document.getElementById('uploadStatus');
const clearModal = document.getElementById('clearModal');
const closeClearModal = document.getElementById('closeClearModal');
const cancelClear = document.getElementById('cancelClear');
const confirmClear = document.getElementById('confirmClear');

// State
let isProcessing = false;

// Welcome messages pool
const WELCOME_MESSAGES = [
    {
        greeting: "Hey there! I'm EDITH 👋",
        message: "I'm here to help you make sense of your notes. Got any questions, or just want to chat?"
    },
    {
        greeting: "Hello! EDITH at your service ✨",
        message: "I can dig through your notes to find answers, or we can just have a casual conversation. What's on your mind?"
    },
    {
        greeting: "Hi! Ready to dive into your notes? 📚",
        message: "Ask me anything about what you've uploaded, or just say hi—I'm pretty good at both!"
    },
    {
        greeting: "Let's get studying! 🎯",
        message: "I'm EDITH, your personal notes assistant. I can help you find information or just keep you company while you work."
    },
    {
        greeting: "Hey! EDITH here 😊",
        message: "Think of me as your study buddy who actually remembers everything you've written down. What can I help with?"
    },
    {
        greeting: "What's up? I'm EDITH! 👓",
        message: "I'm here to help you with your notes—whether you need specific info or just want to chat about what you're learning."
    },
    {
        greeting: "Good to see you! 🌟",
        message: "I'm EDITH, and I'm here to make your notes actually useful. Ask me questions, or we can just talk!"
    },
    {
        greeting: "Hey there, scholar! 📖",
        message: "EDITH here. I've got your notes memorized, so fire away with questions—or just chat if you need a break!"
    },
    {
        greeting: "Hello! Let's make learning easier 💡",
        message: "I'm EDITH. I can pull up info from your notes in seconds, or we can just have a friendly conversation."
    },
    {
        greeting: "Hi! Your notes assistant is online, wait no, not really I guess lol ⚡",
        message: "I'm EDITH—I can help you understand your study materials or just be a conversational companion. Your call!"
    },
    {
        greeting: "EDITH reporting for duty 🎓",
        message: "I'm here to help you navigate your notes and answer questions. Or we can just chat—I'm surprisingly good company!"
    },
    {
        greeting: "Hey! Time to unlock your notes 🔓",
        message: "I'm EDITH, and I turn your pile of notes into actual knowledge you can access. What do you want to explore?"
    },
    {
        greeting: "Hello there! Ready to learn? 🌈",
        message: "I'm EDITH—think of me as your notes on steroids. I can find answers fast or just hang out and chat with you."
    }
];

// Get random welcome message
function getRandomWelcomeMessage() {
    const message = WELCOME_MESSAGES[Math.floor(Math.random() * WELCOME_MESSAGES.length)];
    return `<p><strong>${message.greeting}</strong></p><p>${message.message}</p>`;
}

// ==========================================
// INITIALIZATION
// ==========================================

document.addEventListener('DOMContentLoaded', () => {
    loadRandomWelcomeMessage();
    setupEventListeners();
    checkAPIHealth();
    autoResizeTextarea();
});

function loadRandomWelcomeMessage() {
    const welcomeMessageDiv = document.querySelector('#welcomeMessage .message-text');
    if (welcomeMessageDiv) {
        welcomeMessageDiv.innerHTML = getRandomWelcomeMessage();
    }
}

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
    
    // Clear chat modal
    clearBtn.addEventListener('click', () => clearModal.style.display = 'flex');
    closeClearModal.addEventListener('click', () => clearModal.style.display = 'none');
    cancelClear.addEventListener('click', () => clearModal.style.display = 'none');
    confirmClear.addEventListener('click', () => {
        clearModal.style.display = 'none';
        performClearChat();
    });
    clearModal.addEventListener('click', (e) => {
        if (e.target === clearModal) clearModal.style.display = 'none';
    });
    
    // Stats toggle
    statsBtn.addEventListener('click', toggleStats);
    
    // Upload modal
    uploadBtn.addEventListener('click', () => uploadModal.style.display = 'flex');
    closeUploadModal.addEventListener('click', () => uploadModal.style.display = 'none');
    uploadModal.addEventListener('click', (e) => {
        if (e.target === uploadModal) uploadModal.style.display = 'none';
    });
    
    // Upload area interactions
    uploadArea.addEventListener('click', () => fileInput.click());
    fileInput.addEventListener('change', handleFileSelect);
    
    // Drag and drop
    uploadArea.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadArea.classList.add('dragging');
    });
    
    uploadArea.addEventListener('dragleave', () => {
        uploadArea.classList.remove('dragging');
    });
    
    uploadArea.addEventListener('drop', (e) => {
        e.preventDefault();
        uploadArea.classList.remove('dragging');
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            handleFileUpload(files[0]);
        }
    });
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
    // Show the clear confirmation modal
    clearModal.style.display = 'flex';
}

function performClearChat() {
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

// ==========================================
// FILE UPLOAD HANDLING
// ==========================================

function handleFileSelect(event) {
    const files = Array.from(event.target.files);
    if (files.length > 0) {
        handleMultipleFileUploads(files);
    }
}

async function handleMultipleFileUploads(files) {
    // Validate file types
    const allowedExtensions = ['.pdf', '.docx', '.pptx', '.txt', '.md', '.png', '.jpg', '.jpeg'];
    const validFiles = [];
    const invalidFiles = [];
    
    for (const file of files) {
        const fileExt = '.' + file.name.split('.').pop().toLowerCase();
        if (allowedExtensions.includes(fileExt)) {
            validFiles.push(file);
        } else {
            invalidFiles.push(file.name);
        }
    }
    
    if (invalidFiles.length > 0) {
        showToast(`Skipped ${invalidFiles.length} unsupported file(s)`, 'warning');
    }
    
    if (validFiles.length === 0) {
        showToast('No valid files to upload', 'error');
        return;
    }
    
    // Show progress
    uploadProgress.style.display = 'block';
    progressFill.style.width = '0%';
    uploadStatus.textContent = `Uploading ${validFiles.length} file(s)...`;
    uploadBtn.disabled = true;
    
    let successCount = 0;
    let errorCount = 0;
    let totalChunks = 0;
    
    try {
        for (let i = 0; i < validFiles.length; i++) {
            const file = validFiles[i];
            const progress = ((i / validFiles.length) * 100);
            progressFill.style.width = `${progress}%`;
            uploadStatus.textContent = `Uploading ${i + 1}/${validFiles.length}: ${file.name}...`;
            
            try {
                const result = await uploadSingleFile(file);
                successCount++;
                totalChunks += result.chunks;
            } catch (error) {
                console.error(`Error uploading ${file.name}:`, error);
                errorCount++;
            }
        }
        
        // Complete progress
        progressFill.style.width = '100%';
        uploadStatus.textContent = 'Upload complete!';
        
        // Show success message in chat
        if (successCount > 0) {
            addMessage(
                `✅ **Documents Uploaded Successfully**\n\n` +
                `📄 **Files Uploaded:** ${successCount}\n` +
                `📊 **Total Chunks Created:** ${totalChunks}\n` +
                (errorCount > 0 ? `⚠️ **Failed:** ${errorCount}\n` : '') +
                `\nYour documents have been processed and added to the knowledge base. You can now ask questions about them!`,
                'assistant',
                { mode: 'system' }
            );
            
            showToast(`Successfully uploaded ${successCount} file(s)`, 'success');
        }
        
        if (errorCount > 0) {
            showToast(`${errorCount} file(s) failed to upload`, 'error');
        }
        
        // Close modal after a delay
        setTimeout(() => {
            uploadModal.style.display = 'none';
            uploadProgress.style.display = 'none';
            fileInput.value = ''; // Reset file input
        }, 1500);
        
    } catch (error) {
        console.error('Upload error:', error);
        uploadStatus.textContent = 'Upload failed';
        progressFill.style.width = '0%';
        showToast(`Upload failed: ${error.message}`, 'error');
    } finally {
        uploadBtn.disabled = false;
    }
}

async function uploadSingleFile(file) {
    const formData = new FormData();
    formData.append('file', file);
    
    const response = await fetch(`${API_BASE_URL}/upload`, {
        method: 'POST',
        body: formData
    });
    
    if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Upload failed');
    }
    
    return await response.json();
}

// Legacy single file upload function for drag & drop compatibility
async function handleFileUpload(file) {
    handleMultipleFileUploads([file]);
}
