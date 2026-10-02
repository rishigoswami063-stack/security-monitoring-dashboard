
import os
from pathlib import Path
from datetime import datetime, timedelta, timezone

import jwt
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent / ".env")

SECRET_KEY = os.getenv("JWT_SECRET_KEY")

if not SECRET_KEY:
    raise RuntimeError(
        "JWT_SECRET_KEY is missing. Check that backend/.env exists."
    )

payload = {
    "user_id": 1,
    "username": "admin",
    "role": "admin",
    "exp": datetime.now(timezone.utc) + timedelta(hours=1),
}

token = jwt.encode(
    payload,
    SECRET_KEY,
    algorithm="HS256",
)

print("JWT token created successfully.")

decoded = jwt.decode(
    token,
    SECRET_KEY,
    algorithms=["HS256"],
)

print("\nDecoded token:")
print(decoded)
