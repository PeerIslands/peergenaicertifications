"""
Framework Comparison: LlamaIndex vs LangChain

This example demonstrates the differences between using LlamaIndex 
and LangChain for RAG, helping you choose the right framework for your needs.

Usage:
    python examples/compare_frameworks.py
"""
import requests
import time
from typing import Dict, Any

API_BASE_URL = "http://localhost:8000"


def print_header(title):
    """Print a formatted header."""
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70 + "\n")


def upload_and_compare(pdf_file: str):
    """Upload the same document with both frameworks and compare."""
    print_header("📤 Document Upload Comparison")
    
    results = {}
    
    # Upload with LlamaIndex
    print("📘 Uploading with LlamaIndex (Sentence Window Retrieval)...")
    start_time = time.time()
    try:
        with open(pdf_file, 'rb') as f:
            response = requests.post(
                f"{API_BASE_URL}/documents/upload-file",
                files={"file": f},
                params={"use_llamaindex": True}
            )
        llamaindex_time = time.time() - start_time
        
        if response.status_code == 200:
            print(f"   ✅ Success! Time: {llamaindex_time:.2f}s")
            results['llamaindex_upload'] = response.json()
            results['llamaindex_upload']['time'] = llamaindex_time
        else:
            print(f"   ❌ Failed: {response.text}")
            
    except FileNotFoundError:
        print(f"   ❌ File not found: {pdf_file}")
        return None
    
    # Upload with LangChain
    print("\n📗 Uploading with LangChain (RecursiveCharacterTextSplitter)...")
    start_time = time.time()
    try:
        with open(pdf_file, 'rb') as f:
            response = requests.post(
                f"{API_BASE_URL}/documents/upload-file",
                files={"file": f},
                params={"use_llamaindex": False}
            )
        langchain_time = time.time() - start_time
        
        if response.status_code == 200:
            print(f"   ✅ Success! Time: {langchain_time:.2f}s")
            results['langchain_upload'] = response.json()
            results['langchain_upload']['time'] = langchain_time
        else:
            print(f"   ❌ Failed: {response.text}")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Comparison
    print("\n🔍 Upload Comparison:")
    print(f"   LlamaIndex: {llamaindex_time:.2f}s")
    print(f"   LangChain:  {langchain_time:.2f}s")
    
    if llamaindex_time < langchain_time:
        print(f"   → LlamaIndex was {(langchain_time/llamaindex_time - 1)*100:.1f}% faster")
    else:
        print(f"   → LangChain was {(llamaindex_time/langchain_time - 1)*100:.1f}% faster")
    
    return results


def query_and_compare(question: str):
    """Ask the same question with both frameworks and compare."""
    print_header(f"❓ Query Comparison: '{question}'")
    
    results = {}
    
    # Query with LlamaIndex
    print("📘 Querying with LlamaIndex...")
    response = requests.post(
        f"{API_BASE_URL}/questions/ask",
        json={
            "question": question,
            "use_llamaindex": True,
            "k": 5
        }
    )
    
    if response.status_code == 200:
        result = response.json()
        results['llamaindex'] = result
        print(f"   ✅ Answer received")
        print(f"   📊 Sources: {len(result.get('sources', []))} chunks")
        print(f"   ⏱️  Time: {result.get('processing_time', 0):.2f}s")
        print(f"   📝 Answer preview: {result['answer'][:100]}...")
    else:
        print(f"   ❌ Failed: {response.text}")
    
    # Query with LangChain
    print("\n📗 Querying with LangChain...")
    response = requests.post(
        f"{API_BASE_URL}/questions/ask",
        json={
            "question": question,
            "use_llamaindex": False,
            "k": 5
        }
    )
    
    if response.status_code == 200:
        result = response.json()
        results['langchain'] = result
        print(f"   ✅ Answer received")
        print(f"   📊 Sources: {len(result.get('sources', []))} chunks")
        print(f"   ⏱️  Time: {result.get('processing_time', 0):.2f}s")
        print(f"   📝 Answer preview: {result['answer'][:100]}...")
    else:
        print(f"   ❌ Failed: {response.text}")
    
    # Comparison
    if 'llamaindex' in results and 'langchain' in results:
        print("\n🔍 Detailed Comparison:")
        
        # Processing time
        llama_time = results['llamaindex'].get('processing_time', 0)
        lang_time = results['langchain'].get('processing_time', 0)
        print(f"\n   ⏱️  Processing Time:")
        print(f"      LlamaIndex: {llama_time:.2f}s")
        print(f"      LangChain:  {lang_time:.2f}s")
        
        # Source count
        llama_sources = len(results['llamaindex'].get('sources', []))
        lang_sources = len(results['langchain'].get('sources', []))
        print(f"\n   📚 Sources Retrieved:")
        print(f"      LlamaIndex: {llama_sources} chunks")
        print(f"      LangChain:  {lang_sources} chunks")
        
        # Answer length
        llama_answer_len = len(results['llamaindex']['answer'])
        lang_answer_len = len(results['langchain']['answer'])
        print(f"\n   📝 Answer Length:")
        print(f"      LlamaIndex: {llama_answer_len} characters")
        print(f"      LangChain:  {lang_answer_len} characters")
        
        # Show full answers
        print("\n   📖 Full Answers:")
        print(f"\n   LlamaIndex:")
        print(f"      {results['llamaindex']['answer']}")
        print(f"\n   LangChain:")
        print(f"      {results['langchain']['answer']}")
    
    return results


