"""
Test script to demonstrate TruLens RAG evaluation.

Usage:
    python examples/test_evaluation.py
"""
import requests
import json
from datetime import datetime


API_BASE_URL = "http://localhost:8000"


def test_evaluation_endpoint():
    """Test the /evaluate/rag endpoint with sample data."""
    print("\n" + "="*70)
    print("🧪 Testing RAG Evaluation Endpoint")
    print("="*70)
    
    # Sample evaluation request
    evaluation_data = {
        "question": "What is machine learning?",
        "answer": "Machine learning is a subset of artificial intelligence that enables computers to learn from data and improve their performance over time without being explicitly programmed. It uses algorithms to identify patterns in data and make predictions or decisions.",
        "context": [
            "Machine learning is a branch of artificial intelligence (AI) and computer science which focuses on the use of data and algorithms to imitate the way that humans learn.",
            "The process of learning begins with observations or data, such as examples, direct experience, or instruction, in order to look for patterns in data and make better decisions in the future.",
            "Machine learning algorithms build a model based on sample data, known as training data, in order to make predictions or decisions without being explicitly programmed to do so."
        ]
    }
    
    print("\n📝 Evaluation Request:")
    print(f"Question: {evaluation_data['question']}")
    print(f"Answer: {evaluation_data['answer'][:100]}...")
    print(f"Context chunks: {len(evaluation_data['context'])}")
    
    # Send request
    print("\n⏳ Sending evaluation request...")
    response = requests.post(
        f"{API_BASE_URL}/evaluate/rag",
        json=evaluation_data,
        headers={"Content-Type": "application/json"}
    )
    
    if response.status_code == 200:
        result = response.json()
        
        print("\n✅ Evaluation Complete!")
        print("\n📊 Metrics:")
        metrics = result['metrics']
        print(f"  • Answer Relevance:  {metrics['answer_relevance']:.3f}")
        print(f"  • Context Relevance: {metrics['context_relevance']:.3f}")
        print(f"  • Groundedness:      {metrics['groundedness']:.3f}")
        print(f"  • Overall Quality:   {metrics['overall_quality']:.3f}")
        
        print("\n📚 Context Stats:")
        stats = result['context_stats']
        print(f"  • Number of chunks:  {stats['num_chunks']}")
        print(f"  • Total characters:  {stats['total_chars']}")
        print(f"  • Avg chunk length:  {stats['avg_chunk_length']}")
        
        print(f"\n⏱️  Evaluation Time: {result['evaluation_time']}s")
        
        # Quality interpretation
        overall = metrics['overall_quality']
        if overall >= 0.8:
            print("\n✨ Quality: Excellent!")
        elif overall >= 0.6:
            print("\n✔️  Quality: Good")
        elif overall >= 0.4:
            print("\n⚠️  Quality: Fair")
        else:
            print("\n❌ Quality: Needs improvement")
        
        return result
    else:
        print(f"\n❌ Error: {response.status_code}")
        print(response.text)
        return None


def test_query_and_evaluate():
    """Test the /evaluate/rag-from-query endpoint (query + evaluate in one step)."""
    print("\n" + "="*70)
    print("🧪 Testing Query + Evaluation (One Step)")
    print("="*70)
    
    # This requires documents to be indexed first
    question = "What is machine learning?"
    
    print(f"\n📝 Question: {question}")
    print("⏳ Processing and evaluating...")
    
    response = requests.post(
        f"{API_BASE_URL}/evaluate/rag-from-query",
        data={
            "question": question,
            "use_llamaindex": True
        }
    )
    
    if response.status_code == 200:
        result = response.json()
        
        print("\n✅ Complete!")
        print("\n📖 RAG Response:")
        rag_resp = result['rag_response']
        print(f"Answer: {rag_resp['answer'][:200]}...")
        print(f"Sources: {len(rag_resp['sources'])} chunks")
        
        print("\n📊 Evaluation:")
        eval_data = result['evaluation']
        if 'metrics' in eval_data:
            metrics = eval_data['metrics']
            print(f"  • Answer Relevance:  {metrics['answer_relevance']:.3f}")
            print(f"  • Context Relevance: {metrics['context_relevance']:.3f}")
            print(f"  • Groundedness:      {metrics['groundedness']:.3f}")
            print(f"  • Overall Quality:   {metrics['overall_quality']:.3f}")
        
        print("\n" + result['summary'])
        
        return result
    else:
        print(f"\n❌ Error: {response.status_code}")
        if response.status_code == 500:
            print("Note: Make sure documents are uploaded first!")
        print(response.text)
        return None


def main():
    """Run all tests."""
    print("\n" + "="*70)
    print("🚀 TruLens RAG Evaluation Demo")
    print("="*70)
    
    # Test 1: Direct evaluation endpoint
    print("\n\n📍 Test 1: Direct Evaluation")
    print("-" * 70)
    test_evaluation_endpoint()
    
    # Test 2: Query + evaluate (requires documents)
    print("\n\n📍 Test 2: Query + Evaluate (One Step)")
    print("-" * 70)
    print("⚠️  Note: This requires documents to be indexed.")
    response = input("\nDo you have documents indexed? (y/n): ")
    
    if response.lower() == 'y':
        test_query_and_evaluate()
    else:
        print("\n💡 Tip: Upload some documents first using:")
        print("   POST /documents/upload-file")
        print("   Then try: POST /evaluate/rag-from-query")
    
    print("\n" + "="*70)
    print("✅ Demo Complete!")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()

