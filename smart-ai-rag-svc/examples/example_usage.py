"""
Complete example usage of the Smart AI RAG Service.

This example demonstrates:
1. Uploading documents (LlamaIndex vs LangChain)
2. Asking questions
3. Using conversation history
4. Evaluating RAG quality
5. Comparing frameworks

Requirements:
- Service running at http://localhost:8000
- Documents uploaded before running
"""
import requests
import json
from pathlib import Path

API_BASE_URL = "http://localhost:8000"


def print_section(title):
    """Print a section header."""
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70)


def check_service_health():
    """Check if the service is running."""
    print_section("1. Checking Service Health")
    
    try:
        response = requests.get(f"{API_BASE_URL}/health")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Service is healthy")
            print(f"   Status: {data['status']}")
            print(f"   Version: {data['version']}")
            return True
        else:
            print(f"❌ Service returned status code: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Service is not running: {e}")
        print(f"   Please start the service: python main.py")
        return False


def upload_document_llamaindex(file_path):
    """Upload a document using LlamaIndex (Sentence Window Retrieval)."""
    print_section("2. Upload Document with LlamaIndex")
    
    print(f"📄 Uploading: {file_path}")
    print("   Using: LlamaIndex with Sentence Window Retrieval")
    
    try:
        with open(file_path, 'rb') as f:
            response = requests.post(
                f"{API_BASE_URL}/documents/upload-file",
                files={"file": f},
                params={"use_llamaindex": True}
            )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Upload successful!")
            print(f"   Status: {result['status']}")
            print(f"   Documents indexed: {result.get('num_documents', 'N/A')}")
            print(f"   Chunks created: {result.get('num_chunks', 'N/A')}")
            return True
        else:
            print(f"❌ Upload failed: {response.text}")
            return False
            
    except FileNotFoundError:
        print(f"❌ File not found: {file_path}")
        print("   Please provide a valid PDF file path")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def upload_document_langchain(file_path):
    """Upload a document using LangChain."""
    print_section("2b. Upload Document with LangChain (Alternative)")
    
    print(f"📄 Uploading: {file_path}")
    print("   Using: LangChain with RecursiveCharacterTextSplitter")
    
    try:
        with open(file_path, 'rb') as f:
            response = requests.post(
                f"{API_BASE_URL}/documents/upload-file",
                files={"file": f},
                params={"use_llamaindex": False}
            )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Upload successful!")
            print(f"   Status: {result['status']}")
            return True
        else:
            print(f"❌ Upload failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def ask_question(question, use_llamaindex=True, use_conversation=False):
    """Ask a question to the RAG service."""
    print(f"\n❓ Question: {question}")
    print(f"   Engine: {'LlamaIndex' if use_llamaindex else 'LangChain'}")
    print(f"   Conversation: {'Yes' if use_conversation else 'No'}")
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/questions/ask",
            json={
                "question": question,
                "use_llamaindex": use_llamaindex,
                "k": 5,
                "use_conversation_history": use_conversation
            }
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"\n💡 Answer: {result['answer'][:200]}...")
            print(f"   Sources: {len(result.get('sources', []))} chunks")
            print(f"   Processing time: {result.get('processing_time', 0):.2f}s")
            print(f"   Query engine: {result.get('query_engine', 'N/A')}")
            return result
        else:
            print(f"❌ Error: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return None


def demonstrate_questions():
    """Demonstrate asking various questions."""
    print_section("3. Asking Questions (LlamaIndex)")
    
    questions = [
        "What is the main topic of the document?",
        "Can you summarize the key points?",
        "What are the most important details mentioned?"
    ]
    
    results = []
    for question in questions:
        result = ask_question(question, use_llamaindex=True)
        if result:
            results.append(result)
    
    return results


def demonstrate_conversation():
    """Demonstrate conversation with history."""
    print_section("4. Conversation with History (LangChain)")
    
    # Clear previous conversation
    requests.delete(f"{API_BASE_URL}/conversation/history")
    print("🧹 Cleared conversation history\n")
    
    conversation_questions = [
        "What is artificial intelligence?",
        "How is it different from machine learning?",
        "Can you give me practical applications?"
    ]
    
    for i, question in enumerate(conversation_questions, 1):
        print(f"\n[Turn {i}]")
        ask_question(
            question,
            use_llamaindex=False,  # LangChain has conversation memory
            use_conversation=True
        )


def evaluate_rag_response():
    """Demonstrate RAG evaluation."""
    print_section("5. RAG Quality Evaluation")
    
    print("📊 Evaluating a sample response...")
    
    evaluation_data = {
        "question": "What is machine learning?",
        "answer": "Machine learning is a subset of artificial intelligence that enables computers to learn from data and improve their performance over time without being explicitly programmed. It uses algorithms to identify patterns in data.",
        "context": [
            "Machine learning is a branch of artificial intelligence (AI) and computer science which focuses on the use of data and algorithms.",
            "ML algorithms build a model based on sample data, known as training data, in order to make predictions or decisions.",
            "The process of learning begins with observations or data to look for patterns and make better decisions in the future."
        ]
    }
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/evaluate/rag",
            json=evaluation_data
        )
        
        if response.status_code == 200:
            result = response.json()
            metrics = result['metrics']
            
            print("\n✅ Evaluation Complete!")
            print("\n📊 Quality Metrics:")
            print(f"   • Answer Relevance:  {metrics['answer_relevance']:.3f} / 1.000")
            print(f"   • Context Relevance: {metrics['context_relevance']:.3f} / 1.000")
            print(f"   • Groundedness:      {metrics['groundedness']:.3f} / 1.000")
            print(f"   • Overall Quality:   {metrics['overall_quality']:.3f} / 1.000")
            
            # Quality interpretation
            overall = metrics['overall_quality']
            if overall >= 0.8:
                print("\n   ✨ Quality: EXCELLENT!")
            elif overall >= 0.6:
                print("\n   ✔️  Quality: GOOD")
            elif overall >= 0.4:
                print("\n   ⚠️  Quality: FAIR")
            else:
                print("\n   ❌ Quality: NEEDS IMPROVEMENT")
            
            print(f"\n   ⏱️  Evaluation time: {result['evaluation_time']:.2f}s")
            return result
        else:
            print(f"❌ Evaluation failed: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return None


def evaluate_query_end_to_end():
    """Demonstrate end-to-end query and evaluation."""
    print_section("6. Query + Evaluate (One Step)")
    
    question = "What is the main topic of the document?"
    print(f"❓ Question: {question}")
    print("   This will query the RAG system AND evaluate the response!\n")
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/evaluate/rag-from-query",
            data={
                "question": question,
                "use_llamaindex": True
            }
        )
        
        if response.status_code == 200:
            result = response.json()
            
            # Show RAG response
            rag_resp = result['rag_response']
            print("📖 RAG Response:")
            print(f"   Answer: {rag_resp['answer'][:150]}...")
            print(f"   Sources: {len(rag_resp.get('sources', []))} chunks")
            
            # Show evaluation
            if 'metrics' in result['evaluation']:
                metrics = result['evaluation']['metrics']
                print("\n📊 Quality Evaluation:")
                print(f"   • Answer Relevance:  {metrics['answer_relevance']:.3f}")
                print(f"   • Context Relevance: {metrics['context_relevance']:.3f}")
                print(f"   • Groundedness:      {metrics['groundedness']:.3f}")
                print(f"   • Overall Quality:   {metrics['overall_quality']:.3f}")
            
            return result
        else:
            print(f"❌ Error: {response.text}")
            if "no documents" in response.text.lower():
                print("\n💡 Tip: Upload some documents first!")
            return None
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return None


