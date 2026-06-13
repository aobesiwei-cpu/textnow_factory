import requests
from typing import Optional
from utils.logger import get_logger
from config.settings import REQUEST_TIMEOUT, RETRY_TIMES

logger = get_logger("http_client")

class HttpClient:
    def __init__(self, proxy: Optional[str] = None):
        self.proxy = proxy
        self.timeout = REQUEST_TIMEOUT
        self.retry = RETRY_TIMES
        self.session = requests.Session()

    def send(self, method: str, url: str, headers=None, json=None, data=None):
        proxies = {"http": self.proxy, "https": self.proxy} if self.proxy else None
        last_err = None
        for attempt in range(1, self.retry+1):
            try:
                resp = self.session.request(
                    method=method.upper(),
                    url=url,
                    headers=headers,
                    json=json,
                    data=data,
                    proxies=proxies,
                    timeout=self.timeout
                )
                return resp
            except Exception as e:
                last_err = e
                logger.warning(f"请求重试{attempt}次异常: {str(e)}")
        logger.error(f"请求最终失败 {url} | {str(last_err)}")
        return None