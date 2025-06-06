"""
QA Agent implementation.
"""

from typing import Dict, Any
from langchain.agents import AgentExecutor
from langchain.prompts import ChatPromptTemplate
import logging

logger = logging.getLogger(__name__)

class QAAgent:
    def __init__(self, llm, conversation_manager=None):
        self.llm = llm
        self.conversation_manager = conversation_manager
        
        # Define the QA's prompt template
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a QA agent responsible for quality assurance and review. Your role is to:
1. ANALYZE the implementation and requirements
2. EVALUATE the quality and completeness
3. IDENTIFY any issues or improvements
4. DECIDE if the implementation meets standards
5. EXPLAIN your findings

Follow this structured thinking process:
ANALYZE: What are the requirements and what was implemented?
EVALUATE: How well does the implementation meet the requirements?
IDENTIFY: What issues or improvements are needed?
DECIDE: Does the implementation meet quality standards?
EXPLAIN: Document your findings and recommendations

Always provide your thought process in this format:
ANALYZE: [Your analysis]
EVALUATE: [Your evaluation]
IDENTIFY: [Issues and improvements]
DECIDE: [Your decision]
EXPLAIN: [Your explanation]

Focus on providing detailed, actionable feedback."""),
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
        """Run the QA agent on the given state."""
        try:
            message = state.get("message", "")
            formatted_prompt = self.prompt.format_prompt(message=message)
            logger.info(f"[QAAgent] Formatted prompt: {formatted_prompt.to_string()}")
            try:
                response = self.agent.invoke(formatted_prompt.to_string())
                logger.info(f"[QAAgent] Agent response: {response}")
                output = response.get("output", "") if isinstance(response, dict) else str(response)
                thought_process = ""
                sections = ["ANALYZE:", "EVALUATE:", "IDENTIFY:", "DECIDE:", "EXPLAIN:"]
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
                logger.error(f"[QAAgent] Agent invoke error: {e}")
                state["status"] = "error"
                state["feedback"] = f"Error in QA agent: {str(e)}"
                state["thought_process"] = "Error occurred during processing"
                return state
        except Exception as e:
            logger.error(f"[QAAgent] Error in QA agent: {str(e)}")
            state["status"] = "error"
            state["feedback"] = f"Error in QA agent: {str(e)}"
            state["thought_process"] = "Error occurred during processing"
            return state 