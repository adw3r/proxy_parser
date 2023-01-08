from concurrent.futures import ThreadPoolExecutor
from typing import Iterator, Generator

import requests

from proxy_parser.config import TIMEOUT, MAX_CONNECTIONS


def check_proxy(proxy) -> str | None:
    try:
        requests.get('http://api.ipify.org', proxies={'http': proxy, 'https': proxy}, timeout=TIMEOUT)
        return proxy
    except Exception as error:
        return None


def check_proxy_list(proxy_list: set) -> Generator[str]:
    with ThreadPoolExecutor(MAX_CONNECTIONS) as worker:
        for proxy in worker.map(check_proxy, proxy_list):
            if proxy:
                yield proxy
