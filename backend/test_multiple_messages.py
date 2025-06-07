import requests
import json
import time

def test_message(message, session_id="test_session"):
    url = "http://localhost:8001/chat"
    payload = {
        "message": message,
        "session_id": session_id
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        print(f"Message: {message}")
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Response: {data['response'][:100]}...")
            print(f"Status: {data['status']}")
            if data['thought_process']:
                print(f"Thought Process: {data['thought_process'][:100]}...")
            print("-" * 80)
            return True
        else:
            print(f"Error: {response.text}")
            print("-" * 80)
            return False
    except Exception as e:
        print(f"Error: {e}")
        print("-" * 80)
        return False

def main():
    print("Testing AI-Lab backend with multiple message types...")
    print("=" * 80)
    
    test_messages = [
        "Hi",
        "Tell me about your organization structure",
        "I need to implement a new feature",
        "Can you review this code?",
        "What's your strategy for AI development?",
    ]
    
    session_id = f"test_{int(time.time())}"
    results = []
    
    for message in test_messages:
        success = test_message(message, session_id)
        results.append(success)
        time.sleep(1)  # Small delay between requests
    
    print(f"Test Results: {sum(results)}/{len(results)} tests passed")
    print("All tests completed!")

if __name__ == "__main__":
    main() 