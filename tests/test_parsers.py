from pathlib import Path
from unittest import TestCase

from proxy_parser.parsers import get_files_from_folder, get_proxies_from_link, get_links_from_file

TEST_PROXIES_SOURCE = 'https://github.com/keyaanminhas/ka4mas_inventory/raw/1fce10b92fb9f8b38d5f11315bdcb8f15788fb7d/GMAIL/config/proxies.txt'

TEST_SOURCES_FOLDER_PATH = r'C:\Users\Administrator\Desktop\proxy-scraper-checker\test_sources'


class TestParsers(TestCase):

    def test_get_list_of_files_with_sources(self):
        '''
        получаем список всех файлов с источниками проксей

        '''

        list_of_files: tuple = get_files_from_folder(TEST_SOURCES_FOLDER_PATH)
        self.assertIn(Path(TEST_SOURCES_FOLDER_PATH, 'http.txt'), list_of_files)
        self.assertIn(Path(TEST_SOURCES_FOLDER_PATH, 'socks4.txt'), list_of_files)
        self.assertIn(Path(TEST_SOURCES_FOLDER_PATH, 'socks5.txt'), list_of_files)

    def test_get_sources_list_from_text_file(self):
        '''
        получаем источники проксей из файлов и проверяем что это ссылки

        '''

        list_of_files: tuple = get_files_from_folder(TEST_SOURCES_FOLDER_PATH)

        for file in list_of_files:
            sources: set = get_links_from_file(Path(TEST_SOURCES_FOLDER_PATH, file))
            for source in sources:
                self.assertIn('http', source)

    def test_get_proxy_list_from_link(self):
        '''
        получаем список проксей из источника

        '''

        proxies: set = get_proxies_from_link(TEST_PROXIES_SOURCE)
        self.assertIn('167.235.63.238:3128', proxies)

    def test_regex_kinda(self):
        '''
        интеграционный тест всех трёх функций вместе

        '''
        for file in get_files_from_folder(TEST_SOURCES_FOLDER_PATH):
            for link in get_links_from_file(file):
                for proxy in get_proxies_from_link(link):
                    self.assertIn(':', proxy)
