from src.core import PINECONE_API_KEY
from langchain_pinecone import PineconeVectorStore
from pinecone import Pinecone
from src.retrieval.embeddings import get_embedding


def get_vectorstore():
    """
    Returns the vectorstore to be used for storing and retrieving embeddings.
    """
    embedding = get_embedding()
    if embedding is None:
        raise ValueError("No valid embedder found. Please check the model name.")

    # Initialize Pinecone
    return PineconeVectorStore(index_name="test", embedding=embedding, pinecone_api_key=PINECONE_API_KEY)