from langchain_core.documents import Document


def text_split(docs: list[Document] , chunk_size: int = 1000, chunk_overlap: int = 200) -> list:
    """Split text into chunks with specified size and overlap."""
    from langchain.text_splitter import RecursiveCharacterTextSplitter

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap
    )
    splits = text_splitter.split_documents(docs)
    return splits