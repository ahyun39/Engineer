# utils.py
import time
from typing import Iterable, List

def chunked(iterable: Iterable, n: int) -> List[List]:
    """Split iterable into chunks of size n."""
    chunk = []
    res = []
    for item in iterable:
        chunk.append(item)
        if len(chunk) >= n:
            res.append(chunk)
            chunk = []
    if chunk:
        res.append(chunk)
    return res

def safe_sleep(retries: int = 1):
    """Backoff helper for rate-limit handling."""
    time.sleep(1 + 2 * retries)