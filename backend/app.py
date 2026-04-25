from agent import agent
from fastapi import FastAPI
from langserve import add_routes


app = FastAPI(
    title="Promtior",
    description="Promtior chatbot",
    version="0.1.0",
)

add_routes(
    app=app,
    runnable=agent,
    path="/chat",
)
