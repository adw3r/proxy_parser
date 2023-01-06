from concurrent.futures import ThreadPoolExecutor
from typing import Iterator

import requests

from proxy_parser.config import TIMEOUT, MAX_CONNECTIONS


def check_proxy(proxy) -> str | None:
    '''
    return proxy string if it works, either return None

    '''
    try:
        requests.get('http://api.ipify.org', proxies={'http': proxy, 'https': proxy}, timeout=TIMEOUT)
        print(proxy)
        return proxy
    except Exception as error:
        print(error)
        return None


def check_proxy_list(proxy_list: set) -> str:
    with ThreadPoolExecutor(MAX_CONNECTIONS) as worker:
        for proxy in worker.map(check_proxy, proxy_list):
            yield proxy