def compare_frameworks():
    """Compare LlamaIndex vs LangChain."""
    print_section("7. Framework Comparison")
    
    test_question = "What is the main topic?"
    
    print("🔄 Asking the same question with both frameworks:\n")
    
    # LlamaIndex
    print("📘 LlamaIndex (Sentence Window Retrieval):")
    llamaindex_result = ask_question(test_question, use_llamaindex=True)
    
    # LangChain
    print("\n📗 LangChain (RecursiveCharacterTextSplitter):")
    langchain_result = ask_question(test_question, use_llamaindex=False)
    
    # Compare
    print("\n🔍 Comparison:")
    if llamaindex_result and langchain_result:
        print(f"   LlamaIndex processing time: {llamaindex_result.get('processing_time', 0):.2f}s")
        print(f"   LangChain processing time:  {langchain_result.get('processing_time', 0):.2f}s")
        print(f"\n   LlamaIndex sources: {len(llamaindex_result.get('sources', []))}")
        print(f"   LangChain sources:  {len(langchain_result.get('sources', []))}")


def get_service_stats():
    """Get service statistics."""
    print_section("8. Service Statistics")
    
    try:
        response = requests.get(f"{API_BASE_URL}/stats")
        
        if response.status_code == 200:
            stats = response.json()
            
            print(f"📊 Service Configuration:")
            print(f"   LLM Model: {stats.get('llm_model', 'N/A')}")
            print(f"   Embedding Model: {stats.get('embedding_model', 'N/A')}")
            print(f"   Top K Results: {stats.get('top_k', 'N/A')}")
            print(f"   Similarity Threshold: {stats.get('similarity_threshold', 'N/A')}")
            
            if 'approaches_info' in stats:
                print(f"\n🔧 Available Approaches:")
                for approach in stats['approaches_info'].get('available_approaches', []):
                    print(f"   • {approach}")
                print(f"\n   Default: {stats['approaches_info'].get('default_approach', 'N/A')}")
            
            return stats
        else:
            print(f"❌ Error: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return None


def main():
    """Run all examples."""
    print("\n" + "="*70)
    print("  🚀 Smart AI RAG Service - Complete Example")
    print("="*70)
    
    # Check service health
    if not check_service_health():
        print("\n❌ Service is not running. Please start it first:")
        print("   python main.py")
        return
    
    # Get service stats
    get_service_stats()
    
    # Check if user has documents
    print("\n" + "="*70)
    print("  📄 Document Upload")
    print("="*70)
    print("\n⚠️  To run the full demo, you need to upload a PDF document.")
    
    file_path = input("\nEnter PDF file path (or press Enter to skip upload): ").strip()
    
    if file_path:
        # Upload with LlamaIndex (recommended)
        upload_document_llamaindex(file_path)
        
        # Optionally upload with LangChain for comparison
        # upload_document_langchain(file_path)
    else:
        print("\n⏭️  Skipping document upload.")
        print("   Make sure you have documents indexed before asking questions!")
    
    # Ask questions
    demonstrate_questions()
    
    # Demonstrate conversation
    demonstrate_conversation()
    
    # Evaluate RAG quality
    evaluate_rag_response()
    
    # End-to-end evaluation
    if file_path:
        evaluate_query_end_to_end()
    
    # Compare frameworks
    if file_path:
        compare_frameworks()
    
    # Final summary
    print("\n" + "="*70)
    print("  ✅ Example Complete!")
    print("="*70)
    print("\n📚 What you learned:")
    print("   ✅ How to upload documents (LlamaIndex & LangChain)")
    print("   ✅ How to ask questions")
    print("   ✅ How to use conversation history")
    print("   ✅ How to evaluate RAG quality")
    print("   ✅ How to compare frameworks")
    print("\n🔗 Next steps:")
    print("   • Try the web interface: test_upload.html")
    print("   • Read the docs: http://localhost:8000/docs")
    print("   • Check the README.md for more examples")
    print("\n")


if __name__ == "__main__":
    main()
