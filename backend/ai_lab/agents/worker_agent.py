"""
Worker Agent implementation.
"""

from typing import Dict, Any
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
            ("human", "{context}\n\nTask: {message}")
        ])
    
    def run(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Run the Worker agent on the given state."""
        try:
            message = state.get("message", "")
            session_id = state.get("session_id", "")
            
            # Get conversation context if available
            context = ""
            if self.conversation_manager and session_id:
                context = self.conversation_manager.get_context(session_id)
            
            # Create the formatted prompt
            formatted_prompt = self.prompt.format_messages(
                context=context,
                message=message
            )
            
            logger.info(f"[WorkerAgent] Processing task: {message}")
            
            # Get response from LLM
            response = self.llm.invoke(formatted_prompt)
            
            # Extract the content
            output = response.content if hasattr(response, 'content') else str(response)
            
            # Extract thought process
            thought_process = self._extract_thought_process(output)
            
            # Add to conversation history
            if self.conversation_manager and session_id:
                self.conversation_manager.add_message(
                    session_id,
                    "Worker",
                    output,
                    thought_process
                )
            
            # Return updated state as dictionary
            result = dict(state)
            result.update({
                "feedback": output,
                "thought_process": thought_process,
                "status": "done"
            })
            
            logger.info(f"[WorkerAgent] Task completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"[WorkerAgent] Error in Worker agent: {str(e)}")
            result = dict(state)
            result.update({
                "status": "error",
                "feedback": f"I apologize, but I encountered an error while working on this task: {str(e)}",
                "thought_process": "Error occurred during processing"
            })
            return result
    
    def _extract_thought_process(self, output: str) -> str:
        """Extract thought process from the response."""
        thought_process = ""
        sections = ["ANALYZE:", "PLAN:", "EXECUTE:", "VERIFY:", "EXPLAIN:"]
        for section in sections:
            if section in output:
                start = output.find(section)
                end = output.find("\n\n", start) if "\n\n" in output[start:] else len(output)
                thought_process += output[start:end].strip() + "\n\n"
        
        if not thought_process:
            # Fallback if structured sections aren't found
            thought_process = f"""ANALYZE: Processing task requirements
PLAN: Developing implementation approach
EXECUTE: Working on the solution
VERIFY: Checking implementation quality
EXPLAIN: Task completed with focus on quality and functionality"""
        
        return thought_process.strip() 