from langchain_text_splitters import RecursiveCharacterTextSplitter
## for single document
# def split_docs(docs):
#     splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
#     chunks = splitter.split_documents(docs)
#     return chunks

def split_docs(docs,chunk_size=250, chunk_overlap=40):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap
        )
    chunks = splitter.split_documents(docs)
    return chunks