from unittest import TestCase

from proxy_parser.main import get_all_links_with_protos


class TestMain(TestCase):

    def test_get_all_links_with_protos_from_sources(self):
        all_links_with_proto: dict[str, tuple] = get_all_links_with_protos()
        self.assertIsInstance(all_links_with_proto, dict)
