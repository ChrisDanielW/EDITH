# EDITH Quick Reference

## Installation (Quick)

```powershell
# 1. Install dependencies
pip install -r requirements.txt
pip install llama-cpp-python

# 2. Configure
cp .env.example .env
# Edit .env with your Pinecone API key

# 3. Download model (place in models/ folder)
# Get from: https://huggingface.co/TheBloke

# 4. Ingest documents
python src/main.py --ingest

# 5. Start chatting
python src/main.py
```

## Command Reference

### Basic Commands

```powershell
# Interactive mode (default)
python src/main.py
python src/main.py --interactive

# Ingest documents
python src/main.py --ingest
python src/main.py --ingest --notes-dir "path/to/notes"

# Query
python src/main.py --query "your question here"

# Summary
python src/main.py --summary
```

### Interactive Mode Commands

```
You: <your question>          # Ask anything
You: summary                   # Generate summary
You: quit                      # Exit (or 'exit', 'q')
```

## Configuration Quick Tips

### .env File (Essential Settings)

```bash
# Required
PINECONE_API_KEY=your_key_here
LLAMA_MODEL_PATH=./models/your-model.gguf

# Performance
USE_GPU=true                   # Use GPU if available
BATCH_SIZE=10                  # Process 10 at a time
CHUNK_SIZE=1000               # Characters per chunk

# Quality
TOP_K_RESULTS=5               # Retrieve 5 chunks
SIMILARITY_THRESHOLD=0.7      # Min relevance score
```

## Troubleshooting Quick Fixes

### Problem: GPU not working
```bash
# In .env
USE_GPU=false
EMBEDDING_DEVICE=cpu
```

### Problem: Out of memory
```bash
# In .env
BATCH_SIZE=5
CHUNK_SIZE=500
```

### Problem: Slow performance
- Use smaller/quantized model (Q4_K_M)
- Enable GPU
- Reduce MAX_TOKENS

### Problem: Poor answers
- Increase TOP_K_RESULTS (try 10)
- Decrease SIMILARITY_THRESHOLD (try 0.5)
- Ingest more documents
- Use larger chunks (CHUNK_SIZE=2000)

## Document Format Support

| Format | Extension | Requirements |
|--------|-----------|--------------|
| PDF | .pdf | pypdf, pdfplumber |
| Word | .docx, .doc | python-docx |
| Text | .txt, .md | None |
| Images | .png, .jpg | tesseract (OCR) |

## API Quick Reference

### Using EDITH Programmatically

```python
from src.main import EDITH

# Initialize
edith = EDITH()

# Ingest documents
edith.ingest_documents("path/to/notes")

# Query
result = edith.query("What is machine learning?")
print(result['answer'])
print(result['sources'])

# Summary
summary = edith.summarize(style="comprehensive")
print(summary)
```

## Performance Metrics

### Expected Performance

| Operation | Time | Notes |
|-----------|------|-------|
| Initialization | 10-30s | First time only |
| Document ingestion | 1-5 docs/s | Depends on size |
| Query | 1-3s | With GPU |
| Summary | 5-15s | Depends on length |

### Resource Usage

| Component | Memory | Disk |
|-----------|--------|------|
| Embedding model | ~100MB | ~100MB |
| LLaMA (Q4) | ~4GB | ~4GB |
| LLaMA (Q5) | ~6GB | ~6GB |
| Vector DB | Minimal | Cloud |

## Common Use Cases

### 1. Study Notes Review
```powershell
# Ingest lecture notes
python src/main.py --ingest --notes-dir "lectures/"

# Ask questions
python src/main.py --query "Explain the main concepts from week 3"
```

### 2. Research Paper Analysis
```powershell
# Ingest papers
python src/main.py --ingest --notes-dir "papers/"

# Get summary
python src/main.py --summary
```

### 3. Meeting Notes
```powershell
# Ingest meeting docs
python src/main.py --ingest --notes-dir "meetings/"

# Find action items
python src/main.py --query "What are the action items?"
```

## Best Practices

### 📁 Document Organization
- Use clear filenames
- Group related documents
- Keep original formatting
- Regular updates

### ⚙️ Configuration
- Start with defaults
- Adjust based on results
- Monitor performance
- Test different settings

### 🔍 Querying
- Be specific in questions
- Use natural language
- Try different phrasings
- Check sources

### 📊 Quality
- More documents = better answers
- Update regularly
- Remove outdated info
- Review summaries

## Keyboard Shortcuts (Interactive Mode)

| Key | Action |
|-----|--------|
| Enter | Send message |
| Ctrl+C | Exit |
| Ctrl+D | Exit (Unix) |

## File Locations

```
notes-assistant/
├── src/data/notes/          # Put your documents here
├── models/                   # Put LLaMA model here
├── .env                      # Configuration file
├── src/main.py              # Main application
└── logs/                     # Application logs (if enabled)
```

## Getting Help

### Check Logs
```powershell
# Logs appear in console by default
# Check for error messages

# For more verbose logs, in .env:
LOG_LEVEL=DEBUG
```

### Common Error Messages

| Error | Cause | Solution |
|-------|-------|----------|
| "Pinecone API key required" | Missing config | Set PINECONE_API_KEY in .env |
| "Model not found" | Wrong path | Check LLAMA_MODEL_PATH |
| "Out of memory" | Too large batch | Reduce BATCH_SIZE |
| "No documents found" | Empty folder | Add files to notes dir |

## Resources

- **Documentation**: See SETUP.md, ARCHITECTURE.md
- **Examples**: Run example.py
- **Models**: https://huggingface.co/TheBloke
- **Pinecone**: https://www.pinecone.io/

## Quick Tips

💡 **Tip 1**: Start with a small set of documents to test
💡 **Tip 2**: Use Q4_K_M quantized models for best speed/quality balance
💡 **Tip 3**: Enable GPU for 5-10x faster processing
💡 **Tip 4**: Adjust chunk size based on your document types
💡 **Tip 5**: Check sources to verify answer quality
