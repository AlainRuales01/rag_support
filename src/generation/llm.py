from functools import lru_cache
from langchain_google_genai import ChatGoogleGenerativeAI
from src.core.config import GEMINI_API_KEY

@lru_cache(maxsize=1)
def get_llm(model_name: str = 'Gemini 3.5 Flash Lite', max_output_tokens=1200) -> ChatGoogleGenerativeAI:
    return ChatGoogleGenerativeAI(
        model=model_name,
        temperature=0.1,
        google_api_key=GEMINI_API_KEY, 
        max_output_tokens=max_output_tokens
    )