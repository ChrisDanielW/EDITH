"""Simple check of what's being retrieved"""
import sys
sys.path.insert(0, 'src')

from config.settings import settings
from services.vector_store import VectorStore
from utils.embeddings import EmbeddingGenerator

print("Initializing...")
embedding_gen = EmbeddingGenerator(settings.EMBEDDING_MODEL, settings.EMBEDDING_DEVICE)
vector_store = VectorStore(
    api_key=settings.PINECONE_API_KEY,
    environment=settings.PINECONE_ENVIRONMENT,
    index_name=settings.PINECONE_INDEX_NAME,
    dimension=embedding_gen.get_embedding_dimension()
)

query = "What is an interface?"
print(f"\nQuery: {query}\n")

query_embedding = embedding_gen.generate_embeddings(query)
results = vector_store.query_vectors(query_vector=query_embedding, top_k=5, include_metadata=True)

for i, result in enumerate(results, 1):
    print(f"Result {i}:")
    print(f"  Score: {result['score']:.4f}")
    print(f"  Chunk ID: {result.get('metadata', {}).get('chunk_id', 'N/A')}")
    print(f"  Text (first 200 chars):")
    print(f"  {result['text'][:200]}")
    has_interface = 'interface' in result['text'].lower()
    print(f"  Contains 'interface': {has_interface}\n")
