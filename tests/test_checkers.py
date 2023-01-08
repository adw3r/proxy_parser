from typing import Generator
from unittest import TestCase

from proxy_parser.checkers import check_proxy, check_proxy_list
from proxy_parser.parsers import get_proxies_from_link

TEST_PROXIES_SOURCE = 'https://github.com/jetkai/proxy-list/raw/106ec51ef12130fdcde68c855fad37ecdaa2fd28/online-proxies/txt/proxies-http.txt'
TEST_PROXY = ''


class TestChecker(TestCase):

    def test_proxy_checker(self):

        proxy_checked = check_proxy(TEST_PROXY)
        self.assertIsNotNone(proxy_checked)

    def test_proxy_list_checker(self):
        proxies = set(f'http://{p}' for p in get_proxies_from_link(TEST_PROXIES_SOURCE))
        proxy_list: Generator = check_proxy_list(proxies)
        for proxy in proxy_list:
            self.assertIsNotNone(proxy)
