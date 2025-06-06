"""
Worker Agent implementation.
"""

from typing import Dict, Any
from langchain.agents import AgentExecutor
from langchain.prompts import ChatPromptTemplate
import logging

logger = logging.getLogger(__name__)

class WorkerAgent:
    def __init__(self, llm, conversation_manager=None):
        self.llm = llm
        self.conversation_manager = conversation_manager
        
        # Define the Worker's prompt template
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a Worker agent responsible for implementing and executing tasks. Your role is to:
1. ANALYZE the task requirements and understand what needs to be done
2. PLAN the implementation steps
3. EXECUTE the plan
4. VERIFY the results
5. EXPLAIN your work

Follow this structured thinking process:
ANALYZE: What are the specific requirements and constraints?
PLAN: What steps will you take to implement this?
EXECUTE: Implement the solution
VERIFY: Check if the implementation meets the requirements
EXPLAIN: Document your work and reasoning

Always provide your thought process in this format:
ANALYZE: [Your analysis]
PLAN: [Your plan]
EXECUTE: [Your implementation]
VERIFY: [Your verification]
EXPLAIN: [Your explanation]

Focus on delivering high-quality, well-documented solutions."""),
            ("human", "{message}")
        ])
        
        # Create the agent executor with the prompt
        self.agent = AgentExecutor.from_agent_and_tools(
            agent=self.llm,
            tools=[],
            verbose=True,
            handle_parsing_errors=True
        )
    
    def run(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Run the Worker agent on the given state."""
        try:
            message = state.get("message", "")
            formatted_prompt = self.prompt.format_prompt(message=message)
            logger.info(f"[WorkerAgent] Formatted prompt: {formatted_prompt.to_string()}")
            try:
                response = self.agent.invoke(formatted_prompt.to_string())
                logger.info(f"[WorkerAgent] Agent response: {response}")
                output = response.get("output", "") if isinstance(response, dict) else str(response)
                thought_process = ""
                sections = ["ANALYZE:", "PLAN:", "EXECUTE:", "VERIFY:", "EXPLAIN:"]
                for section in sections:
                    if section in output:
                        start = output.find(section)
                        end = output.find("\n\n", start) if "\n\n" in output[start:] else len(output)
                        thought_process += output[start:end].strip() + "\n\n"
                state["feedback"] = output
                state["thought_process"] = thought_process.strip()
                state["status"] = "done"
                return state
            except Exception as e:
                logger.error(f"[WorkerAgent] Agent invoke error: {e}")
                state["status"] = "error"
                state["feedback"] = f"Error in Worker agent: {str(e)}"
                state["thought_process"] = "Error occurred during processing"
                return state
        except Exception as e:
            logger.error(f"[WorkerAgent] Error in Worker agent: {str(e)}")
            state["status"] = "error"
            state["feedback"] = f"Error in Worker agent: {str(e)}"
            state["thought_process"] = "Error occurred during processing"
            return state 