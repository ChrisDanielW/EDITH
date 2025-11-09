// ==========================================
// EDITH Web UI - JavaScript
// ==========================================

const API_BASE_URL = 'http://localhost:5000/api';

// DOM Elements
const chatMessages = document.getElementById('chatMessages');
const userInput = document.getElementById('userInput');
const sendBtn = document.getElementById('sendBtn');
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
const leftSidebar = document.getElementById('leftSidebar');
const conversationsList = document.getElementById('conversationsList');
const newConversationBtn = document.getElementById('newConversationBtn');
const landingPage = document.getElementById('landingPage');
const landingWelcome = document.getElementById('landingWelcome');

// State
let isProcessing = false;
let currentConversationId = null;
let conversations = [];
let isLandingPage = true;

// Load conversations from localStorage
function loadConversations() {
    const saved = localStorage.getItem('edith_conversations');
    if (saved) {
        conversations = JSON.parse(saved);
    }
    
    // Always show landing page on initial load
    showLandingPage();
    
    renderConversationsList();
}

// Show landing page
function showLandingPage() {
    isLandingPage = true;
    landingPage.style.display = 'flex';
    chatMessages.style.display = 'none';
    currentConversationId = null;
    
    // Set a random welcome message
    const welcomeMsg = getRandomWelcomeMessage();
    landingWelcome.innerHTML = welcomeMsg;
    
    // Hide the new conversation button on landing page
    newConversationBtn.style.display = 'none';
    
    renderConversationsList();
}

// Hide landing page and show chat
function hideLandingPage() {
    isLandingPage = false;
    landingPage.style.display = 'none';
    chatMessages.style.display = 'flex';
    
    // Show the new conversation button when in a conversation
    newConversationBtn.style.display = 'flex';
}

// Save conversations to localStorage
function saveConversations() {
    localStorage.setItem('edith_conversations', JSON.stringify(conversations));
}

// Create a new conversation (called when user sends first message)
function createNewConversation(firstMessage) {
    // Find the highest conversation number to increment from
    let maxNumber = 0;
    conversations.forEach(conv => {
        const match = conv.title.match(/Conversation (\d+)/);
        if (match) {
            maxNumber = Math.max(maxNumber, parseInt(match[1]));
        }
    });
    const conversationNumber = maxNumber + 1;
    
    const conversation = {
        id: Date.now(),
        title: `Conversation ${conversationNumber}`,
        date: new Date().toISOString(),
        messages: []
    };
    
    conversations.unshift(conversation);
    currentConversationId = conversation.id;
    saveConversations();
    
    // Hide landing page and show chat
    hideLandingPage();
    chatMessages.innerHTML = ''; // Clear all messages
    
    renderConversationsList();
}

// Load a conversation
function loadConversation(conversationId) {
    currentConversationId = conversationId;
    const conversation = conversations.find(c => c.id === conversationId);
    
    if (!conversation) return;
    
    // Hide landing page and show chat
    hideLandingPage();
    
    // Clear current messages
    chatMessages.innerHTML = '';
    
    // Load saved messages
    conversation.messages.forEach(msg => {
        addMessage(msg.text, msg.role, msg.metadata, false); // false = don't save
    });
    
    renderConversationsList();
}

// Delete a conversation
function deleteConversation(conversationId, event) {
    event.stopPropagation();
    
    const index = conversations.findIndex(c => c.id === conversationId);
    if (index === -1) return;
    
    conversations.splice(index, 1);
    saveConversations();
    
    // If we deleted the current conversation, switch to another or show landing
    if (conversationId === currentConversationId) {
        if (conversations.length > 0) {
            loadConversation(conversations[0].id);
        } else {
            showLandingPage();
        }
    }
    
    renderConversationsList();
    showToast('Conversation deleted', 'success');
}

// Render conversations list
function renderConversationsList() {
    conversationsList.innerHTML = '';
    
    conversations.forEach(conversation => {
        const item = document.createElement('div');
        item.className = 'conversation-item';
        if (conversation.id === currentConversationId) {
            item.className += ' active';
        }
        
        const date = new Date(conversation.date);
        const formattedDate = date.toLocaleDateString('en-US', { 
            month: 'short', 
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
        
        item.innerHTML = `
            <div class="conversation-title">${conversation.title}</div>
            <div class="conversation-date">${formattedDate}</div>
            <button class="conversation-delete" title="Delete">×</button>
        `;
        
        item.addEventListener('click', () => {
            loadConversation(conversation.id);
            if (window.innerWidth <= 768) {
                leftSidebar.classList.remove('expanded');
            }
        });
        
        const deleteBtn = item.querySelector('.conversation-delete');
        deleteBtn.addEventListener('click', (e) => deleteConversation(conversation.id, e));
        
        conversationsList.appendChild(item);
    });
}

// Save message to current conversation
function saveMessageToConversation(text, role, metadata = {}) {
    const conversation = conversations.find(c => c.id === currentConversationId);
    if (!conversation) return;
    
    conversation.messages.push({ text, role, metadata });
    saveConversations();
}

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
    loadConversations();
    setupEventListeners();
    checkAPIHealth();
    autoResizeTextarea();
});

function setupEventListeners() {
    // Sidebar toggle
    leftSidebar.querySelector('.sidebar-header').addEventListener('click', () => {
        leftSidebar.classList.toggle('expanded');
    });
    
    // New conversation button
    newConversationBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        showLandingPage();
    });
    
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
        const files = Array.from(e.dataTransfer.files);
        if (files.length > 0) {
            handleMultipleFileUploads(files);
        }
    });
}

// ==========================================
// MESSAGE HANDLING
// ==========================================

async function handleSendMessage() {
    const message = userInput.value.trim();
    
    if (!message || isProcessing) return;
    
    // If on landing page, create new conversation with this message
    if (isLandingPage) {
        createNewConversation(message);
    }
    
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

function addMessage(text, sender, metadata = {}, shouldSave = true) {
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
    
    // Save message to conversation if shouldSave is true
    if (shouldSave && sender !== 'system') {
        saveMessageToConversation(text, sender, metadata);
    }
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
        
        // Show success toast notification
        if (successCount > 0) {
            const message = successCount === 1 
                ? `Successfully uploaded 1 file (${totalChunks} chunks created)` 
                : `Successfully uploaded ${successCount} files (${totalChunks} chunks created)`;
            showToast(message, 'success');
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
