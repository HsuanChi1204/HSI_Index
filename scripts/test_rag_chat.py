import requests
import json

def test_rag():
    url = "http://localhost:8000/api/chat"
    
    # Question that requires the paper (RAG)
    payload = {
        "query": "How is the HCI (Human-Context Index) calculated? What is the formula?",
        "history": []
    }
    
    try:
        print(f"Sending query: {payload['query']}")
        response = requests.post(url, json=payload)
        
        if response.status_code == 200:
            data = response.json()
            print("\n✅ Response received:")
            print(data['response'])
        else:
            print(f"\n❌ Error {response.status_code}: {response.text}")
            
    except Exception as e:
        print(f"\n❌ Connection failed: {e}")
        print("Make sure the backend is running (python3 main.py)")

if __name__ == "__main__":
    test_rag()
