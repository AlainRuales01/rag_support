from src.generation.prompt import SUPPORT_PROMPT
from src.generation.llm import get_llm
from src.retrieval.vectorstore import get_vectorstore
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_core.documents import Document

def build_rag_chain(llm):
    prompt = SUPPORT_PROMPT
    retriever = get_vectorstore().as_retriever(
        search_type="similarity_score_threshold",
        search_kwargs={"k": 5, "score_threshold": 0.65}
    )

    chain = (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )

    return chain

def format_docs(docs: list[Document]) -> str:
    if not docs:
        return "No se encontró información relevante."
    return "\n\n".join(doc.page_content for doc in docs)