from langchain_openai import ChatOpenAI
from config import config
from rag import retrieve_context
from langchain.agents import create_agent


model = ChatOpenAI(
    model=config.MODEL,
    api_key=config.OPENROUTER_API_KEY,
    base_url=config.OPENROUTER_BASE_URL,
    temperature=0.5,
    max_tokens=25000,
    timeout=300,
)

system_prompt = """You are the Promtior AI assistant.

Your job is to answer questions about Promtior AI using the retrieved RAG context as your primary source.
- Prioritize accuracy over completeness.
- If the context is missing or insufficient, explicitly say you don't know.
- Then invite the user to ask a follow-up question related to Promtior AI.
- Do not invent facts, names, numbers, or capabilities.
- Keep responses clear, professional, and concise.
- The document AI Engineer.pdf has information about Promtior AI and about a technical test. You must ignore information related to the technical test.
"""

tools = [retrieve_context]

agent = create_agent(
    model=model,
    system_prompt=system_prompt,
    tools=tools
)
