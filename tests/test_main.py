from pathlib import Path
from typing import Generator
from unittest import TestCase

from proxy_parser.checkers import check_proxy_list
from proxy_parser.config import SAVE_PATH
from proxy_parser.main import main
from proxy_parser.parsers import get_proxies_from_links, get_uncheked_proxies_with_proto, get_all_links_with_protos, \
    append_proxy_to_file


class TestMain(TestCase):

    def test_get_all_links_with_protos_from_sources(self):
        all_links_with_proto: dict[str, tuple] = get_all_links_with_protos()
        self.assertIsInstance(all_links_with_proto, dict)

    def test_collect_proxies_from_links(self):
        all_links_with_proto: dict[str, tuple] = get_all_links_with_protos()
        for proto, links in all_links_with_proto.items():
            proxy_pools: Generator = get_proxies_from_links(links)
            for proxy_pool in proxy_pools:
                for proxy in proxy_pool:
                    self.assertIn(':', proxy)

    def test_get_all_proxies_with_protos(self):
        all_unchecked_proxies: dict[str, tuple] = get_uncheked_proxies_with_proto()
        for proto, proxy_pool in all_unchecked_proxies.items():
            for proxy in proxy_pool:
                self.assertIn(proto, proxy)

    def test_get_checked_proxies(self):
        all_unchecked_proxies_with_proto = get_uncheked_proxies_with_proto()

        for proto, proxy_pool in all_unchecked_proxies_with_proto.items():
            checked_proxies = check_proxy_list(proxy_pool)
            for proxy in checked_proxies:
                self.assertIn('://', proxy)

    def test_append_proxy_to_file(self):
        proxy = 'https://123.123.123.123:8080'
        path_to_file = Path(SAVE_PATH, 'parsed.txt')
        append_proxy_to_file(path_to_file, proxy)
        self.assertTrue(path_to_file.exists())

    def test_parsed_file_creates_after_main(self):
        main()
        path = Path(SAVE_PATH, 'parsed.txt')
        self.assertTrue(path.exists())
