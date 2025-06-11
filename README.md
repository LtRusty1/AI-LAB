# AI-Lab: Comprehensive AI Development Environment

![AI-Lab](https://img.shields.io/badge/AI-Lab-blue.svg)
![Python](https://img.shields.io/badge/Python-3.10+-green.svg)

A comprehensive AI development environment featuring multi-agent systems, AutoGen integration, Ollama model deployment, and a modern web interface for building and testing AI applications.

## 🚀 Project Overview

AI-Lab is a full-stack AI development platform that combines:
- **Multi-Agent Systems**: Dynamic agent orchestration with CEO-to-Worker delegation patterns
- **AutoGen Integration**: Microsoft's AutoGen framework for conversational AI
- **Ollama Integration**: Local LLM deployment with GPU acceleration
- **Web Interface**: React-based frontend with real-time chat and conversation management
- **REST API**: FastAPI backend with conversation storage and state management
- **GPU Optimization**: CUDA-accelerated model inference

## 📁 Project Structure

```
AI-lab/
├── agents/                     # Custom AI agent implementations
├── AutoGen/                   # Microsoft AutoGen framework
│   ├── python/               # Python packages and samples
│   ├── dotnet/               # .NET implementations
│   └── docs/                 # Documentation
├── backend/                   # FastAPI backend server
│   ├── main.py              # Main API server
│   ├── conversations/       # Stored conversations (JSON)
│   └── states/              # Agent states (JSON)
├── frontend/                  # React web interface
│   ├── src/                 # Source code
│   │   ├── components/      # React components
│   │   └── pages/           # Page components
│   └── public/              # Static assets
├── config/                    # Configuration files
├── docker/                    # Docker configurations
├── configure_gpu.ps1          # GPU setup script (Windows)
├── setup_efficient_model.ps1  # Lightweight model setup (Windows)
├── simple_gpu_setup.ps1       # Simplified GPU configuration (Windows)
├── start_ai_lab_complete.bat  # One-click launcher (Windows)
├── install.sh                 # Ollama installer for Linux
├── app.py                     # Main application entry
├── agents.py                  # Agent orchestration
├── multi.py                   # Multi-agent coordination
├── requirements.txt           # Python dependencies
└── LAUNCH.bat                # Windows launcher
```

## 🛠️ Installation & Setup

### Prerequisites
- **Python 3.10+** (tested with 3.11)
- **Node.js 16+** (for frontend)
- **Git LFS** (for large model files)
- **NVIDIA GPU** (optional, for accelerated inference)
- **Windows 10/11** or **Linux**

### Quick Start

1. **Clone the Repository**
   ```bash
   git clone https://github.com/LtRusty1/AI-LAB.git
   cd AI-LAB
   ```

2. **Setup Python Environment**
   ```bash
   # Windows
   python -m venv venv
   .\venv\Scripts\activate
   
   # Install dependencies
   pip install -r requirements.txt
   ```

3. **Setup Frontend**
   ```bash
   cd frontend
   npm install
   cd ..
   ```

4. **Configure GPU (Optional)**
   - **Windows**
     ```powershell
     # Run as Administrator
     .\configure_gpu.ps1
     # or for efficient model setup
     .\setup_efficient_model.ps1
     ```
   - **Linux**
     ```bash
     ./install.sh       # Installs Ollama and optional GPU drivers
     ```

5. **Launch the Application**
   ```bash
   # Complete launch (recommended)
   .\LAUNCH.bat
   
   # Or launch components individually
   python app.py              # Main application
   python backend/main.py     # Backend API only
   ```

## 💻 Usage

### Starting the System

#### Option 1: Complete Launch (Recommended)
```bash
.\LAUNCH.bat
```
This starts all components:
- Backend API server
- Frontend development server
- Ollama service (if installed)

#### Option 2: Individual Components
```bash
# Backend only
python backend/main.py

# Frontend only
cd frontend && npm start

# Agent pipeline only
python backend/ai_lab/pipeline_graph.py

# Multi-agent example
python multi.py
```

#### Option 3: Docker Compose
```bash
docker compose up --build
```

### Using the Web Interface

1. **Open Browser**: Navigate to `http://localhost:3000`
2. **Start Chatting**: Use the chat interface to interact with agents
3. **View History**: Access previous conversations from the sidebar
4. **Monitor Agents**: View agent status and routing decisions

### Using the CLI Interface

```bash
# Interactive agent pipeline
python backend/ai_lab/pipeline_graph.py

# Multi-agent conversation
python multi.py

# Direct agent interaction
python agents.py
```

## 🔧 Configuration

### Environment Variables
Create a `.env` file in the root directory:
```env
# API Configuration
API_HOST=localhost
API_PORT=8000

# Ollama Configuration
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=mistral

# GPU Configuration
CUDA_VISIBLE_DEVICES=0
```

### GPU Configuration
For optimal performance with NVIDIA GPUs:

1. **Run GPU Setup Script**:
   ```powershell
   .\configure_gpu.ps1
   ```

2. **Verify CUDA Installation**:
   ```bash
   nvidia-smi
   ```

3. **Configure Ollama for GPU**:
   ```bash
   # Pull a model
   ollama pull mistral
   
   # Start with GPU acceleration
   .\start_ollama_gpu.bat
   ```

## 🔌 API Reference

### Chat Endpoint
```http
POST /chat
Content-Type: application/json

{
  "message": "Your message here",
  "conversation_id": "optional-conversation-id"
}
```

**Response**:
```json
{
  "response": "Agent response",
  "agent": "ceo",
  "conversation_id": "generated-id",
  "timestamp": "2025-01-06T12:00:00Z"
}
```

### Conversations Endpoint
```http
GET /conversations
```

**Response**:
```json
{
  "conversations": [
    {
      "id": "conversation-id",
      "messages": [...],
      "created_at": "2025-01-06T12:00:00Z"
    }
  ]
}
```

## 🛡️ Agent System Details

### CEO Agent
- **Role**: Strategic decision maker and task delegator
- **Capabilities**:
  - Analyzes incoming requests
  - Routes to appropriate specialist agents
  - Reviews and approves final outputs
  - Manages workflow iteration

### Worker Agent
- **Role**: Task implementation specialist
- **Capabilities**:
  - Technical implementation planning
  - Code generation and architecture design
  - Problem-solving and solution development

### QA Agent
- **Role**: Quality assurance specialist
- **Capabilities**:
  - Code review and testing
  - Security analysis
  - Performance optimization suggestions
  - Best practices enforcement

### Reflection Agent
- **Role**: Continuous improvement facilitator
- **Capabilities**:
  - Output analysis and critique
  - Improvement suggestions
  - Process optimization
  - Knowledge distillation

### Adding New Agents

1. **Create Agent Class** in `agents/__init__.py`:
   ```python
   class NewAgent(BaseAgent):
       def __init__(self, llm):
           self.llm = llm
           self.name = "New Agent"
       
       def process(self, message, context):
           # Agent logic here
           return response
   ```

2. **Register Agent**:
   ```python
   AGENT_REGISTRY = {
       # ... existing agents
       "new_agent": NewAgent,
   }
   ```

3. **Update CEO Routing**: The CEO will automatically detect and can route to the new agent.

## 🔄 Development Workflow

### Adding Features

1. **Backend Changes**:
   - Update `backend/main.py` for new endpoints
   - Modify agent logic in `agents/__init__.py`
   - Update requirements if needed

2. **Frontend Changes**:
   - Add components in `frontend/src/components/`
   - Update routing in `App.js`
   - Install new packages: `npm install package-name`

3. **Agent Development**:
   - Create new agent classes
   - Update the registry
   - Test with CLI interface

### Testing

```bash
# Backend tests
python -m pytest backend/tests/

# Frontend tests
cd frontend && npm test

# Basic environment test
python test_setup.py
```

### Code Style

- **Python**: Follow PEP 8, use `black` for formatting
- **JavaScript/TypeScript**: Use ESLint configuration in `frontend/.eslintrc.js`
- **Documentation**: Update README for significant changes

## 🔧 Troubleshooting

### Common Issues

1. **Ollama Connection Failed**:
   ```bash
   # Check if Ollama is running
   curl http://localhost:11434/api/tags
   
   # Start Ollama
   ollama serve
   ```

2. **GPU Not Detected**:
   ```bash
   # Verify CUDA installation
   nvidia-smi
   
   # Run GPU configuration
   .\configure_gpu.ps1
   ```

3. **Frontend Build Errors**:
   ```bash
   # Clear cache and reinstall
   cd frontend
   rm -rf node_modules package-lock.json
   npm install
   ```

4. **Agent Not Responding**:
   - Check Ollama service status
   - Verify model is downloaded: `ollama list`
   - Check API logs for errors

## 📚 Technical Reference

### System Requirements
- **Minimum**: 8GB RAM, 4GB GPU VRAM
- **Recommended**: 16GB RAM, 8GB GPU VRAM
- **Storage**: 10GB for models and data

### Ollama Configuration
- **Installation**: `C:\Users\User\AppData\Local\Programs\Ollama`
- **Service**: Runs on port 11434 (default)
- **GPU**: CUDA v12.9 support
- **Models**: Stored locally after download

### Agent Pipeline
- **Framework**: LangGraph for orchestration
- **LLM Integration**: OpenAI-compatible API calls
- **State Management**: Persistent JSON storage
- **Routing**: Dynamic CEO-based delegation

### Development Environment
- **Python**: 3.10+ with virtual environment
- **Frontend**: React with TypeScript support
- **Backend**: FastAPI with async support
- **Database**: JSON file storage (future: PostgreSQL)

## 🤝 Contributing

### Getting Started
1. Fork the repository
2. Create a feature branch: `git checkout -b feature/new-feature`
3. Make changes and test thoroughly
4. Commit with clear messages: `git commit -m "Add new feature"`
5. Push and create a Pull Request

### Contribution Guidelines
- Follow existing code style and patterns
- Add tests for new functionality
- Update documentation for significant changes
- Ensure backward compatibility

## 🙏 Acknowledgments

- **Microsoft AutoGen**: For the conversational AI framework
- **Ollama**: For local LLM deployment
- **LangGraph**: For agent orchestration
- **FastAPI**: For the backend framework
- **React**: For the frontend framework

## 📞 Support

For support and questions:
- **Issues**: Use GitHub Issues for bug reports and feature requests
- **Discussions**: Use GitHub Discussions for general questions
- **Repository**: https://github.com/LtRusty1/AI-LAB

---

## 🚀 Quick Reference Card

### Essential Commands
```bash
# Quick Start
git clone https://github.com/LtRusty1/AI-LAB.git
cd AI-LAB && python -m venv venv && .\venv\Scripts\activate
pip install -r requirements.txt && .\LAUNCH.bat

# Development
python app.py              # Main application
python backend/ai_lab/pipeline_graph.py  # Agent pipeline CLI
python multi.py           # Multi-agent example
python backend/main.py    # Backend API only

# GPU Setup
.\configure_gpu.ps1       # Configure GPU
.\start_ollama_gpu.bat    # Start Ollama with GPU
nvidia-smi                # Check GPU status
```

### Important URLs
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Ollama**: http://localhost:11434

### Key Directories
- `agents/` - Agent implementations
- `backend/` - FastAPI server
- `frontend/` - React interface
- `AutoGen/` - Microsoft AutoGen
- `backend/conversations/` - Stored chats
- `backend/states/` - Agent states

### Architecture Summary
```
User → Frontend → Backend API → Agent System → LLM (Ollama/AutoGen)
     ↳ Chat UI  ↳ FastAPI   ↳ CEO Router  ↳ GPU Acceleration
```

---

**Last Updated**: January 2025  
**Version**: 2.0.0  
**Repository**: https://github.com/LtRusty1/AI-LAB  
**Maintainer**: AI-Lab Development Team
