# Using EDITH with Ollama and LLaMA 3.1

## Overview

EDITH now supports **Ollama** as a backend for running LLaMA models! This makes it even easier to use EDITH with LLaMA 3.1 without managing GGUF files directly.

## Prerequisites

### 1. Install Ollama

**Windows:**
```powershell
# Download and install from: https://ollama.ai/download
# Or using winget:
winget install Ollama.Ollama
```

**Verify Installation:**
```powershell
ollama --version
```

### 2. Pull LLaMA 3.1 Model

```powershell
# Pull the LLaMA 3.1 8B Instruct model with Q4_K_M quantization
ollama pull llama3.1:8b-instruct-q4_K_M

# Or try other variants:
# ollama pull llama3.1:8b          # Default quantization
# ollama pull llama3.1:70b         # Larger model (if you have VRAM)
```

**Check Available Models:**
```powershell
ollama list
```

## Configuration

### Your .env File

Your current configuration is already set up for Ollama:

```bash
# ========== LLaMA Model Settings ==========
LLAMA_MODEL_PATH=llama3.1:8b-instruct-q4_K_M
LLAMA_MODEL_TYPE=gguf
USE_GPU=true
MAX_TOKENS=4096
TEMPERATURE=0.7
```

**Note:** EDITH auto-detects Ollama format (models with `:` in the name) and will automatically use the Ollama backend!

## Usage

### 1. Start Ollama (if not running)

```powershell
# Ollama usually runs as a service, but you can start it manually:
ollama serve
```

### 2. Run EDITH

```powershell
# Activate your virtual environment (if using one)
.\venv\Scripts\activate

# Run EDITH
python src/main.py --interactive
```

## Testing Your Setup

### Quick Test

```powershell
# Test Ollama directly
ollama run llama3.1:8b-instruct-q4_K_M "Hello, how are you?"

# If that works, EDITH should work too!
```

### Test with EDITH

```python
# test_ollama.py
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from models.llama_client import LlamaClient

# Initialize client
client = LlamaClient(
    model_path="llama3.1:8b-instruct-q4_K_M",
    model_type="gguf",  # Will auto-detect as Ollama
    use_gpu=True,
    max_tokens=100
)

# Test generation
response = client.chat("What is the capital of France?")
print(f"Response: {response}")
```

## LLaMA 3.1 Prompt Format

EDITH automatically uses the correct prompt format for LLaMA 3.1:

```
<|begin_of_text|><|start_header_id|>system<|end_header_id|>

You are EDITH, a helpful AI assistant...
<|eot_id|><|start_header_id|>user<|end_header_id|>

What is machine learning?
<|eot_id|><|start_header_id|>assistant<|end_header_id|>

```

This is handled automatically - no need to format prompts yourself!

## Performance

### LLaMA 3.1 8B Q4_K_M

| Hardware | Speed | Memory |
|----------|-------|--------|
| RTX 3060 (12GB) | ~30 tokens/s | ~6GB VRAM |
| RTX 4070 (12GB) | ~50 tokens/s | ~6GB VRAM |
| RTX 4090 (24GB) | ~80 tokens/s | ~6GB VRAM |
| CPU (16 cores) | ~5 tokens/s | ~8GB RAM |

### Tips for Better Performance

1. **GPU Acceleration**: Ensure `USE_GPU=true` in `.env`
2. **Batch Size**: Reduce if running out of memory
3. **Context Length**: LLaMA 3.1 supports up to 128K tokens, but start with 4096
4. **Quantization**: Q4_K_M is a good balance; Q5_K_M for better quality

## Troubleshooting

### Issue: "Could not connect to Ollama"

**Solution:**
```powershell
# Check if Ollama is running
ollama list

# If not, start it:
ollama serve

# Or restart the service:
# Windows: Restart "Ollama" service in Services
```

### Issue: "Model not found"

**Solution:**
```powershell
# Pull the model
ollama pull llama3.1:8b-instruct-q4_K_M

# Check it's available
ollama list
```

### Issue: Slow generation

