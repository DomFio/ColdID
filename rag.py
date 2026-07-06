# rag.py
# RAG (Retrieval-Augmented Generation) system for ColdIQ
# Loads documents from data/, chunks them, embeds them, and stores them in FAISS
# Agents query this to retrieve relevant context about the candidate

import os
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from config import DATA_PATH

# Global variable to cache the vector store once built
_vector_store = None

def build_vector_store():
    """
    Reads all .txt files from data/, splits them into chunks,
    embeds them, and stores them in a FAISS vector store.
    """
    documents = []

    # Read every .txt file in the data folder
    for filename in os.listdir(DATA_PATH):
        if filename.endswith(".txt"):
            filepath = os.path.join(DATA_PATH, filename)
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
                documents.append(content)

    if not documents:
        raise ValueError(f"No .txt files found in {DATA_PATH}. Add your resume and project writeups there.")

    # Combine all documents into one string, then split into chunks
    full_text = "\n\n".join(documents)

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50
    )
    chunks = text_splitter.split_text(full_text)

    # Embed the chunks and store them in FAISS
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
    vector_store = FAISS.from_texts(chunks, embeddings)

    return vector_store


def get_vector_store():
    """
    Returns the cached vector store, building it if it doesn't exist yet.
    """
    global _vector_store
    if _vector_store is None:
        _vector_store = build_vector_store()
    return _vector_store


def retrieve_context(query: str, k: int = 3) -> str:
    """
    Given a query string, retrieves the k most relevant chunks
    from the candidate's knowledge base.
    Returns them combined as a single string ready to insert into a prompt.
    """
    vector_store = get_vector_store()
    results = vector_store.similarity_search(query, k=k)

    context = "\n\n---\n\n".join([doc.page_content for doc in results])
    return context

def build_vector_store_from_text(text: str):
    """
    Builds a FAISS vector store from a string of text.
    Used when a user uploads their resume directly via the UI
    rather than reading from the data/ folder.
    """
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50
    )
    chunks = text_splitter.split_text(text)
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
    vector_store = FAISS.from_texts(chunks, embeddings)
    return vector_store


def set_vector_store(vector_store):
    """
    Allows the UI to inject a user uploaded vector store
    into the global cache so all agents use it for that session.
    """
    global _vector_store
    _vector_store = vector_store