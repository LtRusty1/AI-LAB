"""
Reflection Agent implementation.
"""

from typing import Dict, Any
from langchain.prompts import ChatPromptTemplate
import logging

logger = logging.getLogger(__name__)

class ReflectionAgent:
    def __init__(self, llm, conversation_manager=None):
        self.llm = llm
        self.conversation_manager = conversation_manager
        
        # Define the Reflection agent's prompt template
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a Reflection agent responsible for process improvement and strategic thinking. Your role is to:
1. REFLECT on the current situation and processes
2. ANALYZE what has been done and what could be improved
3. SYNTHESIZE insights from the work completed
4. OPTIMIZE processes and approaches
5. STRATEGIZE for future improvements

Follow this structured thinking process:
REFLECT: What can we learn from the current situation?
ANALYZE: What worked well and what could be improved?
SYNTHESIZE: What are the key insights and patterns?
OPTIMIZE: How can we improve our processes?
STRATEGIZE: What should be our approach going forward?

Always provide your thought process in this format:
REFLECT: [Your reflection on the situation]
ANALYZE: [Your analysis of what happened]
SYNTHESIZE: [Key insights and lessons learned]
OPTIMIZE: [Process improvements]
STRATEGIZE: [Strategic recommendations]

Focus on continuous improvement and strategic thinking."""),
            ("human", "{context}\n\nSituation to reflect on: {message}")
        ])
    
    def run(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Run the Reflection agent on the given state."""
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
            
            logger.info(f"[ReflectionAgent] Reflecting on: {message}")
            
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
                    "Reflection",
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
            
            logger.info(f"[ReflectionAgent] Reflection completed")
            return result
            
        except Exception as e:
            logger.error(f"[ReflectionAgent] Error in Reflection agent: {str(e)}")
            result = dict(state)
            result.update({
                "status": "error",
                "feedback": f"I apologize, but I encountered an error during reflection: {str(e)}",
                "thought_process": "Error occurred during processing"
            })
            return result
    
    def _extract_thought_process(self, output: str) -> str:
        """Extract thought process from the response."""
        thought_process = ""
        sections = ["REFLECT:", "ANALYZE:", "SYNTHESIZE:", "OPTIMIZE:", "STRATEGIZE:"]
        for section in sections:
            if section in output:
                start = output.find(section)
                end = output.find("\n\n", start) if "\n\n" in output[start:] else len(output)
                thought_process += output[start:end].strip() + "\n\n"
        
        if not thought_process:
            # Fallback if structured sections aren't found
            thought_process = f"""REFLECT: Analyzed current situation and progress
ANALYZE: Reviewed processes and outcomes  
SYNTHESIZE: Identified key patterns and insights
OPTIMIZE: Recommended process improvements
STRATEGIZE: Developed strategic approach for future"""
        
        return thought_process.strip() 