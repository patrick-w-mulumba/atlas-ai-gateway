from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)


def retry_policy():
    return retry(
        retry=retry_if_exception_type(
            (TimeoutError, ConnectionError),
        ),
        wait=wait_exponential(
            multiplier=0.5,
            min=0.5,
            max=4,
        ),
        stop=stop_after_attempt(3),
        reraise=True,
    )
