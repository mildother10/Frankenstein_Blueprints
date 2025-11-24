import os
import chromadb
from langchain_community.vectorstores import Chroma
# --- THIS IS THE FIX ---
from langchain_huggingface import HuggingFaceEmbeddings
# --- (Old line was: from langchain_community.embeddings import SentenceTransformerEmbeddings) ---
from langchain_community.document_loaders import NotebookLoader

# --- v0.4.24 COMPATIBLE VERSION ---

# Define the path for the persistent database
persist_directory = "chroma_db_dlai"
# --- THIS IS THE FIX ---
# Use the new HuggingFaceEmbeddings class
embedding_function = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
# --- (Old line was: SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")) ---

# Define the path to the knowledge base
knowledge_base_path = "./mcp-research-crew/knowledge_base"

def load_and_embed_notebooks():
    """
    Loads .ipynb notebooks, splits them, and embeds them into a Chroma vector store.
    This version is compatible with chromadb v0.4.x.
    """
    print("--- Starting DLAI Knowledge Base Setup (v0.4.x compatible) ---")
    
    if os.path.exists(persist_directory):
        print(f"--- Found old DB. Exorcising '{persist_directory}'... ---")
        import shutil
        shutil.rmtree(persist_directory)
        print("--- Old DB successfully deleted. ---")

    notebook_files = [f for f in os.listdir(knowledge_base_path) if f.endswith('.ipynb')]
    
    if not notebook_files:
        print("--- No notebooks found to load. Skipping RAG setup. ---")
        return

    print(f"--- Found {len(notebook_files)} notebooks. Loading... ---")
    
    docs = []
    for notebook_file in notebook_files:
        loader = NotebookLoader(
            os.path.join(knowledge_base_path, notebook_file),
            include_outputs=False,
            remove_code_prompts=True,
            remove_hidden_cells=True
        )
        docs.extend(loader.load())

    if not docs:
        print("--- Notebooks were empty or failed to load. Skipping RAG setup. ---")
        return

    print(f"--- Notebooks loaded. Embedding {len(docs)} documents... ---")

    vector_store = Chroma.from_documents(
        documents=docs, 
        embedding=embedding_function,
        persist_directory=persist_directory
    )
    
    print("--- ✅ DLAI Knowledge Base Embedded Successfully. ---")
    return vector_store.as_retriever()

def search_dlai_knowledge_base(query: str) -> str:
    """
    Searches the DeepLearning.AI knowledge base for a given query.
    """
    print(f"--- 🧠 RAG Tool: Searching DLAI KB for: {query} ---")
    
    client = chromadb.PersistentClient(path=persist_directory)
    # --- THIS IS THE FIX ---
    embedding_func = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    # --- (Old line was: SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")) ---
    
    vector_store = Chroma(
        client=client,
        embedding_function=embedding_func,
        collection_name="langchain" # Default collection name
    )
    
    results = vector_store.similarity_search(query, k=3)
    
    if not results:
        return "No relevant information found in the DLAI knowledge base."
    
    context = "\n\n---\n\n".join([doc.page_content for doc in results])
    return f"Found relevant context in DLAI knowledge base:\n\n{context}"