def evaluate_and_compare(question: str):
    """Evaluate responses from both frameworks."""
    print_header("📊 Quality Evaluation Comparison")
    
    results = {}
    
    # Evaluate LlamaIndex response
    print("📘 Evaluating LlamaIndex response...")
    response = requests.post(
        f"{API_BASE_URL}/evaluate/rag-from-query",
        data={
            "question": question,
            "use_llamaindex": True
        }
    )
    
    if response.status_code == 200:
        result = response.json()
        if 'metrics' in result['evaluation']:
            results['llamaindex'] = result['evaluation']['metrics']
            metrics = results['llamaindex']
            print(f"   ✅ Evaluation complete")
            print(f"   • Answer Relevance: {metrics['answer_relevance']:.3f}")
            print(f"   • Context Relevance: {metrics['context_relevance']:.3f}")
            print(f"   • Groundedness: {metrics['groundedness']:.3f}")
            print(f"   • Overall Quality: {metrics['overall_quality']:.3f}")
    
    # Evaluate LangChain response
    print("\n📗 Evaluating LangChain response...")
    response = requests.post(
        f"{API_BASE_URL}/evaluate/rag-from-query",
        data={
            "question": question,
            "use_llamaindex": False
        }
    )
    
    if response.status_code == 200:
        result = response.json()
        if 'metrics' in result['evaluation']:
            results['langchain'] = result['evaluation']['metrics']
            metrics = results['langchain']
            print(f"   ✅ Evaluation complete")
            print(f"   • Answer Relevance: {metrics['answer_relevance']:.3f}")
            print(f"   • Context Relevance: {metrics['context_relevance']:.3f}")
            print(f"   • Groundedness: {metrics['groundedness']:.3f}")
            print(f"   • Overall Quality: {metrics['overall_quality']:.3f}")
    
    # Comparison
    if 'llamaindex' in results and 'langchain' in results:
        print("\n🏆 Winner by Metric:")
        
        llama_metrics = results['llamaindex']
        lang_metrics = results['langchain']
        
        metrics_to_compare = [
            ('answer_relevance', 'Answer Relevance'),
            ('context_relevance', 'Context Relevance'),
            ('groundedness', 'Groundedness'),
            ('overall_quality', 'Overall Quality')
        ]
        
        for metric_key, metric_name in metrics_to_compare:
            llama_score = llama_metrics[metric_key]
            lang_score = lang_metrics[metric_key]
            
            if llama_score > lang_score:
                winner = "📘 LlamaIndex"
                diff = ((llama_score - lang_score) / lang_score * 100) if lang_score > 0 else 0
            elif lang_score > llama_score:
                winner = "📗 LangChain"
                diff = ((lang_score - llama_score) / llama_score * 100) if llama_score > 0 else 0
            else:
                winner = "🤝 Tie"
                diff = 0
            
            print(f"   {metric_name:20s}: {winner:20s} (+{diff:.1f}%)")
    
    return results


def show_recommendations():
    """Show framework recommendations."""
    print_header("💡 Framework Recommendations")
    
    print("📘 Use LlamaIndex when:")
    print("   ✅ Answer quality is your top priority")
    print("   ✅ You need advanced retrieval (Sentence Window)")
    print("   ✅ You're building a production RAG system")
    print("   ✅ You need better metadata handling")
    print("   ✅ You want the latest RAG innovations")
    
    print("\n📗 Use LangChain when:")
    print("   ✅ You need conversation memory")
    print("   ✅ You're building complex agent workflows")
    print("   ✅ You need broader LLM ecosystem integration")
    print("   ✅ You're familiar with LangChain already")
    print("   ✅ You need more flexibility for custom chains")
    
    print("\n🎯 Default Recommendation:")
    print("   → Use LlamaIndex for RAG applications")
    print("   → It's optimized specifically for retrieval tasks")
    print("   → Sentence Window Retrieval provides better context")


def main():
    """Run framework comparison."""
    print("\n" + "="*70)
    print("  🔄 Framework Comparison: LlamaIndex vs LangChain")
    print("="*70)
    
    # Check service
    try:
        response = requests.get(f"{API_BASE_URL}/health")
        if response.status_code != 200:
            print("\n❌ Service is not running. Start it with: python main.py")
            return
    except Exception as e:
        print(f"\n❌ Cannot connect to service: {e}")
        return
    
    # Get PDF file
    print("\n📄 To compare frameworks, we need a PDF document.")
    pdf_file = input("Enter PDF file path: ").strip()
    
    if not pdf_file:
        print("❌ No file provided. Exiting.")
        return
    
    # Run comparisons
    print("\nStarting comprehensive comparison...")
    print("(This will take a few minutes...)\n")
    
    # 1. Upload comparison
    upload_results = upload_and_compare(pdf_file)
    
    if not upload_results:
        print("❌ Upload failed. Cannot continue.")
        return
    
    # 2. Query comparison
    test_questions = [
        "What is the main topic of this document?",
        "Can you summarize the key points?",
        "What are the most important details?"
    ]
    
    for question in test_questions:
        query_and_compare(question)
    
    # 3. Quality evaluation
    evaluate_and_compare(test_questions[0])
    
    # 4. Recommendations
    show_recommendations()
    
    # Summary
    print("\n" + "="*70)
    print("  ✅ Comparison Complete!")
    print("="*70)
    print("\n🎓 Key Takeaways:")
    print("   • Both frameworks are powerful for RAG")
    print("   • LlamaIndex excels at retrieval quality")
    print("   • LangChain excels at complex workflows")
    print("   • Choose based on your specific needs")
    print("\n🔗 Learn more:")
    print("   • LlamaIndex: https://docs.llamaindex.ai/")
    print("   • LangChain: https://python.langchain.com/")
    print("\n")


if __name__ == "__main__":
    main()

