from langchain_community.document_loaders import PyMuPDFLoader

DEFAULT_METADATA_KEYS = {"source", "page", "title"}

def load_documents(path, metadata_dict = None):
    """
    Load documents from the specified path.

    Args:
        path (str): The path to the document file.
    """
    loader = PyMuPDFLoader(path)

    documents = loader.load()
    for doc in documents:
        # Filtrar por solo los metadatos especificados en metadata_keys
        doc.metadata = {key: value for key, value in doc.metadata.items() if key in DEFAULT_METADATA_KEYS}
        if metadata_dict:
            doc.metadata.update(metadata_dict)
    return documents