import requests
import json

base_url = "http://localhost:8000"

print("=" * 60)
print("Testing Authentication Flow")
print("=" * 60)
print()

# Test 1: Sign up a new user
print("Test 1: Sign up new user")
test_email = "test@example.com"
test_password = "password123"

response = requests.post(
    f"{base_url}/api/v1/auth/signup",
    json={"email": test_email, "password": test_password}
)
print(f"Status: {response.status_code}")
data = response.json()
print(f"Response: {json.dumps(data, indent=2)}")
print()

if response.status_code == 201:
    access_token = data.get("access_token")
    user_id = data.get("user_id")

    # Test 2: Login with the same credentials
    print("Test 2: Login with credentials")
    response = requests.post(
        f"{base_url}/api/v1/auth/login",
        json={"email": test_email, "password": test_password}
    )
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Response: {json.dumps(data, indent=2)}")
    print()

    # Test 3: Access /me endpoint with token
    print("Test 3: Access /me endpoint with token")
    response = requests.get(
        f"{base_url}/api/v1/auth/me",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Response: {json.dumps(data, indent=2)}")
    print()

    # Test 4: Use chat endpoint with token
    print("Test 4: Use chat endpoint with authentication")
    response = requests.post(
        f"{base_url}/api/v1/chat",
        headers={"Authorization": f"Bearer {access_token}"},
        json={"message": "list all tasks"}
    )
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Assistant: {data.get('assistant_message', 'N/A')}")
    print(f"Conversation ID: {data.get('conversation_id', 'N/A')}")
    print()

    # Test 5: Try to access chat without token (should fail)
    print("Test 5: Access chat endpoint without token (should fail)")
    response = requests.post(
        f"{base_url}/api/v1/chat",
        json={"message": "list all tasks"}
    )
    print(f"Status: {response.status_code} (expected: 401)")
    if response.status_code == 401:
        print("✓ Correctly rejected unauthenticated request")
    print()

    # Test 6: Login with dev user
    print("Test 6: Login with development user")
    response = requests.post(
        f"{base_url}/api/v1/auth/login",
        json={"email": "dev@example.com", "password": "password123"}
    )
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Response: {json.dumps(data, indent=2)}")
    if response.status_code == 200:
        print("✓ Development user login works!")
    print()

else:
    print(f"✗ Signup failed with status {response.status_code}")
    print(data.get("detail", "Unknown error"))

print("=" * 60)
print("Authentication tests completed!")
print("=" * 60)
