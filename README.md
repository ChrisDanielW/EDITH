# EDITH - Even Disconnected, I'm The Helper

## Overview
EDITH is a personal AI assistant that analyzes your notes and generates comprehensive summaries for quick reference. The application runs completely locally using LLaMA 3.1, ensuring privacy and functionality even without an internet connection. It uses Retrieval-Augmented Generation (RAG) with Pinecone vector databases to efficiently process and retrieve information from various types of unstructured data.

## ✨ New: Ollama Support!
EDITH now supports **Ollama** for easy LLaMA 3.1 model management! See [OLLAMA_SETUP.md](OLLAMA_SETUP.md) for details.

## Features
- **Multi-Format Support**: Processes PDFs, Word documents, images (OCR), text files, and more
- **Local LLM**: Uses LLaMA 3.1 (8B/70B) running locally via Ollama or direct GGUF
- **RAG Architecture**: Leverages vector databases for intelligent information retrieval
- **Note Analysis**: Extracts key information from notes using advanced NLP
- **Smart Summarization**: Generates concise, context-aware summaries
- **Vector Storage**: Utilizes Pinecone for efficient storage and retrieval of note embeddings
- **OCR Support**: Extracts text from images and scanned documents
- **Multiple Backends**: Supports Ollama, llama-cpp-python, and HuggingFace transformers

## Project Structure
```
notes-assistant
├── src
│   ├── main.py               # Entry point of the application
│   ├── config
│   │   └── settings.py       # Configuration settings
│   ├── models
│   │   └── llama_client.py    # LLaMA model interactions
│   ├── services
│   │   ├── note_analyzer.py   # Note analysis functionality
│   │   ├── summarizer.py       # Summarization functionality
│   │   └── vector_store.py     # Vector database interactions
│   ├── utils
│   │   ├── text_processor.py    # Text processing utilities
│   │   └── embeddings.py        # Embedding generation functions
│   └── data
│       └── notes              # Directory for notes data files
├── tests
│   ├── test_analyzer.py       # Unit tests for NoteAnalyzer
│   └── test_summarizer.py     # Unit tests for Summarizer
├── requirements.txt           # Project dependencies
├── .env.example               # Example environment variables
└── README.md                  # Project documentation
```

## Quick Start

### 1. Installation

```powershell
# Install dependencies
pip install -r requirements.txt

# Option 1: Use Ollama (Recommended - Easiest!)
# Install Ollama from: https://ollama.ai/download
ollama pull llama3.1:8b-instruct-q4_K_M

# Option 2: Use GGUF files directly
pip install llama-cpp-python  # For GGUF models

# Option 3: Use HuggingFace transformers
pip install transformers accelerate
```

### 2. Configuration

```powershell
# Copy and edit environment file
cp .env.example .env
notepad .env
```

Set your Pinecone API key in `.env`. The model path is pre-configured for Ollama!

### 3. Get LLaMA 3.1 Model

**Using Ollama (Recommended):**
```powershell
ollama pull llama3.1:8b-instruct-q4_K_M
```

**Or download GGUF:** Get from [HuggingFace](https://huggingface.co/bartowski/Meta-Llama-3.1-8B-Instruct-GGUF)

See [OLLAMA_SETUP.md](OLLAMA_SETUP.md) for detailed instructions.

### 4. Ingest Your Notes

```powershell
# Place your documents in src/data/notes/
# Then run:
python src/main.py --ingest
```

### 5. Start Using EDITH

```powershell
# Interactive mode
python src/main.py

# Query mode
python src/main.py --query "What are my notes about machine learning?"

# Summary mode
python src/main.py --summary
```

## Detailed Documentation

See [SETUP.md](SETUP.md) for detailed installation and configuration instructions.

## Architecture

EDITH uses a RAG (Retrieval-Augmented Generation) architecture:

1. **Document Ingestion**: Loads and processes documents (PDF, DOCX, images, etc.)
2. **Text Chunking**: Splits documents into semantic chunks
3. **Embedding Generation**: Creates vector embeddings using sentence-transformers
4. **Vector Storage**: Stores embeddings in Pinecone for fast retrieval
5. **Query Processing**: Converts questions to embeddings and retrieves relevant chunks
6. **Answer Generation**: Uses LLaMA to generate answers based on retrieved context

## Technology Stack

- **LangChain**: Framework for LLM applications
- **Pinecone**: Vector database for embeddings
- **LLaMA**: Local language model (via llama-cpp-python or transformers)
- **Sentence Transformers**: Embedding generation
- **PyPDF/python-docx/Tesseract**: Document processing

## Usage Examples

### Interactive Chat

```powershell
python src/main.py --interactive
```

```
You: What are the main topics in my notes?
EDITH: Based on your notes, the main topics are...

You: Summarize my machine learning notes
EDITH: Here's a summary of your machine learning notes...

You: quit
```

### Command Line Queries

```powershell
# Ask a question
python src/main.py --query "What is gradient descent?"

# Generate summary
python src/main.py --summary

# Ingest new documents
python src/main.py --ingest --notes-dir "path/to/new/notes"
```

## Supported Document Formats

- **Text**: `.txt`, `.md`, `.markdown`
- **PDF**: `.pdf`
- **Word**: `.docx`, `.doc`
- **Images**: `.png`, `.jpg`, `.jpeg` (requires OCR)

## Contributing
Contributions are welcome! Please submit a pull request or open an issue for any enhancements or bug fixes.

## License
This project is licensed under the MIT License. See the LICENSE file for more details.