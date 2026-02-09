import requests
import json

url = "http://localhost:8000/api/v1/chat"

# Test with dev token (like the frontend would send)
headers = {
    "Authorization": "Bearer dev-token-123",
    "Content-Type": "application/json"
}

print("=" * 60)
print("Frontend Integration Test")
print("=" * 60)
print()

# Test 1: List tasks (with dev token)
print("Test 1: List tasks (with dev auth token)")
response = requests.post(url, json={"message": "list all tasks"}, headers=headers)
print(f"Status: {response.status_code}")
data = response.json()
print(f"Assistant: {data['assistant_message']}")
print(f"Conversation ID: {data['conversation_id']}")
print()

# Test 2: Add a task
print("Test 2: Add task")
response = requests.post(url, json={"message": "add task: buy groceries"}, headers=headers)
print(f"Status: {response.status_code}")
data = response.json()
print(f"Assistant: {data['assistant_message']}")
print(f"Conversation ID: {data['conversation_id']}")
print()

# Test 3: List tasks again
print("Test 3: List tasks again (should show the new task)")
response = requests.post(url, json={"message": "show my tasks"}, headers=headers)
print(f"Status: {response.status_code}")
data = response.json()
print(f"Assistant: {data['assistant_message']}")
print()

# Test 4: Complete a task (get task_id from Test 3)
print("Test 4: Complete first task")
response = requests.post(url, json={"message": "complete task 1"}, headers=headers)
print(f"Status: {response.status_code}")
data = response.json()
print(f"Assistant: {data['assistant_message']}")
print()

# Test 5: List tasks again
print("Test 5: List tasks again (should show completed task)")
response = requests.post(url, json={"message": "list tasks"}, headers=headers)
print(f"Status: {response.status_code}")
data = response.json()
print(f"Assistant: {data['assistant_message']}")
print()

print("=" * 60)
print("All tests completed!")
print("=" * 60)
