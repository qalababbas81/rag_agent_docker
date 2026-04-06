from langchain_community.vectorstores import Chroma
from langchain_ollama import OllamaEmbeddings #offline Embeddings

def create_vectorestore(chunks):
    #embeddings = OllamaEmbeddings(model="llama3.1:latest")  # offline
    embeddings = OllamaEmbeddings(
        model="llama3.1:8b",
        base_url="http://ollama:11434",
        num_predict=100
    )
    db = Chroma.from_documents(chunks,embeddings)
    return db
