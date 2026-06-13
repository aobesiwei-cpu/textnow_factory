import os
from dotenv import load_dotenv

load_dotenv()

# JWT
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "change-me-in-production")
JWT_EXPIRE_HOURS = int(os.getenv("JWT_EXPIRE_HOURS", "24"))

# Request & Concurrency
MAX_CONCURRENT_TASK = int(os.getenv("MAX_CONCURRENT_TASK", "5"))
REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "30"))
RETRY_TIMES = int(os.getenv("RETRY_TIMES", "3"))
POLL_INTERVAL_SEC = int(os.getenv("POLL_INTERVAL_SEC", "60"))

# Web Backend
WEB_HOST = "0.0.0.0"
WEB_PORT = 5000
DEBUG = False