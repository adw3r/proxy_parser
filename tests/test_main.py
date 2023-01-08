from typing import Generator
from unittest import TestCase

from proxy_parser.parsers import get_proxies_from_links, get_proxies_with_proto, get_all_links_with_protos


class TestMain(TestCase):

    def test_get_all_links_with_protos_from_sources(self):
        all_links_with_proto: dict[str, tuple] = get_all_links_with_protos()
        self.assertIsInstance(all_links_with_proto, dict)

    def test_collect_proxies_from_links(self):
        all_links_with_proto: dict[str, tuple] = get_all_links_with_protos()
        for proto, links in all_links_with_proto.items():
            proxy_pools: Generator = get_proxies_from_links(links)
            for proxy_pool in proxy_pools:
                self.assertIn(':', proxy_pool)

    def test_get_all_proxies_with_protos(self):
        all_unchecked_proxies = get_proxies_with_proto()
        for proto, proxy_pool in all_unchecked_proxies.items():
            for proxy in proxy_pool:
                self.assertIn(proto, proxy)
