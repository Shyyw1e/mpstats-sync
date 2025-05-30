import time
import logging

logger = logging.getLogger(__name__)

def retry(func, retries=3, delay=2, *args, **kwargs):
    for attempt in range(1, retries+1):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.warning(f"Attempt {attempt} failed: {e}")
            if attempt == retries:
                raise
            time.sleep(delay)
