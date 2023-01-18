from typing import Generator
from unittest import TestCase

from proxy_parser.checkers import check_proxy, check_proxy_list
from proxy_parser.parsers import get_proxies_from_link

TEST_PROXIES_SOURCE = 'https://spys.me/proxy.txt'
TEST_PROXY = ''


class TestChecker(TestCase):

    def test_proxy_checker(self):
        proxy_checked: str | None = check_proxy(TEST_PROXY)
        self.assertIsNotNone(proxy_checked)

    def test_proxy_list_checker(self):
        proxies: tuple = tuple(set(f'http://{p}' for p in get_proxies_from_link(TEST_PROXIES_SOURCE)))
        proxy_list: Generator[str] = check_proxy_list(proxies)
        for proxy in proxy_list:
            self.assertIsNotNone(proxy)
