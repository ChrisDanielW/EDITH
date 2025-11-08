"""
Check how the PDF is being chunked
"""
import sys
sys.path.insert(0, 'src')

from utils.document_loader import DocumentLoader
from utils.text_chunker import SmartChunker

# Load document
loader = DocumentLoader()
doc = loader.load_document('src/data/notes/oops concepts.pdf')

print(f"Document loaded:")
print(f"- Length: {len(doc['text'])} characters")
print(f"- Success: {doc['success']}")
print(f"- Filename: {doc['metadata'].get('filename', 'N/A')}")

# Chunk it
chunker = SmartChunker(chunk_size=1000, chunk_overlap=200)
chunks = chunker.chunk_text(doc['text'], doc['metadata'])

print(f"\nTotal chunks created: {len(chunks)}")
print(f"\nFirst 5 chunks:")
for c in chunks[:5]:
    print(f"\nChunk {c['chunk_id']}:")
    print(f"  Length: {len(c['text'])} chars")
    print(f"  Preview: {c['text'][:100]}...")

# Find interface chunks
interface_chunks = [(c['chunk_id'], c['text']) for c in chunks if 'interface' in c['text'].lower()]

print(f"\n{'='*80}")
print(f"Chunks containing 'interface': {len(interface_chunks)}")
print(f"{'='*80}")

for cid, text in interface_chunks[:3]:
    print(f"\n--- Chunk {cid} ---")
    print(text[:500])
    print("...")
