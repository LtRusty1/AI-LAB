import requests
import json

def test_chat():
    url = "http://localhost:8001/chat"
    payload = {
        "message": "hi",
        "session_id": "test123"
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    print("Testing chat endpoint...")
    success = test_chat()
    print(f"Test {'PASSED' if success else 'FAILED'}") 