from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.retrievers import BM25Retriever
from langchain_core.vectorstores import InMemoryVectorStore #mini vector store created in RAM only. Good for mini projects
from langchain_classic.retrievers import EnsembleRetriever #RRF
from dotenv import load_dotenv
import os

load_dotenv()

def embed_store_retrieve(documents: list, user_query:str):
    """Sets up an Ensemble Hybrid Search Retriever using BM25 (Keywords) 
    and HuggingFace local embeddings (Semantic Vector Search)."""

    #initialise huggingface local embedding model
    embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2",
    model_kwargs={
        "device": "cpu",
        "token": os.environ.get("HF_TOKEN") ,  # Replace with your Hugging Face access token
    },
)

    #Create a lightweight local Vector Store for semantic search
    vector_store = InMemoryVectorStore.from_documents(documents, embeddings)
    vector_retriever = vector_store.as_retriever(search_kwargs={"k": 5})

    #Create the BM25 Retriever for exact keyword matching
    bm25_retriever = BM25Retriever.from_documents(documents)
    bm25_retriever.k = 5

    #combining both bm25 and dense search into ensemble retriever
    ensemble_retriever = EnsembleRetriever(
        retrievers=[bm25_retriever, vector_retriever],
        weights=[0.5, 0.5]
    )

    #retrieve only most relevant documents for user query
    relevant_docs = ensemble_retriever.invoke(user_query)
    
    return relevant_docs