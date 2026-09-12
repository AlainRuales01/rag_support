from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

def chunk_splitter(docs : list[Document]):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=2400, chunk_overlap=400)
    return text_splitter.split_documents(docs)