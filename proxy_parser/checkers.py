from concurrent.futures import ThreadPoolExecutor
from typing import Generator

import requests

from proxy_parser.config import TIMEOUT, MAX_CONNECTIONS

URL = 'http://ip-api.com/json/?fields=8217'


def check_proxy(proxy) -> str | None:
    proxies = {'http': proxy, 'https': proxy}
    try:
        resp = requests.get(URL, proxies=proxies, timeout=TIMEOUT, allow_redirects=False)
        return proxy
    except Exception as error:
        return None


def check_proxy_list(proxy_list: tuple) -> Generator:
    with ThreadPoolExecutor(MAX_CONNECTIONS) as worker:
        for proxy in worker.map(check_proxy, proxy_list):
            if proxy:
                yield proxy
