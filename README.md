# EDITH - Even Disconnected, I'm The Helper 👓

<div align="center">

**A modern, AI study assistant that runs completely offline**

*Smart conversation management • Context-aware responses • Minimalist web UI*

![EDITH Landing Page](images/Screenshot%202025-11-09%20222627.png)

</div>

---

## 🌟 What is EDITH?

EDITH is your personal AI study assistant that helps you make sense of your notes using local LLMs. She features a modern interface with conversation management, intelligent query classification, and context-aware responses. Best of all? She runs **completely offline** using LLaMA 3.1.

![EDITH Chat Interface](images/Screenshot%202025-11-09%20223010.png)

### Key Features

✨ **Modern Web Interface**
- Modern landing page with welcoming design
- Conversation management (create, save, switch, delete)
- Clean, animated UI with expandable sidebar
- Real-time typing indicators and status updates

🧠 **Intelligent AI Assistant**
- Context-aware responses that reference previous messages
- Automatic classification between knowledge queries and casual chat
- RAG (Retrieval-Augmented Generation) for note-based answers
- Conversational mode for general questions

📚 **Powerful Note Processing**
- Multi-format support (PDF, DOCX, images with OCR, text files)
- Drag-and-drop or multi-file upload
- Automatic text chunking and embedding generation
- Vector database storage with Pinecone for fast retrieval

🔒 **Privacy First**
- 100% local LLM execution via Ollama
- No data sent to external servers
- Your notes stay on your machine

---

## 🚀 Quick Start

### 1. Install Ollama & Pull Model

```powershell
# Download Ollama from: https://ollama.ai/download
# Then pull LLaMA 3.1:
ollama pull llama3.1:8b-instruct-q4_K_M
```

### 2. Install Dependencies

```powershell
# Clone the repository
git clone https://github.com/ChrisDanielW/EDITH.git
cd EDITH

# Install Python dependencies
pip install -r requirements.txt
```

### 3. Configure Pinecone

```powershell
# Copy environment file
cp .env.example .env

# Edit .env and add your Pinecone API key
notepad .env
```

Get a free Pinecone API key at [pinecone.io](https://www.pinecone.io/)

### 4. Start EDITH

```powershell
# Start the web UI and API server
python start_ui.py
```

Open your browser to **http://localhost:5000** and start chatting!

---

## 📖 User Guide

### First Time Setup

1. **Upload Your Notes**
   - Click the 📎 Upload button in the sidebar
   - Select or drag-and-drop your documents (PDF, DOCX, TXT, images)
   - EDITH will process and index them automatically

![Upload Interface](images/Screenshot%202025-11-09%20223330.png)

2. **Start a Conversation**
   - Type your first message on the landing page
   - A new numbered conversation will be created automatically
   - Ask questions about your notes or just chat casually

### Using EDITH

**Asking About Notes:**
```
You: What is polymorphism in OOP?
EDITH: [Searches your notes and provides detailed explanation]
```

**Casual Conversation:**
```
You: Hey, how's it going?
EDITH: [Responds naturally without searching notes]
```

**Follow-up Questions:**
```
You: Can you explain that in more detail?
EDITH: [References previous conversation context]
```

![Conversation with Context](images/Screenshot%202025-11-09%20223314.png)

### Managing Conversations

- **New Conversation**: Click the ➕ button (appears when in a conversation)
- **Switch Conversations**: Click any conversation in the left sidebar
- **Delete Conversation**: Click the × button on any conversation
- **Return to Landing**: Click the hamburger menu (☰) to collapse sidebar

---

## 🏗️ Architecture

### Tech Stack

**Frontend:**
- Vanilla HTML, CSS, JavaScript
- LocalStorage for conversation persistence
- Modern animated UI with responsive design

**Backend:**
- Flask REST API
- Python 3.8+
- Ollama for LLM execution

**AI/ML:**
- LLaMA 3.1 (8B Instruct, 4-bit quantized)
- Sentence Transformers for embeddings
- Pinecone vector database
- RAG architecture for context retrieval

### How It Works

1. **Document Upload** → Text extraction & chunking → Embedding generation → Store in Pinecone
2. **User Query** → Classify (knowledge vs. casual) → Retrieve relevant chunks (if knowledge) → Generate answer with conversation context
3. **Conversation History** → Last 3 exchanges sent with each query → Context-aware responses

---

## 📁 Project Structure

```
EDITH/
├── ui/                          # Web interface
│   ├── index.html              # Main HTML
│   ├── styles.css              # Styling
│   └── app.js                  # Frontend logic
├── src/
│   ├── main.py                 # Core EDITH class
│   ├── api/
│   │   └── app.py              # Flask API server
│   ├── models/
│   │   └── llama_client.py     # LLM interface
│   ├── services/
│   │   ├── rag_service.py      # RAG pipeline
│   │   ├── vector_store.py     # Pinecone integration
│   │   ├── note_analyzer.py    # Document analysis
│   │   └── summarizer.py       # Summarization
│   ├── utils/
│   │   ├── document_loader.py  # File loading
│   │   ├── text_chunker.py     # Smart chunking
│   │   ├── embeddings.py       # Embedding generation
│   │   └── query_classifier.py # Query classification
│   └── config/
│       └── settings.py         # Configuration
├── start_ui.py                 # Launch script
├── requirements.txt            # Python dependencies
└── README.md                   # This file
```

---

## ⚙️ Configuration

### Token Limits (Adjustable in `src/main.py`)

- **RAG Mode**: 500 tokens (detailed educational responses)
- **Conversational Mode**: 350 tokens (natural chat)
- **Fallback Mode**: 400 tokens (general knowledge)

### Model Selection

Edit `src/config/settings.py` to change models:

```python
# Current default
MODEL_NAME = "llama3.1:8b-instruct-q4_K_M"

# For more powerful responses (slower, needs more RAM)
MODEL_NAME = "llama3.1:70b-instruct-q4_K_M"
```

### Vector Database

EDITH uses Pinecone with these settings:
- **Top K**: 3 most relevant chunks
- **Similarity Threshold**: 0.7
- **Max Context**: 2000 characters

---

## 🎨 Features Deep Dive

### Conversation Management
- Persistent storage in browser localStorage
- Numbered conversations (1, 2, 3...)
- Auto-save after every message
- Landing page shows on startup

### Intelligent Query Routing
- Automatic classification of user intent
- Knowledge queries → RAG mode (searches notes)
- Casual queries → Conversational mode (direct chat)
- Hybrid queries → RAG with conversational tone

### Context Awareness
- Sends last 6 messages (3 exchanges) with each query
- References previous conversation naturally
- Maintains conversation flow across messages

---

## 🤝 Contributing

Contributions are welcome! Areas for improvement:

- [ ] Export conversations to PDF/text
- [ ] Search within conversations
- [ ] Custom system prompts per conversation
- [ ] Markdown rendering in responses
- [ ] Code syntax highlighting
- [ ] Voice input/output

---

## 📄 License

MIT License - See [LICENSE](LICENSE) for details

---

## 🙏 Acknowledgments

- **LLaMA 3.1** by Meta AI
- **Ollama** for easy local LLM deployment
- **Pinecone** for vector database
- **Sentence Transformers** for embeddings

---

<div align="center">

Made with ❤️ for students who want to study smarter

**[Report Bug](https://github.com/ChrisDanielW/EDITH/issues)** • **[Request Feature](https://github.com/ChrisDanielW/EDITH/issues)**

</div>