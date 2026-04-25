from langchain.agents import create_agent
from langchain_openrouter import ChatOpenRouter
from config import config
from langgraph.checkpoint.memory import InMemorySaver
from langchain_core.messages import SystemMessage


# Model

model = ChatOpenRouter(
    model=config.MODEL,
    api_key=config.OPENROUTER_API_KEY,
    base_url=config.OPENROUTER_BASE_URL,
    temperature=0.5,
    streaming=True,
    max_tokens=25000,
    timeout=300
)

# Memory

checkpointer = InMemorySaver()

# System prompt

SYSTEM_PROMPT = SystemMessage(content="""You are a promtior assistant.

Your task is to answer questions based on the provided context and the information provided in the RAG.
If you don't know the answer, just say that you don't know, don't try to make up an answer.
""")

# Tools

tools = []

# Agent

agent = create_agent(
    model=model,
    checkpointer=checkpointer,
    system_prompt=SYSTEM_PROMPT,
    tools=tools
)