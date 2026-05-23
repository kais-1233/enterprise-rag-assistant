from langchain_community.vectorstores import Chroma

def create_vector_store(chunks, embeddings):

    vector_db = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory="chroma_db"
    )

    return vector_db