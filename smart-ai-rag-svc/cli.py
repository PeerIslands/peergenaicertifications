#!/usr/bin/env python3
"""
Command Line Interface for the RAG service.
"""
import argparse
import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent))

from src.services.rag_service import RAGService


def load_documents(args):
    """Load and index documents."""
    rag_service = RAGService()
    
    if args.file:
        result = rag_service.load_and_index_documents(file_path=args.file)
    elif args.directory:
        result = rag_service.load_and_index_documents(directory_path=args.directory)
    else:
        print("Error: Provide either --file or --directory")
        return
    
    if result["success"]:
        print(f"✓ {result['message']}")
        print(f"Documents indexed: {result['document_stats']['total_documents']}")
        print(f"Total characters: {result['document_stats']['total_characters']}")
    else:
        print(f"✗ {result['message']}")


def ask_question(args):
    """Ask a question to the RAG service."""
    rag_service = RAGService()
    
    result = rag_service.ask_question(
        question=args.question,
        k=args.k,
        use_conversation_history=args.history
    )
    
    print(f"Question: {args.question}")
    print(f"Answer: {result['answer']}")
    print(f"Sources used: {result['num_sources']}")
    print(f"Processing time: {result['processing_time']:.2f} seconds")
    
    if args.verbose and result['sources']:
        print("\nSources:")
        for i, source in enumerate(result['sources'][:3]):  # Show first 3 sources
            print(f"{i+1}. {source['content_preview']}")


def interactive_mode():
    """Interactive question-answering mode."""
    rag_service = RAGService()
    
    print("RAG Service Interactive Mode")
    print("Type 'quit' to exit, 'clear' to clear conversation history")
    print("-" * 50)
    
    while True:
        try:
            question = input("\nYour question: ").strip()
            
            if question.lower() in ['quit', 'exit', 'q']:
                break
            elif question.lower() == 'clear':
                rag_service.clear_conversation_history()
                print("Conversation history cleared.")
                continue
            elif not question:
                continue
            
            result = rag_service.ask_question(
                question=question,
                use_conversation_history=True
            )
            
            print(f"\nAnswer: {result['answer']}")
            print(f"(Sources: {result['num_sources']}, Time: {result['processing_time']:.2f}s)")
            
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"Error: {str(e)}")


def show_stats():
    """Show service statistics."""
    rag_service = RAGService()
    stats = rag_service.get_service_stats()
    
    print("RAG Service Statistics")
    print("-" * 30)
    print(f"LLM Model: {stats.get('llm_model', 'N/A')}")
    print(f"Embedding Model: {stats.get('embedding_model', 'N/A')}")
    print(f"Chunk Size: {stats.get('chunk_size', 'N/A')}")
    print(f"Chunk Overlap: {stats.get('chunk_overlap', 'N/A')}")
    print(f"Top K Results: {stats.get('top_k_results', 'N/A')}")
    print(f"Similarity Threshold: {stats.get('similarity_threshold', 'N/A')}")
    
    vector_stats = stats.get('vector_store_stats', {})
    if vector_stats:
        print(f"\nVector Store:")
        print(f"Documents: {vector_stats.get('document_count', 'N/A')}")
        print(f"Storage Size: {vector_stats.get('storage_size', 'N/A')} bytes")


def main():
    """Main CLI function."""
    parser = argparse.ArgumentParser(description="RAG Service CLI")
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Load documents command
    load_parser = subparsers.add_parser('load', help='Load and index documents')
    load_group = load_parser.add_mutually_exclusive_group(required=True)
    load_group.add_argument('--file', '-f', help='Path to PDF file')
    load_group.add_argument('--directory', '-d', help='Path to directory with PDFs')
    
    # Ask question command
    ask_parser = subparsers.add_parser('ask', help='Ask a question')
    ask_parser.add_argument('question', help='Question to ask')
    ask_parser.add_argument('--k', type=int, default=5, help='Number of sources to retrieve')
    ask_parser.add_argument('--history', action='store_true', help='Use conversation history')
    ask_parser.add_argument('--verbose', '-v', action='store_true', help='Show source details')
    
    # Interactive mode command
    subparsers.add_parser('interactive', help='Interactive question-answering mode')
    
    # Stats command
    subparsers.add_parser('stats', help='Show service statistics')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    try:
        if args.command == 'load':
            load_documents(args)
        elif args.command == 'ask':
            ask_question(args)
        elif args.command == 'interactive':
            interactive_mode()
        elif args.command == 'stats':
            show_stats()
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()


