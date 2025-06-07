"""
Mock LLM for testing when Ollama is not available.
"""

import random
from typing import List, Dict, Any


class MockResponse:
    """Mock response object that mimics the structure of a real LLM response."""
    
    def __init__(self, content: str):
        self.content = content


class MockLLM:
    """Mock LLM that provides realistic responses for testing purposes."""
    
    def __init__(self):
        self.ceo_responses = {
            "organization": """As the CEO of AI-Lab, I'm proud to lead an innovative organization structured for excellence:

**Organization Structure:**

CEO (Chief Executive Officer):
- Strategic decision making and overall direction
- Resource allocation and team coordination 
- Quality assurance oversight and final approvals

Worker (Development Team):
- Implementation of technical solutions
- Code development and system architecture
- Problem-solving and feature development

QA (Quality Assurance):
- Code review and quality validation
- Testing and verification processes
- Ensuring standards and best practices

This structure ensures efficient workflow, clear accountability, and high-quality deliverables. Each role is essential for our success.""",

            "strategy": """Our strategic approach focuses on:

1. **Innovation Leadership**: Staying at the forefront of AI technology
2. **Quality Excellence**: Maintaining the highest standards in all deliverables  
3. **Efficient Execution**: Streamlined processes from conception to deployment
4. **Collaborative Culture**: Foster teamwork and knowledge sharing
5. **Continuous Improvement**: Regular reflection and process optimization

We believe in empowering our teams while maintaining clear oversight and quality control.""",

            "delegation": """Based on your request, I'm evaluating the best approach for task delegation:

**Analysis**: This appears to be a technical implementation task requiring specialized skills.

**Decision**: I'm delegating this to our Development Worker team who specializes in:
- Technical implementation and coding
- System architecture and design
- Problem-solving and optimization

The Worker team will handle the implementation, followed by QA review to ensure quality standards are met.""",

            "default": """Thank you for your inquiry. As the CEO of AI-Lab, I'm here to help coordinate our team's efforts and provide strategic guidance. 

Our organization operates with clear roles and responsibilities:
- I handle strategic decisions and coordination
- Our Worker team focuses on implementation
- Our QA team ensures quality and standards

How can I assist you today? Whether you need information about our organization, want to delegate a task, or discuss strategy, I'm here to help."""
        }
        
        self.worker_responses = {
            "implementation": """ANALYZE: The task requires careful planning and systematic implementation approach.

PLAN: I'll break this down into manageable components:
1. Understand the requirements thoroughly
2. Design the solution architecture
3. Implement core functionality
4. Test and validate the implementation
5. Document the solution

EXECUTE: Beginning implementation with focus on:
- Clean, maintainable code structure
- Following best practices and standards
- Ensuring scalability and performance
- Proper error handling and logging

VERIFY: The implementation meets all specified requirements and follows our coding standards. All functionality has been tested and validated.

EXPLAIN: I've completed the implementation using industry best practices, ensuring the solution is robust, scalable, and maintainable. The code is well-documented and ready for QA review.""",

            "default": """ANALYZE: Processing the assigned task and understanding the requirements.

PLAN: Developing a structured approach to deliver high-quality results:
- Requirements analysis and clarification
- Solution design and architecture planning  
- Implementation with best practices
- Testing and validation procedures

EXECUTE: Working on the solution with attention to:
- Code quality and maintainability
- Performance optimization
- Security considerations
- Documentation standards

VERIFY: Ensuring the deliverable meets all requirements and quality standards.

EXPLAIN: Task completed successfully with focus on quality, performance, and maintainability. Ready for quality assurance review."""
        }
        
        self.qa_responses = {
            "review": """REVIEW: Conducted comprehensive examination of the submitted work, including code quality, functionality, and adherence to standards.

VALIDATE: The deliverable meets the specified requirements and follows our established coding standards. All core functionality works as expected.

IDENTIFY: Minor opportunities for improvement in documentation and code comments. Overall implementation is solid and well-structured.

RECOMMEND: Approve for deployment with suggested documentation enhancements. The work demonstrates good practices and meets quality standards.

DOCUMENT: Quality review completed successfully. The implementation shows strong technical execution and is ready for production use.""",

            "default": """REVIEW: Performed thorough quality assessment of the submitted work across multiple dimensions.

VALIDATE: Checked compliance with requirements, coding standards, and performance benchmarks. All critical criteria are satisfied.

IDENTIFY: The work demonstrates good quality with only minor areas for potential enhancement. No blocking issues found.

RECOMMEND: Approve the deliverable for next phase. Suggested minor improvements can be addressed in future iterations.

DOCUMENT: Quality assurance review complete. The work meets our quality standards and is approved for progression."""
        }
        
        self.reflection_responses = {
            "process": """REFLECT: Analyzing our current processes and identifying opportunities for enhancement and optimization.

ANALYZE: Our workflow demonstrates strong fundamentals with effective communication between team members. The CEO provides clear direction, Workers deliver quality implementations, and QA maintains high standards.

SYNTHESIZE: Key insights include the importance of clear role definition, structured communication, and continuous feedback loops. Our collaborative approach enables efficient problem-solving.

OPTIMIZE: Recommendations for improvement:
- Enhanced documentation standards
- More frequent checkpoint reviews
- Streamlined handoff processes between roles

STRATEGIZE: Moving forward, we should focus on maintaining our collaborative culture while implementing process refinements to increase efficiency and quality.""",

            "default": """REFLECT: Examining our current situation and processes to identify learning opportunities and improvements.

ANALYZE: Our team dynamics show effective collaboration with clear role boundaries and good communication patterns. Each team member contributes their specialized expertise effectively.

SYNTHESIZE: The key to our success lies in structured approaches, clear communication, and commitment to quality at every stage of our work.

OPTIMIZE: Areas for enhancement include refining our feedback mechanisms and establishing more robust knowledge sharing practices.

STRATEGIZE: Continue building on our collaborative foundation while implementing targeted improvements to enhance efficiency and outcomes."""
        }
    
    def invoke(self, messages) -> MockResponse:
        """Mock the invoke method of a real LLM."""
        content = self._extract_content(messages)
        
        # Determine which agent type this is for based on content
        if "worker" in content or "task:" in content.lower():
            responses = self.worker_responses
            if any(word in content for word in ['implement', 'code', 'develop', 'build']):
                response_text = responses["implementation"]
            else:
                response_text = responses["default"]
                
        elif "qa" in content or "review" in content.lower() or "work to review:" in content.lower():
            responses = self.qa_responses
            if any(word in content for word in ['review', 'quality', 'check', 'validate']):
                response_text = responses["review"]
            else:
                response_text = responses["default"]
                
        elif "reflection" in content or "reflect on:" in content.lower():
            responses = self.reflection_responses
            if any(word in content for word in ['process', 'improve', 'strategy']):
                response_text = responses["process"]
            else:
                response_text = responses["default"]
                
        else:
            # CEO responses
            responses = self.ceo_responses
            if any(word in content for word in ['organization', 'structure', 'chart', 'roles', 'team']):
                response_text = responses["organization"]
            elif any(word in content for word in ['strategy', 'plan', 'direction', 'goals']):
                response_text = responses["strategy"]
            elif any(word in content for word in ['implement', 'code', 'develop', 'build', 'delegate']):
                response_text = responses["delegation"]
            else:
                response_text = responses["default"]
        
        return MockResponse(response_text)
    
    def _extract_content(self, messages) -> str:
        """Extract content from various message formats."""
        if isinstance(messages, str):
            return messages.lower()
        elif isinstance(messages, list):
            content = ""
            for msg in messages:
                if hasattr(msg, 'content'):
                    content += msg.content.lower() + " "
                elif isinstance(msg, dict) and 'content' in msg:
                    content += msg['content'].lower() + " "
                else:
                    content += str(msg).lower() + " "
            return content
        else:
            return str(messages).lower()
    
    def __call__(self, *args, **kwargs):
        """Allow the mock to be called directly."""
        return self.invoke(*args, **kwargs) 