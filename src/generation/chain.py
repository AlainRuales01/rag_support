from src.generation.prompt import SUPPORT_PROMPT
from src.generation.llm import get_llm
from src.retrieval.vectorstore import get_vectorstore
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_core.documents import Document

def build_rag_chain(input_data: dict = None):
    '''
    Main function to build a RAG (Retrieval-Augmented Generation) chain for question answering.
    This function constructs a chain that retrieves relevant documents based on the provided filters and generates a response using a language model, 
    following the rules and format specified in the SUPPORT_SYSTEM_PROMPT.
    '''
    prompt = SUPPORT_PROMPT
    llm =  get_llm()
    filters = input_data.get("filters", {})
    retriever = get_vectorstore().as_retriever(
        search_type="similarity_score_threshold",
        search_kwargs={"k": 5, "score_threshold": 0.65, "filter": filters}
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
    docs_text = "\n\n".join(doc.page_content for doc in docs)
    print("Retrieved documents:\n", docs_text)
    return docs_text