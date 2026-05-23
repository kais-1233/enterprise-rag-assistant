from langchain_community.document_loaders import PyPDFLoader
import os

def load_all_documents():

    documents = []

    # Company PDFs
    company_folder = "company_data"

    for file in os.listdir(company_folder):

        if file.endswith(".pdf"):

            pdf_path = os.path.join(company_folder, file)

            loader = PyPDFLoader(pdf_path)

            docs = loader.load()

            documents.extend(docs)

    # User Uploaded PDFs
    upload_folder = "uploaded_docs"

    for file in os.listdir(upload_folder):

        if file.endswith(".pdf"):

            pdf_path = os.path.join(upload_folder, file)

            loader = PyPDFLoader(pdf_path)

            docs = loader.load()

            documents.extend(docs)

    return documents