
import os
from pathlib import Path
from datetime import datetime, timedelta, timezone

import jwt
import requests
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent / ".env")

BASE_URL = "http://127.0.0.1:5000"
SECRET_KEY = os.getenv("JWT_SECRET_KEY")

if not SECRET_KEY:
    raise RuntimeError(
        "JWT_SECRET_KEY is missing. Check that backend/.env exists."
    )

# Generate a JWT token for testing
payload = {
    "user_id": 1,
    "username": "admin",
    "role": "admin",
    "exp": datetime.now(timezone.utc) + timedelta(hours=1),
}

token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")

headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {token}",
}

# Test incident status update
incident_id = 2

response = requests.patch(
    f"{BASE_URL}/api/incidents/{incident_id}/status",
    headers=headers,
    json={"status": "Investigating"},
    timeout=10,
)

print("HTTP Status:", response.status_code)
print("Response:")
print(response.text)
