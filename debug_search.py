"""
Debug script to check what chunks are retrieved for a specific query
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.config.settings import settings
from src.services.vector_store import VectorStore
from src.utils.embeddings import EmbeddingGenerator

# Initialize components
print("Initializing...")
embedding_gen = EmbeddingGenerator(
    model_name=settings.EMBEDDING_MODEL,
    device=settings.EMBEDDING_DEVICE
)

vector_store = VectorStore(
    api_key=settings.PINECONE_API_KEY,
    environment=settings.PINECONE_ENVIRONMENT,
    index_name=settings.PINECONE_INDEX_NAME,
    dimension=embedding_gen.get_embedding_dimension()
)

# Query for "interface"
query = "What is an interface?"
print(f"\nQuery: {query}")
print("="*80)

query_embedding = embedding_gen.generate_embeddings(query)
results = vector_store.query_vectors(
    query_vector=query_embedding,
    top_k=10,
    include_metadata=True
)

print(f"\nFound {len(results)} results:\n")

for i, result in enumerate(results, 1):
    print(f"\n--- Result {i} ---")
    print(f"Score: {result['score']:.4f}")
    print(f"Chunk ID: {result.get('metadata', {}).get('chunk_id', 'N/A')}")
    print(f"Filename: {result.get('metadata', {}).get('filename', 'N/A')}")
    print(f"\nText preview (first 300 chars):")
    print(result['text'][:300])
    print("...")
    
    # Check if "interface" is in the chunk
    if 'interface' in result['text'].lower():
        print("✓ Contains 'interface'")
    else:
        print("✗ Does NOT contain 'interface'")

# Now let's search for chunks that actually contain "interface"
print("\n" + "="*80)
print("Searching for chunks that contain 'interface' keyword...")
print("="*80)

# This is a hacky way - we'll search with the word "interface" directly
interface_embedding = embedding_gen.generate_embeddings("interface definition class methods implementation")
interface_results = vector_store.query_vectors(
    query_vector=interface_embedding,
    top_k=10,
    include_metadata=True
)

found_interface = False
for i, result in enumerate(interface_results, 1):
    if 'interface' in result['text'].lower():
        if not found_interface:
            print("\nFound chunks with 'interface':")
            found_interface = True
        print(f"\n--- Match {i} (Score: {result['score']:.4f}) ---")
        print(result['text'][:400])
        print("...")
