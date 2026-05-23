import streamlit as st
import os

from utils.load_documents import load_all_documents
from utils.split_documents import split_documents
from utils.create_embeddings import get_embedding_model
from utils.vector_store import create_vector_store
from utils.retriever import get_retriever
from utils.llm_model import load_llm

# ------------------------------------
# PAGE CONFIG
# ------------------------------------

st.set_page_config(
    page_title="Enterprise RAG Assistant",
    layout="wide"
)

st.title("Enterprise Multi-PDF RAG Assistant")

# ------------------------------------
# FILE UPLOAD
# ------------------------------------

uploaded_files = st.file_uploader(
    "Upload PDF Files",
    type="pdf",
    accept_multiple_files=True
)

if uploaded_files:

    for file in uploaded_files:

        save_path = os.path.join("uploaded_docs", file.name)

        with open(save_path, "wb") as f:

            f.write(file.getbuffer())

    st.success("Files Uploaded Successfully")

# ------------------------------------
# LOAD DOCUMENTS
# ------------------------------------

documents = load_all_documents()

# ------------------------------------
# SPLIT DOCUMENTS
# ------------------------------------

chunks = split_documents(documents)

# ------------------------------------
# EMBEDDINGS
# ------------------------------------

embeddings = get_embedding_model()

# ------------------------------------
# VECTOR DATABASE
# ------------------------------------

vector_db = create_vector_store(chunks, embeddings)

# ------------------------------------
# RETRIEVER
# ------------------------------------

retriever = get_retriever(vector_db)

# ------------------------------------
# LOAD LLM
# ------------------------------------

llm = load_llm()

# ------------------------------------
# CHAT HISTORY
# ------------------------------------

if "messages" not in st.session_state:

    st.session_state.messages = []

# ------------------------------------
# USER QUESTION
# ------------------------------------

query = st.chat_input("Ask Question From Documents")

if query:

    # -----------------------------
    # VALIDATE QUERY
    # -----------------------------

    if len(query.strip()) < 3:

        st.warning("Please ask meaningful question.")
        st.stop()

    # -----------------------------
    # STORE USER MESSAGE
    # -----------------------------

    st.session_state.messages.append({
        "role": "user",
        "content": query
    })

    # -----------------------------
    # RETRIEVE DOCUMENTS
    # -----------------------------

    retrieved_docs = retriever.invoke(query)

    # -----------------------------
    # FILTER RELEVANT DOCS
    # -----------------------------

    relevant_context = []

    for doc in retrieved_docs:

        content = doc.page_content.strip()

        if len(content) > 50:

            relevant_context.append(doc)

    # -----------------------------
    # IF DOCUMENTS FOUND
    # -----------------------------

    if len(relevant_context) > 0:

        # -------------------------
        # CREATE CONTEXT
        # -------------------------

        context = "\n\n".join([

            f"""
            SOURCE TYPE:
            {"USER UPLOADED DOCUMENT" if "uploaded_docs" in doc.metadata.get("source", "") else "COMPANY DOCUMENT"}

            CONTENT:
            {doc.page_content}
            """

            for doc in relevant_context
        ])

        # -------------------------
        # ENTERPRISE PROMPT
        # -------------------------

        prompt = f"""
        You are an Enterprise RAG AI Assistant.

        STRICT INSTRUCTIONS:

        1. Answer ONLY from the provided document context.

        2. If the user uploaded documents,
           prioritize answers from uploaded user documents first.

        3. If information exists in uploaded documents,
           answer strictly from those documents only.

        4. Do NOT use outside knowledge
           when relevant document information exists.

        5. Keep answers professional,
           concise, and clean.

        6. Do NOT hallucinate or make up information.

        7. Do NOT mention document sources,
           filenames, or retrieved chunks
           unless the user explicitly asks.

        8. If the answer is not available
           in the provided documents,
           reply exactly:

           "Information not found in uploaded documents."

        DOCUMENT CONTEXT:
        {context}

        USER QUESTION:
        {query}

        ANSWER:
        """

        # -------------------------
        # LLM RESPONSE
        # -------------------------

        response = llm.invoke(prompt)

        answer = response.content

    # -----------------------------
    # FALLBACK MODE
    # -----------------------------

    else:

        fallback_prompt = f"""
        Answer this question using your general knowledge.

        Question:
        {query}
        """

        response = llm.invoke(fallback_prompt)

        answer = response.content

        answer += "\n\n⚠️ Relevant information was not found in uploaded documents."

    # -----------------------------
    # STORE ASSISTANT RESPONSE
    # -----------------------------

    st.session_state.messages.append({
        "role": "assistant",
        "content": answer
    })

# ------------------------------------
# DISPLAY CHAT
# ------------------------------------

for msg in st.session_state.messages:

    with st.chat_message(msg["role"]):

        st.write(msg["content"])

# ------------------------------------
# SHOW SOURCES
# ------------------------------------

show_sources = st.checkbox("Show Document Sources")

if query and show_sources:

    st.subheader("Document Sources")

    for i, doc in enumerate(relevant_context):

        with st.expander(f"Source {i+1}"):

            if "source" in doc.metadata:

                st.write("File:", doc.metadata["source"])

            if "page" in doc.metadata:

                st.write("Page:", doc.metadata["page"] + 1)

            st.write(doc.page_content)