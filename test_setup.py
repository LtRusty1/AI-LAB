#!/usr/bin/env python3
"""
Test script to verify that the AI-Lab project is set up correctly.
"""

import sys
import subprocess
import importlib

def test_imports():
    """Test that all required packages can be imported."""
    required_packages = [
        'streamlit',
        'langchain',
        'langchain_openai', 
        'langgraph',
        'plotly',
        'networkx',
        'rich'
    ]
    
    print("Testing package imports...")
    for package in required_packages:
        try:
            importlib.import_module(package)
            print(f"✅ {package}")
        except ImportError as e:
            print(f"❌ {package}: {e}")
            return False
    
    return True

def test_ollama_connection():
    """Test if Ollama is running and accessible."""
    try:
        import requests
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            print("✅ Ollama server is running")
            models = response.json().get('models', [])
            if any('mistral' in model.get('name', '') for model in models):
                print("✅ Mistral model is available")
            else:
                print("⚠️  Mistral model not found. Run 'ollama pull mistral'")
            return True
        else:
            print("❌ Ollama server responded with error")
            return False
    except Exception as e:
        print(f"❌ Cannot connect to Ollama: {e}")
        print("💡 Make sure Ollama is running: ollama serve")
        return False

def test_agents():
    """Test that our agent classes work."""
    try:
        from agents import AgentState, CEOAgent, WorkerAgent, QAAgent
        from langchain_openai import ChatOpenAI
        
        # Test AgentState
        state = AgentState(
            message="test",
            status="pending", 
            feedback="",
            transitions=[]
        )
        print("✅ AgentState creation works")
        
        # Test agent creation (without LLM call)
        llm = ChatOpenAI(
            model="mistral",
            api_key="not-needed",
            base_url="http://localhost:11434/v1"
        )
        
        ceo = CEOAgent(llm)
        worker = WorkerAgent(llm)
        qa = QAAgent(llm)
        
        print("✅ Agent classes can be instantiated")
        return True
        
    except Exception as e:
        print(f"❌ Agent test failed: {e}")
        return False

def test_pipeline_graph():
    """Test the pipeline graph creation."""
    try:
        from pipeline_graph import create_agent_graph
        graph = create_agent_graph()
        compiled_graph = graph.compile()
        print("✅ Pipeline graph creation works")
        return True
    except Exception as e:
        print(f"❌ Pipeline graph test failed: {e}")
        return False

def test_visualization():
    """Test the visualization component."""
    try:
        from visualization import AgentVisualizer
        viz = AgentVisualizer()
        fig = viz.create_animation_frame([])
        print("✅ Visualization component works")
        return True
    except Exception as e:
        print(f"❌ Visualization test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("🧪 Testing AI-Lab Setup\n")
    
    tests = [
        ("Package Imports", test_imports),
        ("Ollama Connection", test_ollama_connection),
        ("Agent Classes", test_agents),
        ("Pipeline Graph", test_pipeline_graph), 
        ("Visualization", test_visualization)
    ]
    
    passed = 0
    total = len(tests)
    
    for name, test_func in tests:
        print(f"\n📋 {name}:")
        if test_func():
            passed += 1
        
    print(f"\n📊 Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! You can now run:")
        print("   streamlit run app.py")
        print("   or")
        print("   python start_pipeline.bat")
    else:
        print("\n⚠️  Some tests failed. Please fix the issues above.")
        
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 