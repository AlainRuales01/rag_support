import os
import random
import time

from anyio import Path
from langchain_core.load import dumps


from src.ingestion.splitters import chunk_splitter
from src.ingestion.loader import load_documents
from src.retrieval.vectorstore import get_vectorstore




class IngestionPipeline:
    def __init__(self):
        """
        Initialize the ingestion pipeline.
        """
        pass

    def run_ingestion(self, data_source, metadata_dict=None, batch_size=20, wait_time=30.0, max_retries: int = 5):
        """
        Run the ingestion pipeline to load and process documents.

        Returns:
            list: A list of processed documents.
        """
        documents = load_documents(data_source, metadata_dict)
        documents = chunk_splitter(documents)

        save_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data", "processed"))
        json_documents = dumps([d for d in documents], pretty=True)
        doc_name = f"{os.path.basename(data_source).split('.')[0]}.json"
        with open(f"{save_path}/{doc_name}", "w", encoding="utf-8") as f:
            f.write(json_documents)
        print(f"Documents saved to {save_path}/{doc_name}")
        vectorstore = get_vectorstore()
        for offset in range(0, len(documents), batch_size):
            batch = documents[offset:offset + batch_size]
            for attempt in range(1, max_retries + 1):
                try:
                    print(f'Processing batch {offset // batch_size + 1} of {len(documents) // batch_size + 1}, attempt {attempt} of {max_retries} for batch with offset {offset}')
                    vectorstore.add_documents(batch)
                    break
                except Exception as e:
                    if "429" in str(e) or "ResourceExhausted" in str(e):
                        wait = min(120, 30 * 2 ** (attempt - 1)) + random.uniform(0, 5)
                        print(f"Límite de tasa alcanzado. Esperando {wait}s antes de reintentar...")
                        time.sleep(wait)
                    else:
                        raise e
            else:
                raise RuntimeError(f"Fallo definitivo al procesar el lote con offset {offset}")
            if offset + batch_size < len(documents):
                time.sleep(wait_time)
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
