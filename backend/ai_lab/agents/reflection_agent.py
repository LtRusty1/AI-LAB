"""
Reflection Agent implementation.
"""

from typing import Dict, Any
from langchain.agents import AgentExecutor
from langchain.prompts import ChatPromptTemplate
import logging

logger = logging.getLogger(__name__)

class ReflectionAgent:
    def __init__(self, llm, conversation_manager=None):
        self.llm = llm
        self.conversation_manager = conversation_manager
        
        # Define the Reflection's prompt template
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a Reflection agent responsible for self-reflection and improvement. Your role is to:
1. ANALYZE the current state and process
2. EVALUATE what worked and what didn't
3. IDENTIFY areas for improvement
4. SUGGEST specific improvements
5. EXPLAIN your insights

Follow this structured thinking process:
ANALYZE: What was the process and outcome?
EVALUATE: What worked well and what didn't?
IDENTIFY: What could be improved?
SUGGEST: What specific improvements would you recommend?
EXPLAIN: Document your insights and reasoning

Always provide your thought process in this format:
ANALYZE: [Your analysis]
EVALUATE: [Your evaluation]
IDENTIFY: [Areas for improvement]
SUGGEST: [Your suggestions]
EXPLAIN: [Your explanation]

Focus on providing actionable insights for continuous improvement."""),
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
        """Run the Reflection agent on the given state."""
        try:
            message = state.get("message", "")
            formatted_prompt = self.prompt.format_prompt(message=message)
            logger.info(f"[ReflectionAgent] Formatted prompt: {formatted_prompt.to_string()}")
            try:
                response = self.agent.invoke(formatted_prompt.to_string())
                logger.info(f"[ReflectionAgent] Agent response: {response}")
                output = response.get("output", "") if isinstance(response, dict) else str(response)
                thought_process = ""
                sections = ["ANALYZE:", "EVALUATE:", "IDENTIFY:", "SUGGEST:", "EXPLAIN:"]
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
                logger.error(f"[ReflectionAgent] Agent invoke error: {e}")
                state["status"] = "error"
                state["feedback"] = f"Error in Reflection agent: {str(e)}"
                state["thought_process"] = "Error occurred during processing"
                return state
        except Exception as e:
            logger.error(f"[ReflectionAgent] Error in Reflection agent: {str(e)}")
            state["status"] = "error"
            state["feedback"] = f"Error in Reflection agent: {str(e)}"
            state["thought_process"] = "Error occurred during processing"
            return state 