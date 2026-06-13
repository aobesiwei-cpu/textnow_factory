import time
import random
from datetime import datetime

def now_str(fmt: str = "%Y-%m-%d %H:%M:%S") -> str:
    return datetime.now().strftime(fmt)

def random_sleep(min_s: float = 1, max_s: float = 3):
    time.sleep(random.uniform(min_s, max_s))

def batch_chunk(lst: list, size: int):
    """列表分批"""
    for i in range(0, len(lst), size):
        yield lst[i:i+size]