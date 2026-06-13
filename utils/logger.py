import logging
from logging.handlers import RotatingFileHandler
import os

LOG_DIR = "data/logs"
os.makedirs(LOG_DIR, exist_ok=True)

def get_logger(name: str):
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    if logger.handlers:
        return logger

    log_file = os.path.join(LOG_DIR, f"{name}.log")
    # 单个日志最大100MB，最多保留5个轮转文件
    file_handler = RotatingFileHandler(
        log_file, maxBytes=100*1024*1024, backupCount=5, encoding="utf-8"
    )
    console_handler = logging.StreamHandler()

    fmt = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    file_handler.setFormatter(fmt)
    console_handler.setFormatter(fmt)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    return logger