import requests
import json

url = "http://localhost:8000/api/v1/chat"

# Test 1: List tasks
print("Test 1: List tasks")
response = requests.post(url, json={"message": "list all tasks"})
print(f"Status: {response.status_code}")
print(f"Response: {json.dumps(response.json(), indent=2)}")
print()

# Test 2: Add a task
print("Test 2: Add task")
response = requests.post(url, json={"message": "add a task: test frontend integration"})
print(f"Status: {response.status_code}")
print(f"Response: {json.dumps(response.json(), indent=2)}")
print()
