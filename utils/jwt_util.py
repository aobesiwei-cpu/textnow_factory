from datetime import datetime, timedelta
import jwt
from config.settings import JWT_SECRET_KEY, JWT_EXPIRE_HOURS

def generate_token(admin_id: int, username: str) -> str:
    exp = datetime.utcnow() + timedelta(hours=JWT_EXPIRE_HOURS)
    payload = {
        "admin_id": admin_id,
        "username": username,
        "exp": exp
    }
    token = jwt.encode(payload, JWT_SECRET_KEY, algorithm="HS256")
    return token

def verify_token(token: str):
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=["HS256"])
        return payload
    except Exception:
        return None