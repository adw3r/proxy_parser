from pathlib import Path
from typing import Generator
from unittest import TestCase

from proxy_parser.config import PATH_TO_SOURCES
from proxy_parser.parsers import get_files_from_folder, get_proxies_from_link, get_links_from_file

TEST_PROXIES_SOURCE = 'https://github.com/keyaanminhas/ka4mas_inventory/raw/1fce10b92fb9f8b38d5f11315bdcb8f15788fb7d/GMAIL/config/proxies.txt'


class TestParsers(TestCase):

    def test_get_list_of_files_with_sources(self):
        '''
        получаем список всех файлов с источниками проксей

        '''

        list_of_files: tuple = get_files_from_folder(PATH_TO_SOURCES)
        self.assertIn(Path(PATH_TO_SOURCES, 'http.txt'), list_of_files)
        self.assertIn(Path(PATH_TO_SOURCES, 'socks4.txt'), list_of_files)
        self.assertIn(Path(PATH_TO_SOURCES, 'socks5.txt'), list_of_files)

    def test_get_sources_list_from_text_file(self):
        '''
        получаем источники проксей из файлов и проверяем что это ссылки

        '''

        list_of_files: tuple = get_files_from_folder(PATH_TO_SOURCES)

        for file in list_of_files:
            sources: set = get_links_from_file(Path(PATH_TO_SOURCES, file))
            for source in sources:
                self.assertIn('http', source)

    def test_get_proxy_from_link(self):
        '''
        получаем список проксей из источника

        '''

        proxies: Generator = get_proxies_from_link(TEST_PROXIES_SOURCE)
        for p in proxies:
            self.assertIn(':', p)
