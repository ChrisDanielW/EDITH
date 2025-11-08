# EDITH Setup Guide

## Prerequisites

1. **Python 3.8+** installed on your system
2. **CUDA-capable GPU** (optional but recommended for better performance)
3. **Tesseract OCR** (optional, for image text extraction)

## Installation Steps

### 1. Install Python Dependencies

```powershell
# Navigate to the project directory
cd "c:\KJC\MCA\Year 2\Sem 3\Diligent\Just A Rather Very Intelligent System\EDITH\notes-assistant"

# Install dependencies
pip install -r requirements.txt
```

### 2. Install LLaMA Model Support

Choose one of the following options:

**Option A: GGUF Models (Recommended for local use)**
```powershell
pip install llama-cpp-python
```

For GPU support on Windows with CUDA:
```powershell
$env:CMAKE_ARGS="-DLLAMA_CUBLAS=on"
pip install llama-cpp-python --force-reinstall --no-cache-dir
```

**Option B: HuggingFace Transformers**
```powershell
pip install transformers accelerate bitsandbytes
```

### 3. Install OCR Support (Optional)

For processing images and scanned documents:

```powershell
# Install Python library
pip install pytesseract

# Download and install Tesseract OCR
# Visit: https://github.com/UB-Mannheim/tesseract/wiki
# After installation, add Tesseract to your PATH
```

### 4. Download LLaMA Model

**Option A: GGUF Models (Recommended)**

Download a quantized LLaMA model from HuggingFace:

1. Visit: https://huggingface.co/TheBloke
2. Search for LLaMA models (e.g., "Llama-2-7B-Chat-GGUF")
3. Download a `.gguf` file (Q4_K_M or Q5_K_M recommended for balance)
4. Place it in the `models` directory

Example:
```powershell
# Create models directory
mkdir models

# Download using Git LFS or directly from HuggingFace
# Place the .gguf file in the models folder
```

**Option B: Full HuggingFace Models**

```python
from transformers import AutoModelForCausalLM, AutoTokenizer

model_name = "meta-llama/Llama-2-7b-chat-hf"
model = AutoModelForCausalLM.from_pretrained(model_name)
tokenizer = AutoTokenizer.from_pretrained(model_name)

# Save locally
model.save_pretrained("./models/llama-2-7b-chat")
tokenizer.save_pretrained("./models/llama-2-7b-chat")
```

### 5. Set Up Pinecone

1. Create account at https://www.pinecone.io/
2. Create a new index:
   - Name: `edith-notes`
   - Dimensions: `384` (for all-MiniLM-L6-v2)
   - Metric: `cosine`
3. Get your API key from the dashboard

### 6. Configure Environment Variables

```powershell
# Copy the example env file
cp .env.example .env

# Edit .env with your values
notepad .env
```

Update the following in your `.env` file:
- `PINECONE_API_KEY`: Your Pinecone API key
- `LLAMA_MODEL_PATH`: Path to your LLaMA model
- `NOTES_DIRECTORY`: Path to your notes folder
- Other settings as needed

### 7. Prepare Your Notes

Place your documents in the notes directory:

```powershell
# Create the notes directory
mkdir "src\data\notes"

# Copy your documents there
# Supported formats: .pdf, .docx, .txt, .md, .png, .jpg, etc.
```

## Usage

### 1. Ingest Your Documents

First-time setup - load your documents into the vector database:

```powershell
python src/main.py --ingest
```

### 2. Query Your Notes

Ask questions about your notes:

```powershell
python src/main.py --query "What are the main topics in my machine learning notes?"
```

### 3. Generate Summaries

```powershell
python src/main.py --summary
```

### 4. Interactive Mode

Chat with EDITH interactively:

```powershell
python src/main.py --interactive
```

Or simply:

```powershell
python src/main.py
```

## Troubleshooting

### GPU Not Detected

```powershell
# Check if CUDA is available
python -c "import torch; print(torch.cuda.is_available())"
```

If False, either:
- Install PyTorch with CUDA support
- Set `USE_GPU=false` in `.env`

### Out of Memory Errors

1. Reduce `CHUNK_SIZE` in `.env`
2. Reduce `BATCH_SIZE` in `.env`
3. Use a smaller/quantized model
4. Set `USE_GPU=false` to use CPU

### Pinecone Connection Issues

1. Verify API key is correct
2. Check index name matches
3. Ensure dimension matches embedding model (384 for MiniLM)

### OCR Not Working

1. Ensure Tesseract is installed
2. Add Tesseract to PATH
3. Set `USE_OCR=false` if not needed

## Performance Tips

1. **Use GPU**: Dramatically faster for embeddings and inference
2. **Quantized Models**: Use Q4_K_M or Q5_K_M GGUF models for speed
3. **Batch Processing**: Increase `BATCH_SIZE` if you have enough memory
4. **Chunk Size**: Smaller chunks = better retrieval but more storage

## Project Structure

```
notes-assistant/
├── src/
│   ├── main.py                 # Main application entry point
│   ├── config/
│   │   └── settings.py         # Configuration management
│   ├── models/
│   │   └── llama_client.py     # LLaMA model interface
│   ├── services/
│   │   ├── vector_store.py     # Pinecone vector database
│   │   ├── rag_service.py      # RAG pipeline orchestration
│   │   ├── note_analyzer.py    # Note analysis logic
│   │   └── summarizer.py       # Summarization logic
│   ├── utils/
│   │   ├── document_loader.py  # Multi-format document loading
│   │   ├── text_chunker.py     # Smart text chunking
│   │   ├── embeddings.py       # Embedding generation
│   │   └── text_processor.py   # Text preprocessing
│   └── data/
│       └── notes/              # Your notes go here
├── models/                      # LLaMA model files
├── tests/                       # Unit tests
├── .env                         # Your configuration (create from .env.example)
├── requirements.txt
└── README.md
```

## Next Steps

1. Add more documents to improve EDITH's knowledge
2. Experiment with different summary styles
3. Try different chunk sizes for your use case
4. Fine-tune RAG parameters (top_k, similarity_threshold)

## Support

For issues and questions:
- Check the logs in the console
- Ensure all dependencies are installed
- Verify environment variables are set correctly
