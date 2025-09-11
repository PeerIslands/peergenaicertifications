

def load_pdf(file_path: str):
    """Load a PDF file and return its documents."""
    from langchain.document_loaders import PyPDFLoader
    # Validate file extension
    if not file_path.endswith('.pdf'):
        raise ValueError("The file must be a PDF.")
    loader = PyPDFLoader(file_path)
    documents = loader.load()
    return documents

def load_txt(file_path: str):
    """Load a text file and return its documents."""
    from langchain.document_loaders import TextLoader
    loader = TextLoader(file_path)
    documents = loader.load()
    return documents