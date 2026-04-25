import json
import os
import uuid

import httpx
import chainlit as cl

BACKEND_URL = os.getenv("BACKEND_URL", "http://backend:8000")


@cl.on_chat_start
async def on_chat_start():
    cl.user_session.set("thread_id", str(uuid.uuid4()))
    await cl.Message(
        content=(
            "Hi! I'm the **Promtior Assistant**. "
            "Ask me anything about Promtior and I'll do my best to help."
        )
    ).send()


@cl.on_message
async def on_message(message: cl.Message):
    thread_id = cl.user_session.get("thread_id")

    response_msg = cl.Message(content="")
    await response_msg.send()

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            async with client.stream(
                "POST",
                f"{BACKEND_URL}/chat/stream",
                json={
                    "input": {"messages": [{"role": "user", "content": message.content}]},
                    "config": {"configurable": {"thread_id": thread_id}},
                },
                headers={"Accept": "text/event-stream"},
            ) as response:
                response.raise_for_status()
                async for line in response.aiter_lines():
                    if not line.startswith("data: "):
                        continue
                    data_str = line[6:].strip()
                    if not data_str or data_str == "[DONE]":
                        break
                    try:
                        chunk = json.loads(data_str)
                        # LangGraph streams node-level updates; extract from "agent" node
                        agent_output = chunk.get("agent", {})
                        messages = agent_output.get("messages", [])
                        if messages:
                            last_msg = messages[-1]
                            content = (
                                last_msg.get("content", "")
                                if isinstance(last_msg, dict)
                                else getattr(last_msg, "content", "")
                            )
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
