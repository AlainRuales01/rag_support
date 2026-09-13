import os

from pathlib import Path
import sys
from src.ingestion import ingest_data

PDF_PATH = os.path.join(Path(__file__).resolve().parent.parent, "data", "raw")
def run_ingestion():
    """
    Run the ingestion process for PDF files in the specified directory.
    """
    print(f"Starting ingestion process for PDF files in: {PDF_PATH}")
    documents = []
    for root, _, files in os.walk(PDF_PATH):
        for file in files:
            if file.endswith(".pdf"):
                metadata_dict = {"category" : root.split(os.sep)[-1], "brand" : file.split("-")[0], "model" : file.split("-")[1]}
                file_path = os.path.join(root, file)
                documents.append((file_path, metadata_dict))

    documents = ingest_data(documents)

    for doc in documents:
        print(f"Length of document: {len(doc)}")

if __name__ == "__main__":
    run_ingestion()
                