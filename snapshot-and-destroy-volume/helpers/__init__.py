"""Shared helper utilities for cloud volume actions."""

import time


def wait_until(check, kwargs, cond, timeout=300, interval=5):
    """Wait until a condition is met.

    Args:
        check: Function to call to check the condition
        kwargs: Keyword arguments to pass to the check function
        cond: Condition function that returns True when satisfied
        timeout: Maximum time to wait in seconds (default: 300)
        interval: Time between checks in seconds (default: 5)

    Returns:
        Result from the check function when condition is met

    Raises:
        TimeoutError: If condition is not met within timeout period
    """
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            result = check(**kwargs)
            if cond(result):
                return result
        except Exception as e:
            pass
        time.sleep(interval)
    raise TimeoutError(f"Condition not met within {timeout} seconds")
