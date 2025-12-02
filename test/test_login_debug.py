import requests
import json

url = "http://127.0.0.1:8009/api/users/login"
data = {
    "username": "admin",
    "password": "admin123"
}

try:
    print(f"Sending POST to {url}")
    response = requests.post(url, json=data)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"Error: {e}")
