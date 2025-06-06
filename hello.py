# hello.py  •  minimal sanity-check with local Ollama (mistral:latest)
import asyncio

from autogen_agentchat.agents import AssistantAgent
from autogen_ext.models.ollama import OllamaChatCompletionClient

async def main() -> None:
    # Point at your local Ollama server
    client = OllamaChatCompletionClient(model="mistral:latest")

    # One assistant backed by that client
    assistant = AssistantAgent(name="assistant", model_client=client)

    # Fire a one-shot task
    result = await assistant.run(task="Hi! What is 2 + 2?")
    # The final reply is always the last message in result.messages
    print("\n>>>", result.messages[-1].content, flush=True)

asyncio.run(main())
