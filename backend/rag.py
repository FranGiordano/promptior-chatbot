from langchain_openai import OpenAIEmbeddings
from langchain_core.vectorstores import InMemoryVectorStore
from config import config
from langchain_community.document_loaders import WebBaseLoader, PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.tools import tool


# Setup embeddings and vector store

embeddings = OpenAIEmbeddings(
    model="openai/text-embedding-ada-002",
    openai_api_key=config.OPENROUTER_API_KEY,
    openai_api_base=config.OPENROUTER_BASE_URL
)

vector_store = InMemoryVectorStore(embeddings)

# Setup Web document loader

web_loader = WebBaseLoader(
    web_paths=(
        config.PROMTIOR_URL,
        config.PROMTIOR_URL + "/service",
        config.PROMTIOR_URL + "/use-cases"
    ),
)
web_docs = web_loader.load()

# Setup PDF document loader

pdf_loader = PyPDFLoader(
    "public/AI Engineer.pdf"
)
pdf_docs = pdf_loader.load()

docs = web_docs + pdf_docs

# Split document

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,  # chunk size (characters)
    chunk_overlap=200,  # chunk overlap (characters)
    add_start_index=True,  # track index in original document
)
all_splits = text_splitter.split_documents(docs)

# Store document on vector_storage

document_ids = vector_store.add_documents(documents=all_splits)

# Tool Definition

@tool(response_format="content_and_artifact")
def retrieve_context(query: str):
    """Retrieve information to help answer a query."""
    retrieved_docs = vector_store.similarity_search(query, k=2)
    serialized = "\n\n".join(
        (f"Source: {doc.metadata}\nContent: {doc.page_content}")
        for doc in retrieved_docs
    )
    return serialized, retrieved_docs
