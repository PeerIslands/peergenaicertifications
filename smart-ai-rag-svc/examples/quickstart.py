"""
Quickstart Example - Get started in 5 minutes!

This is the simplest possible example to get you started with the RAG service.

Usage:
    python examples/quickstart.py
"""
import requests

# Configuration
API_BASE_URL = "http://localhost:8000"
PDF_FILE = "your_document.pdf"  # ⬅️ Change this to your PDF file path


def main():
    print("🚀 Smart AI RAG Service - Quickstart\n")
    
    # Step 1: Check if service is running
    print("1️⃣  Checking service health...")
    try:
        response = requests.get(f"{API_BASE_URL}/health")
        if response.status_code != 200:
            print("❌ Service is not running. Start it with: python main.py")
            return
        print("✅ Service is healthy!\n")
    except Exception as e:
        print(f"❌ Cannot connect to service: {e}")
        print("   Start the service with: python main.py")
        return
    
    # Step 2: Upload a document
    print("2️⃣  Uploading document...")
    try:
        with open(PDF_FILE, 'rb') as f:
            response = requests.post(
                f"{API_BASE_URL}/documents/upload-file",
                files={"file": f},
                params={"use_llamaindex": True}  # Use LlamaIndex (recommended)
            )
        
        if response.status_code == 200:
            print("✅ Document uploaded successfully!\n")
        else:
            print(f"❌ Upload failed: {response.text}")
            return
            
    except FileNotFoundError:
        print(f"❌ File not found: {PDF_FILE}")
        print(f"   Please update the PDF_FILE variable in this script.")
        return
    
    # Step 3: Ask a question
    print("3️⃣  Asking a question...")
    response = requests.post(
        f"{API_BASE_URL}/questions/ask",
        json={
            "question": "What is the main topic of this document?",
            "use_llamaindex": True,
            "k": 5
        }
    )
    
    if response.status_code == 200:
        result = response.json()
        print("\n📖 Answer:")
        print(f"   {result['answer']}\n")
        print(f"   ℹ️  Used {len(result.get('sources', []))} source chunks")
        print(f"   ⏱️  Processing time: {result.get('processing_time', 0):.2f}s\n")
    else:
        print(f"❌ Question failed: {response.text}")
        return
    
    # Step 4: Evaluate the quality (optional)
    print("4️⃣  Evaluating RAG quality...")
    response = requests.post(
        f"{API_BASE_URL}/evaluate/rag-from-query",
        data={
            "question": "What is the main topic?",
            "use_llamaindex": True
        }
    )
    
    if response.status_code == 200:
        result = response.json()
        if 'metrics' in result['evaluation']:
            metrics = result['evaluation']['metrics']
            print("\n📊 Quality Scores:")
            print(f"   • Answer Relevance: {metrics['answer_relevance']:.2f}")
            print(f"   • Context Relevance: {metrics['context_relevance']:.2f}")
            print(f"   • Groundedness: {metrics['groundedness']:.2f}")
            print(f"   • Overall Quality: {metrics['overall_quality']:.2f}")
            
            if metrics['overall_quality'] >= 0.8:
                print("\n   ✨ Excellent quality!")
            elif metrics['overall_quality'] >= 0.6:
                print("\n   ✔️  Good quality")
            else:
                print("\n   ⚠️  Could be improved")
    
    # Done!
    print("\n" + "="*60)
    print("✅ Quickstart Complete!")
    print("="*60)
    print("\n🎯 Next steps:")
    print("   • Try more questions")
    print("   • Upload more documents")
    print("   • Check the full example: python examples/example_usage.py")
    print("   • Read the docs: http://localhost:8000/docs")
    print("\n")


if __name__ == "__main__":
    main()

