import asyncio
from autogen_agentchat.agents._assistant_agent import AssistantAgent
from autogen_agentchat.agents._user_proxy_agent import UserProxyAgent
from autogen_agentchat.messages import TextMessage
from autogen_agentchat.base import Response
from autogen_core import CancellationToken

async def main():
    user = UserProxyAgent("You")
    token = CancellationToken()
    initial_msg = TextMessage(
        content="🚀 Success. AutoGen is now running from local source.",
        source="user"
    )
    # Use on_messages (as the new method) to start the conversation.
    response = await user.on_messages([initial_msg], token)
    print("UserProxyAgent returned:", response.chat_message.content)

if __name__ == '__main__':
    asyncio.run(main())
