import time

from src.ingestion.splitters import chunk_splitter
from src.ingestion.loader import load_documents
from src.retrieval.vectorstore import get_vectorstore


class IngestionPipeline:
    def __init__(self):
        """
        Initialize the ingestion pipeline.
        """
        pass

    def run_ingestion(self, data_source, metadata_dict=None, batch_size=50, wait_time=3.0, max_retries: int = 5):
        """
        Run the ingestion pipeline to load and process documents.

        Returns:
            list: A list of processed documents.
        """
        documents = load_documents(data_source, metadata_dict)
        documents = chunk_splitter(documents)
        vectorstore = get_vectorstore()
        for offset in range(0, len(documents), batch_size):
            batch = documents[offset:offset + batch_size]
            # Wait the specified time before processing the next batch to avoid rate limiting
            # Manejo de reintentos con respaldo exponencial (Exponential Backoff)
            for attempt in range(1, max_retries + 1):
                try:
                    print(f"Procesando lote con offset {offset} (Intento {attempt}/{max_retries})...")
                    vectorstore.add_documents(batch)
                    break 
                except Exception as e:
                    if "429" in str(e) or "ResourceExhausted" in str(e):
                        wait = 2 ** attempt * 5
                        print(f"Límite de tasa alcanzado. Esperando {wait}s antes de reintentar...")
                        time.sleep(wait)
                    else:
                        raise e
            else:
                raise RuntimeError(f"Fallo definitivo al procesar el lote con offset {offset}")
            time.sleep(wait_time) # Wait before processing the next batch
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
        print(f"Ingesting data from source: {source[0]} with metadata: {source[1]}")
        document.append(ingest.run_ingestion(source[0], source[1]))    
    return document
