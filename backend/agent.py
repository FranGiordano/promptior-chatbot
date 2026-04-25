from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI
from config import config


model = ChatOpenAI(
    model=config.MODEL,
    api_key=config.OPENROUTER_API_KEY,
    base_url=config.OPENROUTER_BASE_URL,
    temperature=0.5,
    max_tokens=25000,
    timeout=300,
)

prompt = ChatPromptTemplate.from_messages([
    ("system", """You are a promtior assistant.

Your task is to answer questions related to Promtior AI based on the information provided in the RAG.
If you don't know the answer, just say that you don't know, and invite the user to ask a follow-up question related to Promtior AI.
"""),
    MessagesPlaceholder(variable_name="messages"),
])

chain = prompt | model
