import json
import os

import httpx
import chainlit as cl

BACKEND_URL = os.getenv("BACKEND_URL", "http://backend:8000")


@cl.on_chat_start
async def on_chat_start():
    cl.user_session.set("history", [])
    await cl.Message(
        content=(
            "Hi! I'm the **Promtior Assistant**. "
            "Ask me anything about Promtior and I'll do my best to help."
        )
    ).send()


@cl.on_message
async def on_message(message: cl.Message):
    history: list = cl.user_session.get("history", [])

    messages = history + [{"type": "human", "content": message.content}]

    response_msg = cl.Message(content="")
    await response_msg.send()

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            async with client.stream(
                "POST",
                f"{BACKEND_URL}/chat/stream",
                json={
                    "input": {"messages": messages},
                    "config": {},
                },
                headers={"Accept": "text/event-stream"},
            ) as response:
                response.raise_for_status()
                current_event = None
                async for line in response.aiter_lines():
                    if line.startswith("event: "):
                        current_event = line[7:].strip()
                        continue
                    if current_event != "data" or not line.startswith("data: "):
                        continue
                    data_str = line[6:].strip()
                    if not data_str:
                        continue
                    try:
                        chunk = json.loads(data_str)
                        # LCEL streams AIMessageChunk — content is at the top level
                        content = chunk.get("content", "")
                        if content:
                            await response_msg.stream_token(content)
                    except json.JSONDecodeError:
                        pass
    except httpx.ConnectError:
        response_msg.content = (
            "Sorry, I can't reach the backend right now. Please try again later."
        )
    except httpx.HTTPStatusError as exc:
        response_msg.content = f"Backend error {exc.response.status_code}. Please try again."

    await response_msg.update()
    history.append({"type": "human", "content": message.content})
    history.append({"type": "ai", "content": response_msg.content})
    cl.user_session.set("history", history)
