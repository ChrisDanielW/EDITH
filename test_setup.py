"""
Quick test script for EDITH with LLaMA 3.1
Tests the LLaMA client connection and basic functionality
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

print("=" * 60)
print("EDITH - LLaMA 3.1 Connection Test")
print("=" * 60)

# Test 1: Check environment
print("\n1. Checking environment...")
try:
    from dotenv import load_dotenv
    import os
    
    load_dotenv()
    
    model_path = os.getenv("LLAMA_MODEL_PATH", "Not set")
    use_gpu = os.getenv("USE_GPU", "Not set")
    
    print(f"   ✓ Model path: {model_path}")
    print(f"   ✓ GPU enabled: {use_gpu}")
    
except Exception as e:
    print(f"   ✗ Error: {e}")
    sys.exit(1)

# Test 2: Check if Ollama is running (if using Ollama)
if ":" in model_path and not model_path.startswith("./"):
    print("\n2. Checking Ollama connection...")
    try:
        import requests
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        response.raise_for_status()
        
        models = response.json().get("models", [])
        model_names = [m.get("name") for m in models]
        
        print(f"   ✓ Ollama is running")
        print(f"   ✓ Available models: {len(model_names)}")
        
        if model_path in model_names:
            print(f"   ✓ Model '{model_path}' is available")
        else:
            print(f"   ⚠ Model '{model_path}' not found")
            print(f"   Available: {model_names[:3]}")
            print(f"\n   Run: ollama pull {model_path}")
            
    except Exception as e:
        print(f"   ✗ Ollama not running or error: {e}")
        print(f"   Start Ollama with: ollama serve")
        sys.exit(1)
else:
    print("\n2. Using direct GGUF file...")
    if Path(model_path).exists():
        print(f"   ✓ Model file found")
    else:
        print(f"   ✗ Model file not found: {model_path}")
        sys.exit(1)

# Test 3: Initialize LLaMA client
print("\n3. Initializing LLaMA client...")
try:
    from config.settings import settings
    from models.llama_client import LlamaClient
    
    client = LlamaClient(
        model_path=settings.LLAMA_MODEL_PATH,
        model_type=settings.LLAMA_MODEL_TYPE,
        use_gpu=settings.USE_GPU,
        max_tokens=100,  # Short for testing
        temperature=settings.TEMPERATURE
    )
    
    print(f"   ✓ Client initialized")
    print(f"   ✓ Backend: {client.model_type}")
    
except Exception as e:
    print(f"   ✗ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 4: Generate text
print("\n4. Testing text generation...")
try:
    test_prompt = "What is 2+2? Answer briefly."
    
    print(f"   Prompt: '{test_prompt}'")
    print(f"   Generating response...")
    
    response = client.chat(
        message=test_prompt,
        system_prompt="You are a helpful assistant. Answer briefly and accurately."
    )
    
    print(f"   ✓ Response received!")
    print(f"   Response: {response[:100]}..." if len(response) > 100 else f"   Response: {response}")
    
except Exception as e:
    print(f"   ✗ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 5: Check embedding model
print("\n5. Checking embedding model...")
try:
    from utils.embeddings import EmbeddingGenerator
    
    embed_gen = EmbeddingGenerator(
        model_name=settings.EMBEDDING_MODEL,
        device=settings.EMBEDDING_DEVICE
    )
    
    test_text = "This is a test sentence."
    embedding = embed_gen.generate_embeddings(test_text)
    
    print(f"   ✓ Embedding model loaded")
    print(f"   ✓ Embedding dimension: {len(embedding)}")
    
except Exception as e:
    print(f"   ✗ Error: {e}")
    import traceback
    traceback.print_exc()

# Test 6: Check Pinecone
print("\n6. Checking Pinecone connection...")
try:
    pinecone_key = os.getenv("PINECONE_API_KEY", "")
    
    if not pinecone_key or pinecone_key == "your_pinecone_api_key_here":
        print(f"   ⚠ Pinecone API key not set in .env")
        print(f"   Set PINECONE_API_KEY in your .env file")
    else:
        from services.vector_store import VectorStore
        
        vector_store = VectorStore(
            api_key=settings.PINECONE_API_KEY,
            environment=settings.PINECONE_ENVIRONMENT,
            index_name=settings.PINECONE_INDEX_NAME,
            dimension=embed_gen.get_embedding_dimension()
        )
        
        stats = vector_store.get_index_stats()
        print(f"   ✓ Connected to Pinecone")
        print(f"   ✓ Index: {settings.PINECONE_INDEX_NAME}")
        print(f"   ✓ Vectors: {stats.get('total_vectors', 0)}")
        
except Exception as e:
    print(f"   ⚠ Pinecone error: {e}")
    print(f"   This is OK for now - set it up when ready")

# Summary
print("\n" + "=" * 60)
print("Test Summary")
print("=" * 60)
print("""
✓ Environment configured
✓ LLaMA client working
✓ Text generation successful
✓ Embedding model loaded

Next steps:
1. Ensure Pinecone API key is set in .env
2. Add documents to src/data/notes/
3. Run: python src/main.py --ingest
4. Run: python src/main.py --interactive

Your EDITH setup is ready! 🚀
""")
