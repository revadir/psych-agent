"""
Script to ingest DSM-5-TR PDF and build the vector database.
Moved from root directory for production organization.
"""

import os
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma

# Configuration
DATA_PATH = "data/DSM5-TR.pdf"
DB_PATH = "vector_db"


def build_vector_store():
    """Build the vector store from the DSM-5-TR PDF."""
    # 1. Load PDF
    loader = PyMuPDFLoader(DATA_PATH)
    docs = loader.load()

    # 2. Chunking (optimized for psychiatric criteria)
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=150)
    chunks = text_splitter.split_documents(docs)

    # 3. Embedding (runs locally on your Air)
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

    # 4. Create and persist the DB
    vector_db = Chroma.from_documents(
        documents=chunks, embedding=embeddings, persist_directory=DB_PATH
    )
    print(f"Index complete! Stored {len(chunks)} chunks in {DB_PATH}")


if __name__ == "__main__":
    build_vector_store()
