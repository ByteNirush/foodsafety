import requests
import json

def test_openrouter_api():
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": "Bearer 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",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost:8000",
        "X-Title": "Food Safety Assistant"
    }
    
    data = {
        "model": "anthropic/claude-3-opus:beta",
        "messages": [
            {
                "role": "system",
                "content": "You are a Food Safety Assistant. Provide helpful information about food safety."
            },
            {
                "role": "user",
                "content": "Hello, can you help me with food safety?"
            }
        ],
        "max_tokens": 500,
        "temperature": 0.7
    }
    
    try:
        response = requests.post(url, headers=headers, json=data)
        print(f"Status Code: {response.status_code}")
        print("Response:")
        print(json.dumps(response.json(), indent=2))
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    test_openrouter_api() 