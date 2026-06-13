import uuid
import random
from utils.common import random_sleep
from utils.logger import get_logger

logger = get_logger("fingerprint")

def generate_uuid() -> str:
    return str(uuid.uuid4()).upper()

def generate_idfa() -> str:
    """生成合规iOS IDFA"""
    parts = [
        f"{random.getrandbits(32):08X}",
        f"{random.getrandbits(16):04X}",
        f"{random.getrandbits(16):04X}",
        f"{random.getrandbits(16):04X}",
        f"{random.getrandbits(48):012X}"
    ]
    return "-".join(parts)

class FingerPool:
    """指纹池，避免短时间重复"""
    def __init__(self, max_cache=500):
        self.pool = set()
        self.max_cache = max_cache

    def get_one(self):
        while len(self.pool) >= self.max_cache:
            self.pool.pop()
        idfa = generate_idfa()
        self.pool.add(idfa)
        random_sleep(0.1, 0.3)
        return idfa