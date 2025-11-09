"""
EDITH Flask API Server
Provides REST API endpoints for the web UI
"""

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import sys
from pathlib import Path
import logging
import os

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from main import EDITH

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Get absolute paths
BASE_DIR = Path(__file__).parent.parent.parent
UI_DIR = BASE_DIR / 'ui'

# Initialize Flask app with absolute path
app = Flask(__name__, 
            static_folder=str(UI_DIR),
            static_url_path='')
CORS(app)  # Enable CORS for frontend

# Initialize EDITH (do this once on startup)
logger.info("Initializing EDITH...")
edith = None

def get_edith():
    """Lazy initialization of EDITH"""
    global edith
    if edith is None:
        edith = EDITH()
    return edith


@app.route('/')
def index():
    """Serve the main UI"""
    return send_from_directory(app.static_folder, 'index.html')


@app.route('/<path:path>')
def serve_static(path):
    """Serve static files (CSS, JS, etc.)"""
    return send_from_directory(app.static_folder, path)


@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'EDITH API',
        'version': '1.0.0'
    })


@app.route('/api/query', methods=['POST'])
def query():
    """
    Query EDITH with a question
    
    Request body:
    {
        "query": "What is polymorphism?",
        "use_rag": true/false (optional, auto-detect if not provided)
    }
    
    Response:
    {
        "answer": "...",
        "mode": "rag" or "conversational",
        "confidence": 0.85,
        "sources": [...],
        "num_sources": 2
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'query' not in data:
            return jsonify({
                'error': 'Missing query parameter'
            }), 400
        
        user_query = data['query']
        use_rag = data.get('use_rag', None)
        
        logger.info(f"Received query: {user_query}")
        
        # Get EDITH instance
        edith_instance = get_edith()
        
        # Process query
        result = edith_instance.query(user_query, use_rag=use_rag)
        
        logger.info(f"Query processed - Mode: {result.get('mode')}, Sources: {result.get('num_sources', 0)}")
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error processing query: {str(e)}")
        return jsonify({
            'error': str(e),
            'answer': 'Sorry, I encountered an error processing your request.',
            'mode': 'error',
            'confidence': 0.0,
            'sources': [],
            'num_sources': 0
        }), 500


@app.route('/api/summary', methods=['POST'])
def summary():
    """
    Generate a summary of notes
    
    Request body:
    {
        "style": "comprehensive" | "bullet" | "brief"
    }
    
    Response:
    {
        "summary": "...",
        "style": "comprehensive"
    }
    """
    try:
        data = request.get_json() or {}
        style = data.get('style', 'comprehensive')
        
        logger.info(f"Generating {style} summary")
        
        # Get EDITH instance
        edith_instance = get_edith()
        
        # Generate summary
        summary_text = edith_instance.summarize(style=style)
        
        return jsonify({
            'summary': summary_text,
            'style': style
        })
        
    except Exception as e:
        logger.error(f"Error generating summary: {str(e)}")
        return jsonify({
            'error': str(e),
            'summary': 'Sorry, I encountered an error generating the summary.'
        }), 500


@app.route('/api/ingest', methods=['POST'])
def ingest():
    """
    Ingest documents from the notes directory
    
    Request body:
    {
        "directory": "optional/path/to/notes"
    }
    
    Response:
    {
        "status": "success",
        "message": "Ingested 50 chunks from 1 document"
    }
    """
    try:
        data = request.get_json() or {}
        directory = data.get('directory', None)
        
        logger.info(f"Starting document ingestion from: {directory or 'default location'}")
        
        # Get EDITH instance
        edith_instance = get_edith()
        
        # Ingest documents
        edith_instance.ingest_documents(directory=directory)
        
        return jsonify({
            'status': 'success',
            'message': 'Documents ingested successfully'
        })
        
    except Exception as e:
        logger.error(f"Error ingesting documents: {str(e)}")
        return jsonify({
            'error': str(e),
            'status': 'error',
            'message': 'Failed to ingest documents'
        }), 500


@app.route('/api/upload', methods=['POST'])
def upload_file():
    """
    Upload and ingest a single document
    
    Form data:
    - file: The document file to upload
    
    Response:
    {
        "status": "success",
        "message": "File uploaded and processed",
        "filename": "document.pdf",
        "chunks": 25
    }
    """
    try:
        # Check if file was uploaded
        if 'file' not in request.files:
            return jsonify({
                'error': 'No file provided',
                'status': 'error'
            }), 400
        
        file = request.files['file']
        
        # Check if filename is empty
        if file.filename == '':
            return jsonify({
                'error': 'No file selected',
                'status': 'error'
            }), 400
        
        # Check file extension
        allowed_extensions = {'.pdf', '.docx', '.pptx', '.txt', '.md', '.png', '.jpg', '.jpeg'}
        file_ext = Path(file.filename).suffix.lower()
        
        if file_ext not in allowed_extensions:
            return jsonify({
                'error': f'File type {file_ext} not supported. Allowed: {", ".join(allowed_extensions)}',
                'status': 'error'
            }), 400
        
        # Save file to notes directory
        notes_dir = Path(__file__).parent.parent / 'data' / 'notes'
        notes_dir.mkdir(parents=True, exist_ok=True)
        
        file_path = notes_dir / file.filename
        file.save(str(file_path))
        
        logger.info(f"File uploaded: {file.filename}")
        
        # Get EDITH instance and ingest the file
        edith_instance = get_edith()
        
        # Ingest just this file
        from utils.document_loader import DocumentLoader
        from utils.text_chunker import TextChunker
        
        doc_loader = DocumentLoader()
        chunker = TextChunker()
        
        # Load document (returns a dict with 'text' and 'metadata')
        doc_result = doc_loader.load_document(str(file_path))
        
        if not doc_result.get('success', True):
            return jsonify({
                'error': 'Failed to process document',
                'status': 'error',
                'message': doc_result.get('metadata', {}).get('error', 'Unknown error')
            }), 400
        
        # Chunk the document text
        chunks = chunker.chunk_text(
            doc_result['text'],
            metadata={
                'filename': doc_result['metadata']['filename'],
                'type': doc_result['metadata']['type']
            }
        )
        
        # Generate embeddings and store in vector database
        if chunks:
            # Extract texts and prepare metadata
            texts = [chunk['text'] for chunk in chunks]
            metadatas = []
            for chunk in chunks:
                metadata = chunk.get('metadata', {}).copy()
                metadata['chunk_id'] = chunk.get('chunk_id', 0)
                metadata['char_count'] = chunk.get('char_count', 0)
                metadatas.append(metadata)
            
            # Generate embeddings
            embeddings = edith_instance.embedding_generator.batch_generate_embeddings(
                texts,
                batch_size=32,
                show_progress=False
            )
            
            # Upsert to vector store
            result = edith_instance.vector_store.upsert_vectors(
                vectors=embeddings,
                texts=texts,
                metadatas=metadatas
            )
            
            if result['success']:
                logger.info(f"Stored {len(chunks)} chunks from {file.filename}")
            else:
                raise Exception(f"Failed to store vectors: {result.get('error', 'Unknown error')}")
        
        return jsonify({
            'status': 'success',
            'message': f'File uploaded and processed successfully',
            'filename': file.filename,
            'chunks': len(chunks)
        })
        
    except Exception as e:
        logger.error(f"Error uploading file: {str(e)}")
        return jsonify({
            'error': str(e),
            'status': 'error',
            'message': 'Failed to upload and process file'
        }), 500


@app.route('/api/stats', methods=['GET'])
def stats():
    """
    Get statistics about the vector database
    
    Response:
    {
        "total_vectors": 50,
        "dimension": 384,
        "index_fullness": 0.0
    }
    """
    try:
        edith_instance = get_edith()
        
        stats_data = edith_instance.vector_store.get_index_stats()
        
        return jsonify(stats_data)
        
    except Exception as e:
        logger.error(f"Error getting stats: {str(e)}")
        return jsonify({
            'error': str(e)
        }), 500


@app.route('/api/generate-title', methods=['POST'])
def generate_title():
    """
    Generate a conversation title based on the first message
    
    Request body:
    {
        "message": "What is polymorphism in OOP?"
    }
    
    Response:
    {
        "title": "Understanding OOP Polymorphism"
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'message' not in data:
            return jsonify({
                'error': 'Missing message parameter'
            }), 400
        
        message = data['message']
        logger.info(f"Generating title for message: {message[:50]}...")
        
        # Get EDITH instance
        edith_instance = get_edith()
        
        # Create a prompt for title generation
        title_prompt = f"Generate a brief, descriptive 3-5 word title for a conversation that starts with this message: \"{message}\"\n\nRespond with ONLY the title, nothing else."
        
        # Use conversational mode with low token limit for quick response
        result = edith_instance.query(title_prompt, use_rag=False)
        
        # Extract the title from the response
        title = result.get('answer', '').strip()
        
        # Clean up the title (remove quotes if present)
        title = title.strip('"\'').strip()
        
        # Fallback if title is too long or empty
        if not title or len(title) > 60:
            title = message[:50] + ('...' if len(message) > 50 else '')
        
        logger.info(f"Generated title: {title}")
        
        return jsonify({
            'title': title
        })
        
    except Exception as e:
        logger.error(f"Error generating title: {str(e)}")
        # Fallback to message substring
        message = data.get('message', 'New Conversation')
        fallback_title = message[:50] + ('...' if len(message) > 50 else '')
        return jsonify({
            'title': fallback_title
        })


if __name__ == '__main__':
    print("\n" + "=" * 60)
    print("🚀 Starting EDITH API Server")
    print("=" * 60)
    print("📡 API: http://localhost:5000/api")
    print("🌐 UI:  http://localhost:5000")
    print("=" * 60 + "\n")
    
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True,
        threaded=True
    )
