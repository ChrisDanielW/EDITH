"""
Directly search for chunk 17 embedding
"""
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

# Load the actual chunks to get chunk 17's text
from utils.document_loader import DocumentLoader
from utils.text_chunker import SmartChunker

loader = DocumentLoader()
doc = loader.load_document('src/data/notes/oops concepts.pdf')
chunker = SmartChunker(chunk_size=1000, chunk_overlap=200)
chunks = chunker.chunk_text(doc['text'], doc['metadata'])

print(f"\nTotal chunks: {len(chunks)}")

# Find chunk 17
chunk17 = next((c for c in chunks if c['chunk_id'] == 17), None)
if chunk17:
    print(f"\nChunk 17 text:")
    print(chunk17['text'])
    print(f"\n{'='*80}\n")
    
    # Generate embedding for chunk 17's text
    chunk17_embedding = embedding_gen.generate_embeddings(chunk17['text'])
    
    # Search for this exact chunk
    results = vector_store.query_vectors(
        query_vector=chunk17_embedding,
        top_k=3,
        include_metadata=True
    )
    
    print("Searching for chunk 17 by its own embedding:")
    for i, result in enumerate(results, 1):
        print(f"\nResult {i}:")
        print(f"  Score: {result['score']:.4f}")
        print(f"  Chunk ID: {result.get('metadata', {}).get('chunk_id', 'N/A')}")
        print(f"  Text preview: {result['text'][:150]}...")