**Solutions:**
1. Ensure GPU is being used: `USE_GPU=true`
2. Close other GPU-intensive applications
3. Use a smaller model: `ollama pull llama3.1:8b` (smaller quantization)
4. Reduce `MAX_TOKENS` in `.env`

### Issue: Out of memory

**Solutions:**
1. Use CPU: `USE_GPU=false`
2. Reduce batch size: `BATCH_SIZE=5`
3. Reduce chunk size: `CHUNK_SIZE=500`
4. Close other applications

## Alternative: Direct GGUF Files

If you prefer using GGUF files directly (without Ollama):

### 1. Download GGUF Model

Visit: https://huggingface.co/bartowski/Meta-Llama-3.1-8B-Instruct-GGUF

Download: `Meta-Llama-3.1-8B-Instruct-Q4_K_M.gguf`

### 2. Update .env

```bash
LLAMA_MODEL_PATH=./models/Meta-Llama-3.1-8B-Instruct-Q4_K_M.gguf
LLAMA_MODEL_TYPE=gguf
```

### 3. Install llama-cpp-python

```powershell
# CPU only
pip install llama-cpp-python

# With GPU support (CUDA)
$env:CMAKE_ARGS="-DLLAMA_CUBLAS=on"
pip install llama-cpp-python --force-reinstall --no-cache-dir
```

## Comparison: Ollama vs Direct GGUF

| Feature | Ollama | Direct GGUF |
|---------|--------|-------------|
| **Setup** | Very easy | Moderate |
| **Model Management** | Built-in | Manual |
| **Performance** | Excellent | Excellent |
| **GPU Support** | Automatic | Requires setup |
| **Model Updates** | `ollama pull` | Manual download |
| **Multi-model** | Easy switch | Need multiple files |
| **Recommended** | ✅ Yes | For advanced users |

## Using Different LLaMA 3.1 Variants

### Smaller/Faster

```bash
LLAMA_MODEL_PATH=llama3.1:8b  # Less quantization, faster
```

### Better Quality

```bash
LLAMA_MODEL_PATH=llama3.1:8b-instruct-q5_K_M  # More precise
```

### Larger Model (if you have VRAM)

```bash
LLAMA_MODEL_PATH=llama3.1:70b-instruct-q4_K_M  # Much better, needs ~40GB VRAM
```

## Complete Workflow Example

```powershell
# 1. Install Ollama
winget install Ollama.Ollama

# 2. Pull model
ollama pull llama3.1:8b-instruct-q4_K_M

# 3. Setup EDITH
cd "c:\KJC\MCA\Year 2\Sem 3\Diligent\Just A Rather Very Intelligent System\EDITH\notes-assistant"
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt

# 4. Configure (your .env is already set!)
# Just add your Pinecone API key

# 5. Add some notes
# Copy files to: src\data\notes\

# 6. Ingest documents
python src/main.py --ingest

# 7. Start chatting!
python src/main.py --interactive
```

## Expected Output

```
============================================================
Initializing EDITH - Even Disconnected, I'm The Helper
============================================================
Loading embedding model...
Connecting to Pinecone vector store...
Loading LLaMA model (this may take a while)...
Initializing LLaMA client with ollama backend
Model: llama3.1:8b-instruct-q4_K_M
GPU available: True, Using GPU: True
Detected Ollama model format
Connected to Ollama
Model llama3.1:8b-instruct-q4_K_M is available in Ollama
Model loaded successfully
Setting up RAG service...
✓ All components initialized successfully!

============================================================
EDITH Interactive Mode
Commands: 'quit' to exit, 'summary' for note summary
============================================================

You: _
```

## Benefits of LLaMA 3.1

1. **Larger Context**: 128K tokens (vs 4K in LLaMA 2)
2. **Better Quality**: Improved instruction following
3. **Faster**: Optimized architecture
4. **More Accurate**: Better training data
5. **Multilingual**: Better support for multiple languages

## Next Steps

1. ✅ Set up Ollama and pull model
2. ✅ Configure EDITH
3. ✅ Add your notes to `src/data/notes/`
4. ✅ Run document ingestion
5. ✅ Start asking questions!

Enjoy using EDITH with LLaMA 3.1! 🚀
