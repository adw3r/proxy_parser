from pathlib import Path
from typing import Generator
from unittest import TestCase

from proxy_parser.config import SAVE_PATH
from proxy_parser.parsers import get_proxies_from_links, get_uncheked_proxies, append_string_to_file, \
    get_all_links_with_protos_and_clean_if_link_without_proxies

TEST_PROXY_SOURCE = 'https://github.com/Gripex-lee/CQhouse_data/raw/e28fdb7c9c61fe647e7e3e5c0cf5d9afc0d8fe6e/house_data/proxies.txt'


class TestMain(TestCase):

    def test_get_all_links_with_protos_from_sources(self):
        all_links_with_proto: dict[str, tuple] = get_all_links_with_protos_and_clean_if_link_without_proxies()
        self.assertIsInstance(all_links_with_proto, dict)

    def test_get_proxies_from_links(self):
        links = (TEST_PROXY_SOURCE,)
        proxies = get_proxies_from_links(links)
        for proxy in proxies:
            print(proxy)

    def test_collect_proxies_from_links(self):
        all_links_with_proto: dict[str, tuple] = get_all_links_with_protos_and_clean_if_link_without_proxies()
        for proto, links in all_links_with_proto.items():
            proxy_pools: Generator = get_proxies_from_links(links)
            for proxy_pool in proxy_pools:
                for proxy in proxy_pool:
                    self.assertIn(':', proxy)

    def test_get_all_proxies_with_protos(self):
        all_unchecked_proxies: tuple[str] = get_uncheked_proxies()
        for proxy in all_unchecked_proxies:
            self.assertIn('://', proxy)

    def test_append_proxy_to_file(self):
        proxy = 'https://123.123.123.123:8080'
        path_to_file = Path(SAVE_PATH, 'parsed.txt')
        append_string_to_file(path_to_file, proxy)
        self.assertTrue(path_to_file.exists())
