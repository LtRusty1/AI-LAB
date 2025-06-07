#!/usr/bin/env python3

import requests
import time
import json
import subprocess
import sys
import os

def test_server():
    """Test that the server is running and responding correctly."""
    
    # Test health endpoint
    try:
        response = requests.get("http://localhost:8001/health", timeout=5)
        if response.status_code == 200:
            print("✅ Health check passed")
            print(f"Response: {response.json()}")
        else:
            print(f"❌ Health check failed with status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False
    
    # Test chat endpoint
    try:
        chat_data = {
            "message": "What is your project organization chart?",
            "session_id": "test_session"
        }
        
        response = requests.post(
            "http://localhost:8001/chat", 
            json=chat_data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Chat endpoint test passed")
            print(f"Response: {data.get('response', 'No response')[:100]}...")
            print(f"Status: {data.get('status')}")
            if data.get('thought_process'):
                print(f"Thought process: {data.get('thought_process')[:100]}...")
        else:
            print(f"❌ Chat endpoint failed with status {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Chat endpoint test failed: {e}")
        return False
    
    return True

if __name__ == "__main__":
    print("🚀 Testing AI-Lab backend server...")
    
    if test_server():
        print("\n🎉 All tests passed! The server is working correctly.")
        print("\nYou can now:")
        print("1. Open http://localhost:3000 in your browser")
        print("2. Chat with the CEO agent")
        print("3. Ask about the organization structure")
    else:
        print("\n❌ Tests failed. Please check the server logs.")
        sys.exit(1) 