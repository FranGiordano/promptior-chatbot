import os
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from langchain_core.messages import HumanMessage, AIMessage
from chain import build_chain

app = FastAPI()
chain = build_chain()


class ChatRequest(BaseModel):
    message: str
    history: list[dict] = []


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/chat")
async def chat(request: ChatRequest):
    history = [
        HumanMessage(content=m["content"]) if m["role"] == "user"
        else AIMessage(content=m["content"])
        for m in request.history[:-1]  # exclude the last user message, sent separately
    ]

    async def generate():
        async for chunk in chain.astream({
            "question": request.message,
            "chat_history": history,
        }):
            if hasattr(chunk, "content"):
                yield chunk.content
            elif isinstance(chunk, str):
                yield chunk

    return StreamingResponse(generate(), media_type="text/plain")
