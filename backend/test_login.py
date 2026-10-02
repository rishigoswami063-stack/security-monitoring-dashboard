import requests

response = requests.post(
    "http://127.0.0.1:5000/api/login",
    json={
        "username": "admin",
        "password": "admin123"
    }
)

print(response.status_code)
print(response.json())