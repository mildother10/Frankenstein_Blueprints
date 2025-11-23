import os
from langchain_community.document_loaders import NotebookLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.tools import tool

NOTEBOOK_DIR = "mcp-research-crew/knowledge_base/dlai_notebooks"
DB_PATH = "mcp-research-crew/chroma_db_dlai"
COLLECTION_NAME = "dlai_notebooks"

embedding_function = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

def _get_retriever():
    vector_store = Chroma(
        persist_directory=DB_PATH,
        embedding_function=embedding_function,
        collection_name=COLLECTION_NAME
    )
    return vector_store.as_retriever(search_kwargs={"k": 5})

@tool("DLAI Knowledge Base Search Tool")
def search_dlai_knowledge_base(query: str) -> str:
    """
    Searches the private DeepLearning.AI (DLAI) knowledge base
    of Jupyter Notebooks for code snippets and technical explanations.
    """
    print(f"Tool: search_dlai_knowledge_base (Query: {query})")
    try:
        retriever = _get_retriever()
        docs = retriever.invoke(query)
        if not docs:
            return f"No relevant information found for: {query}"
        context = [f"--- Source: {d.metadata.get('source', 'N/A')} ---\n{d.page_content}" for d in docs]
        return "\n---\n".join(context)
    except Exception as e:
        if "does not exist" in str(e):
             return "Error: The DLAI knowledge base has not been initialized."
        return f"Error searching DLAI knowledge base: {e}"

def load_and_embed_notebooks():
    print("--- Starting DLAI Knowledge Base Setup ---")
    os.makedirs(NOTEBOOK_DIR, exist_ok=True)
    notebook_files = [os.path.join(NOTEBOOK_DIR, f) for f in os.listdir(NOTEBOOK_DIR) if f.endswith(".ipynb")]
    
    if not notebook_files:
        print(f"Warning: No .ipynb files found in {NOTEBOOK_DIR}. Creating dummy notebook.")
        dummy_path = os.path.join(NOTEBOOK_DIR, "dummy_notebook.ipynb")
        with open(dummy_path, 'w') as f:
            f.write('{"cells": [{"cell_type": "markdown", "source": "This is a test notebook."}], "metadata": {}, "nbformat": 4, "nbformat_minor": 4}')
        notebook_files = [dummy_path]

    all_docs = []
    for nb_path in notebook_files:
        loader = NotebookLoader(nb_path)
        docs = loader.load()
        for doc in docs: doc.metadata["source"] = nb_path
        all_docs.extend(docs)

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    split_docs = text_splitter.split_documents(all_docs)
    
    vector_store = Chroma.from_documents(
        documents=split_docs,
        embedding=embedding_function,
        persist_directory=DB_PATH,
        collection_name=COLLECTION_NAME
    )
    vector_store.persist()
    print("✅ --- DLAI Knowledge Base Setup Complete ---")
