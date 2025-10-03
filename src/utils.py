import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

def get_retry(url: str, retries: int = 5, backoff_factor: float = 0.5, timeout: int = 30, **kwargs) -> requests.Response:
    """
    Perform a GET request with automatic retries and exponential backoff.

    Retry logic:
        sleep_time = backoff_factor * (2 ** (retry_number - 1))
    Args:
        url (str): The full URL to fetch.
        retries (int, optional): Maximum number of retry attempts. Defaults to 5.
        backoff_factor (float, optional): Base factor for exponential backoff. Defaults to 0.5.
        timeout (int, optional): Timeout in seconds for the request. Defaults to 30.
        **kwargs: Additional keyword arguments passed directly to `requests.get()`.
            Examples:
                - stream=True (for large files)
                - headers={'User-Agent': '...'}
                - params={'key': 'value'}
    """
    session = requests.Session()
    retry = Retry(
        total=retries,
        read=retries,
        connect=retries,
        backoff_factor=backoff_factor,
        status_forcelist=(500, 502, 503, 504),
        allowed_methods=("GET",),
        raise_on_status=False
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("https://", adapter)

    response = session.get(url, timeout=timeout, **kwargs)

    return response

def deduplicate(data_list, key_attr: str):
    """
    Deduplicate a list of objects based on a specified attribute.

    Keeps the first occurrence of each unique key.
    """
    seen = set()
    deduped = []
    for item in data_list:
        key_val = getattr(item, key_attr, None)
        if key_val is None:
            deduped.append(item)
        elif key_val not in seen:
            deduped.append(item)
            seen.add(key_val)
    return deduped