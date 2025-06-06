import asyncio
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.messages import TextMessage
from autogen_core import CancellationToken
from autogen_ext.models.ollama import OllamaChatCompletionClient
from ollama import Options

async def main():
    print("Initializing agents...")
    
    # Configure GPU options
    gpu_options = Options(
        num_gpu=1,  # Use 1 GPU
        num_thread=4,  # Number of CPU threads to use
        num_ctx=4096,  # Context window size
        num_batch=512,  # Batch size for processing
        num_keep=32,  # Number of tokens to keep from the input
        temperature=0.7,  # Sampling temperature
        top_k=40,  # Top-k sampling
        top_p=0.9  # Top-p sampling
    )
    
    client = OllamaChatCompletionClient(
        model="mistral:latest",
        options=gpu_options,
        host="http://localhost:11434"  # Use the default Ollama port
    )

    # Create the coder agent
    coder = AssistantAgent(
        name="coder",
        model_client=client,
        description="A coding expert that can write and explain code",
        system_message="You are a coding expert. Write clear, efficient, and well-documented code. Focus on performance and readability."
    )
    
    # Create the critic agent
    critic = AssistantAgent(
        name="critic",
        model_client=client,
        description="A code reviewer that can analyze and improve code",
        system_message="You are a code reviewer. Analyze code for efficiency, readability, and best practices. Pay special attention to time and space complexity."
    )

    print("\nStarting the conversation...")
    print("The coder will write code, and the critic will review it.")
    
    # First, let's ask the coder to write code
    print("\nAsking the coder to write code...")
    initial_message = TextMessage(
        content="""Write a Python function that finds the longest common subsequence (LCS) of two strings. 
        The function should be efficient and handle edge cases. Include example usage and time complexity analysis.""",
        source="user"
    )
    
    # Get response from coder
    coder_response = await coder.on_messages([initial_message], CancellationToken())
    print(f"\nCoder's response: {coder_response.chat_message.content}")

    # Now let's ask the critic to review the code
    print("\nAsking the critic to review the code...")
    review_message = TextMessage(
        content=f"""Please review this code and suggest improvements. Focus on:
        1. Time and space complexity
        2. Edge case handling
        3. Code readability and documentation
        4. Potential optimizations
        
        Here's the code to review:
        {coder_response.chat_message.content}""",
        source="user"
    )
    
    # Get response from critic
    critic_response = await critic.on_messages([review_message], CancellationToken())
    print(f"\nCritic's response: {critic_response.chat_message.content}")

    # Let the coder respond to the critic's feedback
    print("\nAsking the coder to respond to the feedback...")
    feedback_message = TextMessage(
        content=f"""The critic provided the following feedback:
        {critic_response.chat_message.content}
        
        Please improve the code based on this feedback, addressing all the points mentioned.""",
        source="user"
    )
    
    # Get final response from coder
    final_response = await coder.on_messages([feedback_message], CancellationToken())
    print(f"\nCoder's final response: {final_response.chat_message.content}")

if __name__ == "__main__":
    asyncio.run(main()) 