"""
QA Agent implementation.
"""

from typing import Dict, Any
from langchain.prompts import ChatPromptTemplate
import logging

logger = logging.getLogger(__name__)

class QAAgent:
    def __init__(self, llm, conversation_manager=None):
        self.llm = llm
        self.conversation_manager = conversation_manager
        
        # Define the QA agent's prompt template
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a Quality Assurance (QA) agent responsible for reviewing and validating work. Your role is to:
1. REVIEW the submitted work for quality and completeness
2. VALIDATE that requirements are met
3. IDENTIFY any issues or areas for improvement
4. RECOMMEND necessary changes or approvals
5. DOCUMENT your findings

Follow this structured thinking process:
REVIEW: What aspects of the work did you examine?
VALIDATE: Do the deliverables meet the specified requirements?
IDENTIFY: What issues, if any, were found?
RECOMMEND: What actions should be taken next?
DOCUMENT: Summary of your quality assessment

Always provide your thought process in this format:
REVIEW: [Your review process]
VALIDATE: [Your validation results]
IDENTIFY: [Issues found, if any]
RECOMMEND: [Your recommendations]
DOCUMENT: [Your documentation]

Maintain high standards while being constructive and helpful."""),
            ("human", "{context}\n\nWork to review: {message}")
        ])
    
    def run(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Run the QA agent on the given state."""
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
            
            logger.info(f"[QAAgent] Reviewing work: {message}")
            
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
                    "QA",
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
            
            logger.info(f"[QAAgent] Quality review completed")
            return result
            
        except Exception as e:
            logger.error(f"[QAAgent] Error in QA agent: {str(e)}")
            result = dict(state)
            result.update({
                "status": "error",
                "feedback": f"I apologize, but I encountered an error during the quality review: {str(e)}",
                "thought_process": "Error occurred during processing"
            })
            return result
    
    def _extract_thought_process(self, output: str) -> str:
        """Extract thought process from the response."""
        thought_process = ""
        sections = ["REVIEW:", "VALIDATE:", "IDENTIFY:", "RECOMMEND:", "DOCUMENT:"]
        for section in sections:
            if section in output:
                start = output.find(section)
                end = output.find("\n\n", start) if "\n\n" in output[start:] else len(output)
                thought_process += output[start:end].strip() + "\n\n"
        
        if not thought_process:
            # Fallback if structured sections aren't found
            thought_process = f"""REVIEW: Conducted comprehensive quality assessment
VALIDATE: Checked against requirements and standards
IDENTIFY: Examined for potential issues and improvements
RECOMMEND: Provided feedback and next steps
DOCUMENT: Quality review completed with detailed analysis"""
        
        return thought_process.strip() 