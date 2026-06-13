import os
from dotenv import load_dotenv

load_dotenv()

# JWT
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
JWT_EXPIRE_HOURS = int(os.getenv("JWT_EXPIRE_HOURS"))

# 请求&并发
MAX_CONCURRENT_TASK = int(os.getenv("MAX_CONCURRENT_TASK"))
REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT"))
RETRY_TIMES = int(os.getenv("RETRY_TIMES"))
POLL_INTERVAL_SEC = int(os.getenv("POLL_INTERVAL_SEC"))

# Web后台
WEB_HOST = "0.0.0.0"
WEB_PORT = 5000
DEBUG = False