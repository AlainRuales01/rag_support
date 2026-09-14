from functools import lru_cache

from langchain_google_genai import GoogleGenerativeAIEmbeddings
from src.core import GOOGLE_API_KEY

@lru_cache(maxsize=1)
def get_embedding(model_name: str = "models/gemini-embedding-001", api_key: str = GOOGLE_API_KEY, truncate_length: int = 768):
    """
    Returns the embeddings model to be used for generating embeddings.
    """
    if model_name in ["models/gemini-embedding-001", "models/gemini-embedding-002"]:
        if truncate_length <= 0:
            return GoogleGenerativeAIEmbeddings(model=model_name, api_key=api_key)
        else:
            return GoogleGenerativeAIEmbeddings(model=model_name, api_key=api_key, output_dimensionality=truncate_length)


    return None
