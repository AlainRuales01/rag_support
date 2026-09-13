from src.ingestion.splitters import chunk_splitter
from src.ingestion.loader import load_documents
from src.retrieval.vectorstore import get_vectorstore


class IngestionPipeline:
    def __init__(self):
        """
        Initialize the ingestion pipeline.
        """
        pass

    def run_ingestion(self, data_source, metadata_dict=None):
        """
        Run the ingestion pipeline to load and process documents.

        Returns:
            list: A list of processed documents.
        """
        documents = load_documents(data_source, metadata_dict)
        documents = chunk_splitter(documents)
        documents = documents[:10]  # Limit to the first 10 documents for testing
        vector_store = get_vectorstore()
        vector_store.add_documents(documents)
        return documents




def ingest_data(data_source : list[tuple[str, dict]]):
    """
    Ingest data from the specified data source.

    Args:
        data_source (str): The path or URL of the data source.

    Returns:
        pd.DataFrame: A DataFrame containing the ingested data.
    """
    # Implementation for ingesting data goes here
    ingest = IngestionPipeline()
    document = []
    for source in data_source:
        document.append(ingest.run_ingestion(source[0], source[1]))    
    return document
