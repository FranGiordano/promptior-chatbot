import os
from langchain_openai import ChatOpenAI
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_retrieval_chain, create_history_aware_retriever
from langchain_community.document_loaders import WebBaseLoader

OPENROUTER_API_KEY = os.environ["OPENROUTER_API_KEY"]
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
MODEL = os.getenv("MODEL", "openai/gpt-4o-mini")
PROMTIOR_URL = os.getenv("PROMTIOR_URL", "https://www.promtior.ai")


def build_llm(streaming: bool = True) -> ChatOpenAI:
    return ChatOpenAI(
        model=MODEL,
        openai_api_key=OPENROUTER_API_KEY,
        openai_api_base=OPENROUTER_BASE_URL,
        streaming=streaming,
    )


def build_vectorstore() -> FAISS:
    loader = WebBaseLoader(PROMTIOR_URL)
    docs = loader.load()

    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)
    splits = splitter.split_documents(docs)

    embeddings = OpenAIEmbeddings(
        openai_api_key=OPENROUTER_API_KEY,
        openai_api_base=OPENROUTER_BASE_URL,
    )
    return FAISS.from_documents(splits, embeddings)


def build_chain():
    llm = build_llm()
    vectorstore = build_vectorstore()
    retriever = vectorstore.as_retriever(search_kwargs={"k": 4})

    # Reformulate the question to be standalone given chat history
    condense_prompt = ChatPromptTemplate.from_messages([
        MessagesPlaceholder("chat_history"),
        ("human", "{input}"),
        ("human", (
            "Given the conversation above, rewrite the follow-up question "
            "as a standalone question that includes all necessary context."
        )),
    ])
    history_aware_retriever = create_history_aware_retriever(llm, retriever, condense_prompt)

    qa_prompt = ChatPromptTemplate.from_messages([
        ("system", (
            "You are a helpful assistant for Promtior, an AI consulting company. "
            "Answer the user's question using only the context below. "
            "If the answer is not in the context, say you don't know.\n\n"
            "{context}"
        )),
        MessagesPlaceholder("chat_history"),
        ("human", "{input}"),
    ])
    combine_docs_chain = create_stuff_documents_chain(llm, qa_prompt)

    return create_retrieval_chain(history_aware_retriever, combine_docs_chain)
