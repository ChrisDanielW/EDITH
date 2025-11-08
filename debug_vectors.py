"""
Check all chunks in the vector store
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.config.settings import settings
from pinecone import Pinecone

# Connect to Pinecone
pc = Pinecone(api_key=settings.PINECONE_API_KEY)
index = pc.Index(settings.PINECONE_INDEX_NAME)

# Get index stats
stats = index.describe_index_stats()
print(f"Total vectors in index: {stats['total_vector_count']}")
print(f"Dimension: {stats['dimension']}")
print(f"\nNamespaces: {stats.get('namespaces', {})}")

# Try to fetch a few vectors to see what we have
print("\n" + "="*80)
print("Attempting to list some vectors...")
print("="*80)

# Since we can't list all IDs easily, let's try a broad query
from src.utils.embeddings import EmbeddingGenerator

embedding_gen = EmbeddingGenerator(
    model_name=settings.EMBEDDING_MODEL,
    device=settings.EMBEDDING_DEVICE
)

# Search for interface content
test_queries = [
    "interface class methods",
    "abstract class interface difference",
    "what is interface definition"
]

for query in test_queries:
    print(f"\n--- Searching for: '{query}' ---")
    query_emb = embedding_gen.generate_embeddings(query)
    results = index.query(vector=query_emb, top_k=5, include_metadata=True)
    
    for i, match in enumerate(results.matches, 1):
        text = match.metadata.get('text', '')
        has_interface = 'interface' in text.lower()
        print(f"{i}. Score: {match.score:.4f}, Chunk: {match.metadata.get('chunk_id', 'N/A')}, "
              f"Has 'interface': {'YES' if has_interface else 'NO'}")
        if has_interface:
            # Find the interface mention
            lines = text.split('\n')
            for line in lines:
                if 'interface' in line.lower():
                    print(f"   -> {line[:150]}")
