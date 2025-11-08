"""
EDITH Example Usage Script
Demonstrates basic functionality
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.main import EDITH


def example_basic_usage():
    """Basic usage example"""
    print("=" * 60)
    print("EDITH Example: Basic Usage")
    print("=" * 60)
    
    # Initialize EDITH
    edith = EDITH()
    
    # Example 1: Query
    print("\n1. Querying notes...")
    result = edith.query("What are the main topics in my notes?")
    print(f"\nAnswer: {result['answer']}")
    print(f"Confidence: {result['confidence']:.2f}")
    print(f"Sources: {len(result['sources'])}")
    
    # Example 2: Summary
    print("\n2. Generating summary...")
    summary = edith.summarize(style="bullet")
    print(f"\nSummary:\n{summary}")


def example_filtered_query():
    """Example with metadata filtering"""
    print("\n" + "=" * 60)
    print("EDITH Example: Filtered Query")
    print("=" * 60)
    
    edith = EDITH()
    
    # Query with filter (e.g., only from specific document type)
    result = edith.query(
        "What is machine learning?",
        filter_metadata={"type": "pdf"}
    )
    
    print(f"\nAnswer: {result['answer']}")


def example_document_ingestion():
    """Example of ingesting documents"""
    print("\n" + "=" * 60)
    print("EDITH Example: Document Ingestion")
    print("=" * 60)
    
    edith = EDITH()
    
    # Ingest documents from default directory
    print("\nIngesting documents from notes directory...")
    edith.ingest_documents()
    
    print("\n✓ Documents ingested successfully!")


if __name__ == "__main__":
    print("""
EDITH Usage Examples
====================

This script demonstrates basic EDITH functionality.

Note: Before running, ensure you have:
1. Configured .env file with API keys
2. Downloaded LLaMA model
3. Placed some documents in src/data/notes/

""")
    
    choice = input("Choose example (1: Basic, 2: Filtered, 3: Ingestion): ").strip()
    
    if choice == "1":
        example_basic_usage()
    elif choice == "2":
        example_filtered_query()
    elif choice == "3":
        example_document_ingestion()
    else:
        print("Running basic example...")
        example_basic_usage()
