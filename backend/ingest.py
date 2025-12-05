from pypdf import PdfReader
from langchain_text_splitters import CharacterTextSplitter
from sentence_transformers import SentenceTransformer
import chromadb
import os

# Directory containing PDFs
PDF_DIR = os.path.join(os.path.dirname(__file__), "pdfs")

# Chroma persistent DB directory
PERSIST_DIR = os.path.join(os.path.dirname(__file__), "chroma_db")


def pdf_to_text(path):
    """Extract text from a PDF file."""
    reader = PdfReader(path)
    texts = [page.extract_text() or "" for page in reader.pages]
    return "\n".join(texts)


# ------------------------
# Load all PDF files
# ------------------------
pdf_files = [f for f in os.listdir(PDF_DIR) if f.lower().endswith(".pdf")]

if not pdf_files:
    print("❌ No PDF files found in /pdfs/ folder.")
    exit(1)

print(f"📄 PDFs found: {pdf_files}")

all_chunks = []
chunk_id = 0  # unique incremental ID


# Chunk splitter
splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=200)

# Read each PDF
for pdf in pdf_files:
    pdf_path = os.path.join(PDF_DIR, pdf)
    print(f"\n🔍 Processing: {pdf}")

    text = pdf_to_text(pdf_path)
    chunks = splitter.split_text(text)

    # Tag chunks by filename to avoid confusion
    chunks = [f"[{pdf}] {c}" for c in chunks]

    all_chunks.extend(chunks)

print(f"\n📌 Total chunks generated: {len(all_chunks)}")


# ------------------------
# Embed chunks
# ------------------------
print("\n⚙️ Generating embeddings...")
model = SentenceTransformer("all-MiniLM-L6-v2")
embeddings = model.encode(all_chunks, show_progress_bar=True)


# ------------------------
# ChromaDB persistent client
# ------------------------
client = chromadb.PersistentClient(path=PERSIST_DIR)

# Create or load collection
COLLECTION_NAME = "peer-ai-table"

try:
    collection = client.get_collection(COLLECTION_NAME)
except ValueError:  # ChromaDB 0.5.x
    collection = client.create_collection(name=COLLECTION_NAME)

# Insert documents into Chroma
ids = [str(i) for i in range(len(all_chunks))]

collection.add(
    documents=all_chunks,
    embeddings=embeddings.tolist(),
    ids=ids
)

print("\n✅ Ingestion complete!")
print(f"📦 Total documents stored: {len(all_chunks)}")
print(f"💾 Chroma DB location: {PERSIST_DIR}")

