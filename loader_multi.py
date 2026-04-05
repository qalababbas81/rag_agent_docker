import os
from langchain_community.document_loaders import PyPDFLoader,Docx2txtLoader

def load_all_docs(folder_path="docs"):

    if not os.path.exists(folder_path):
        raise ValueError(f"Folder '{folder_path}' does not exist")
    
    docs =[]
    for file_name in os.listdir(folder_path):
        file_path = os.path.join(folder_path,file_name)

        if not os.path.isfile(file_path):
         continue

        if file_name.lower().endswith(".pdf"):
            loader = PyPDFLoader(file_path)
            docs.extend(loader.load())

        elif file_name.lower().endswith(".docx"):
            loader = Docx2txtLoader(file_path)
            docs.extend(loader.load())
    return docs

