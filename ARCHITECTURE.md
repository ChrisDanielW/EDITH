# EDITH Architecture

## System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                              EDITH                              │
│         (Even Disconnected, I'm The Helper)                     │
└─────────────────────────────────────────────────────────────────┘

┌─────────────┐      ┌──────────────┐      ┌─────────────────┐
│   User      │◄────►│   Main App   │◄────►│  RAG Service    │
│ Interface   │      │   (main.py)  │      │                 │
└─────────────┘      └──────────────┘      └─────────────────┘
                            │                       │
                            │                       │
                            ▼                       ▼
                    ┌──────────────┐      ┌─────────────────┐
                    │  Document    │      │  LLaMA Client   │
                    │  Loader      │      │  (Local Model)  │
                    └──────────────┘      └─────────────────┘
                            │                       │
                            ▼                       │
                    ┌──────────────┐               │
                    │  Text        │               │
                    │  Chunker     │               │
                    └──────────────┘               │
                            │                       │
                            ▼                       │
                    ┌──────────────┐               │
                    │  Embedding   │               │
                    │  Generator   │               │
                    └──────────────┘               │
                            │                       │
                            ▼                       ▼
                    ┌──────────────────────────────────┐
                    │      Pinecone Vector Store       │
                    │    (Cloud-based but offline-     │
                    │     accessible once cached)      │
                    └──────────────────────────────────┘
```

## Component Details

### 1. Document Loader (`utils/document_loader.py`)

**Purpose**: Load and extract text from various file formats

**Supported Formats**:
- PDF (using pypdf/pdfplumber)
- Word documents (using python-docx)
- Images (using Tesseract OCR)
- Plain text files

**Process**:
1. Detect file type
2. Route to appropriate parser
3. Extract text content
4. Return structured document with metadata

### 2. Text Chunker (`utils/text_chunker.py`)

**Purpose**: Split documents into manageable, semantic chunks

**Features**:
- Smart chunking (respects paragraphs, sections)
- Configurable chunk size and overlap
- Preserves context between chunks
- Maintains metadata throughout

**Why Chunking?**
- LLMs have token limits
- Smaller chunks = more precise retrieval
- Better context relevance
- Efficient storage and search

### 3. Embedding Generator (`utils/embeddings.py`)

**Purpose**: Convert text into vector embeddings

**Model**: sentence-transformers/all-MiniLM-L6-v2
- 384 dimensions
- Fast and efficient
- Good balance of speed/quality
- Runs locally

**Process**:
1. Receives text chunks
2. Generates embeddings in batches
3. Normalizes vectors for cosine similarity
4. Returns numerical representations

### 4. Vector Store (`services/vector_store.py`)

**Purpose**: Store and retrieve document embeddings

**Technology**: Pinecone
- Cloud-based vector database
- Fast similarity search
- Scalable storage
- Metadata filtering

**Operations**:
- **Upsert**: Store embeddings with metadata
- **Query**: Find similar vectors (k-NN search)
- **Delete**: Remove vectors
- **Stats**: Get index information

### 5. LLaMA Client (`models/llama_client.py`)

**Purpose**: Run LLaMA model locally for text generation

**Supported Backends**:
- **llama-cpp-python**: For GGUF quantized models (recommended)
- **transformers**: For full HuggingFace models

**Features**:
- GPU acceleration support
- Configurable parameters (temperature, max_tokens)
- Prompt formatting for LLaMA chat models
- Context-aware generation

### 6. RAG Service (`services/rag_service.py`)

**Purpose**: Orchestrate the Retrieval-Augmented Generation pipeline

**RAG Workflow**:

```
User Query
    │
    ├─► Generate Query Embedding
    │
    ├─► Search Vector Store (Top-K similar chunks)
    │
    ├─► Filter by Similarity Threshold
    │
    ├─► Prepare Context (combine chunks)
    │
    ├─► Create Prompt (system + context + query)
    │
    ├─► Generate Answer (LLaMA)
    │
    └─► Return Answer + Sources
```

**Key Methods**:
- `query()`: Answer questions using RAG
- `summarize_notes()`: Generate summaries
- `analyze_note()`: Extract structured information

## Data Flow

### Document Ingestion Flow

```
1. Load Documents
   └─► DocumentLoader reads files
        └─► Extracts text + metadata

2. Chunk Documents
   └─► TextChunker splits into segments
        └─► Adds chunk metadata

3. Generate Embeddings
   └─► EmbeddingGenerator creates vectors
        └─► Batch processing for efficiency

4. Store in Vector DB
   └─► VectorStore uploads to Pinecone
        └─► Associates metadata with vectors
```

### Query Flow

```
1. User asks question
   └─► "What is gradient descent?"

2. Convert to embedding
   └─► [0.234, -0.123, 0.456, ...]

3. Search vector store
   └─► Find 5 most similar chunks

4. Retrieve context
   └─► Combine relevant text chunks

5. Build prompt
   └─► System prompt + Context + Question

6. Generate answer
   └─► LLaMA processes prompt
        └─► Returns natural language answer

7. Return with sources
   └─► Answer + Source documents + Confidence
```

## Configuration

### Settings Hierarchy

```
Environment Variables (.env)
    │
    ├─► settings.py (Config class)
    │
    └─► Main App Components
         ├─► LLaMA Client
         ├─► Vector Store
         ├─► Embedding Generator
         └─► RAG Service
```

### Key Settings

- **Model Settings**: LLaMA path, GPU usage, parameters
- **Embedding Settings**: Model name, device
- **Vector DB Settings**: API key, index name, dimensions
- **Chunking Settings**: Size, overlap
- **RAG Settings**: Top-K, similarity threshold
- **Document Settings**: Supported formats, OCR

## Why This Architecture?

### 1. Modularity
- Each component has single responsibility
- Easy to swap implementations
- Independent testing

### 2. Scalability
- Batch processing for efficiency
- Vector DB handles large datasets
- Chunking enables processing large documents

### 3. Privacy
- LLaMA runs locally (no API calls)
- Complete offline operation after setup
- Data never leaves your machine (except Pinecone)

### 4. Flexibility
- Support multiple document formats
- Configurable parameters
- Different summary styles

### 5. Efficiency
- Vector search is fast (O(log n))
- Only relevant context sent to LLM
- Quantized models for speed

## Technical Decisions

### Why Pinecone?
- Fast k-NN search
- Managed service (no infrastructure)
- Good free tier
- Metadata filtering

**Alternatives**: FAISS (local), ChromaDB (local), Weaviate

### Why Sentence Transformers?
- Lightweight and fast
- Good semantic understanding
- Pre-trained models available
- Easy to use

### Why llama-cpp-python?
- GGUF quantization = smaller models
- Fast inference
- GPU acceleration
- Lower memory usage

### Why Smart Chunking?
- Better retrieval accuracy
- Preserves semantic meaning
- Respects document structure
- Maintains context

## Performance Considerations

### Memory Usage
- Embedding model: ~100MB
- LLaMA model: 4-13GB (depends on quantization)
- Vector DB: Cloud-based (minimal local)
- Document processing: Depends on batch size

### Speed
- Document ingestion: ~1-5 docs/second
- Query processing: 1-3 seconds
- Summary generation: 5-15 seconds
- Embedding generation: ~100 texts/second

### Optimization Tips
1. Use quantized models (Q4_K_M or Q5_K_M)
2. Enable GPU acceleration
3. Increase batch size (if enough memory)
4. Reduce chunk size for faster retrieval
5. Use appropriate top-K value

## Future Enhancements

### Potential Additions
1. **Multi-modal support**: Images, tables, charts
2. **Conversation memory**: Maintain chat history
3. **Fine-tuning**: Adapt model to your notes
4. **Web UI**: Streamlit or Gradio interface
5. **Mobile app**: iOS/Android clients
6. **Collaboration**: Share knowledge bases
7. **Advanced analytics**: Note insights, trends
8. **Export features**: PDF reports, presentations

### Improvements
1. Better chunking strategies
2. Hybrid search (vector + keyword)
3. Re-ranking retrieved results
4. Query understanding and expansion
5. Automatic metadata extraction
6. Document version tracking
