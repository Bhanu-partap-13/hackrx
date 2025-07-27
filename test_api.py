import requests
import json

# Test data from the hackathon problem statement
test_url = "http://127.0.0.1:8000/hackrx/run"

test_payload = {
    "documents": "https://hackrx.blob.core.windows.net/assets/policy.pdf?sv=2023-01-03&st=2025-07-04T09%3A11%3A24Z&se=2027-07-05T09%3A11%3A00Z&sr=b&sp=r&sig=N4a9OU0w0QXO6AOIBiu4bpl7AXvEZogeT%2FjUHNO7HzQ%3D",
    "questions": [
        "What is the grace period for premium payment under the National Parivar Mediclaim Plus Policy?",
        "What is the waiting period for pre-existing diseases (PED) to be covered?",
        "Does this policy cover maternity expenses, and what are the conditions?"
    ]
}

headers = {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer 80952cdfb4fc8cfff557b6cb27c4c39b9c980c039093b1ec6047ebedba90a9d7'
}

try:
    response = requests.post(test_url, json=test_payload, headers=headers)
    print("Status Code:", response.status_code)
    print("Response:", json.dumps(response.json(), indent=2))
except Exception as e:
    print("Error:", str(e))
