from pypdf import PdfReader
from langchain_text_splitters import CharacterTextSplitter
from sentence_transformers import SentenceTransformer
import chromadb
import os

PDF_PATH = "../pdf/GenerativeAI.pdf"
PERSIST_DIR = os.path.join(os.path.dirname(__file__), "chroma_db")  # persistent DB folder


# /**
#  * Extract full text content from a PDF file using PyPDF.
#  *
#  * @param {str} path - Path to the PDF file.
#  * @returns {str} The extracted text from all PDF pages.
#  */
def pdf_to_text(path):
    reader = PdfReader(path)
    texts = [p.extract_text() or "" for p in reader.pages]
    return "\n".join(texts)


# Read full PDF text
text = pdf_to_text(PDF_PATH)


# /**
#  * Split large text into smaller chunks for embedding.
#  *
#  * @constant
#  * @type {CharacterTextSplitter}
#  * @property {number} chunk_size - Maximum size of each chunk.
#  * @property {number} chunk_overlap - Overlap between chunks for context preservation.
#  */
splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
chunks = splitter.split_text(text)


# /**
#  * Load embedding model (SentenceTransformer)
#  * Used to convert text chunks into high-dimensional vectors.
#  *
#  * @type {SentenceTransformer}
#  * @model all-MiniLM-L6-v2
#  */
model = SentenceTransformer("all-MiniLM-L6-v2")

# Generate embeddings for every chunk
embeddings = model.encode(chunks, show_progress_bar=True)


# ---------------------------
# New Chroma v0.6+ persistent client
# ---------------------------

# /**
#  * Initialize a ChromaDB persistent client.
#  *
#  * @type {chromadb.PersistentClient}
#  * @param {str} path - Directory where vector DB will be stored.
#  */
client = chromadb.PersistentClient(path=PERSIST_DIR)


# /**
#  * Create or load an existing Chroma collection.
#  * Collection: "peer-ai-table"
#  *
#  * @throws {NotFoundError} If collection does not exist.
#  * @returns {Collection} Chroma collection instance.
#  */
try:
    collection = client.get_collection("peer-ai-table")
except chromadb.errors.NotFoundError:
    collection = client.create_collection("peer-ai-table")


# /**
#  * Store documents, embeddings, and unique IDs inside ChromaDB.
#  *
#  * @param {list<string>} documents - Chunked text documents.
#  * @param {list<float[]>} embeddings - Vector embeddings for each chunk.
#  * @param {list<string>} ids - Unique string IDs for each chunk.
#  */
collection.add(
    documents=chunks,
    embeddings=embeddings.tolist() if hasattr(embeddings, "tolist") else embeddings,
    ids=[str(i) for i in range(len(chunks))]
)

print("PDF ingestion complete. Total chunks:", len(chunks))
print(f"Chroma DB persisted to: {PERSIST_DIR}")
