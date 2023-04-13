import json
import os
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Generator, NoReturn, Iterable

import requests
from bs4 import BeautifulSoup

from proxy_parser.config import PATH_TO_SOURCES
from proxy_parser.config import REGEX_PATTERN

protos = ('http://', 'https://', 'socks4://', 'socks5://')

COOKIES = {
    '_octo': 'GH1.1.2045407306.1670336220',
    '_device_id': '4080764a6f93b98d37a7aba816e05ad3',
    'user_session': 'GJ2FquNK2R7LQszFIYzptfpN0wfc8zUgOEk89qHJoPXfzcKh',
    '__Host-user_session_same_site': 'GJ2FquNK2R7LQszFIYzptfpN0wfc8zUgOEk89qHJoPXfzcKh',
    'logged_in': 'yes',
    'dotcom_user': 'adw3r',
    'has_recent_activity': '1',
    'color_mode': '%7B%22color_mode%22%3A%22dark%22%2C%22light_theme%22%3A%7B%22name%22%3A%22light%22%2C%22color_mode%22%3A%22light%22%7D%2C%22dark_theme%22%3A%7B%22name%22%3A%22dark_dimmed%22%2C%22color_mode%22%3A%22dark%22%7D%7D',
    'preferred_color_mode': 'dark',
    'tz': 'Europe%2FKiev',
    '_gh_sess': 'lxCBQn3nPCar9NLkiJyetDqWpLlBqP4%2BcH%2BKhI2hB%2Bk4LY6WeKtLMwpvUs8CKxaOq1jw5utX5gXzSJ0tLMXyFQJD%2B%2B4aH2b8%2Bwt%2B7ihBw%2BOsF6DRZsxnWLIOb8Pdvg%2FuZncbjHftP4LSxlzQvDTydh%2BMnqwWR3pt20pwQzt6%2FyCu6XLZKpStLmxrxPdQbzj4vAREwOHrOuxT4EQkj3s0qzpztbU%2FESv%2BJOLRhmte36qaIw2QzS5l2sgZilRyfYgAfXF4HQ44mqtgXSpyCpyQHOzftgTc1yuMogpgaA16TTYUmKn5etBVXEuBMS9RbLI6guUMoKAy5bSFTE1AjA%3D%3D--ku2G%2B9n9xkQwdSp1--YS50c%2B8VobLzP5XOENOi%2Fw%3D%3D',
}

HEADERS = {
    'authority': 'github.com',
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'accept-language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
    'cache-control': 'max-age=0',
    # 'cookie': '_octo=GH1.1.2045407306.1670336220; _device_id=4080764a6f93b98d37a7aba816e05ad3; user_session=GJ2FquNK2R7LQszFIYzptfpN0wfc8zUgOEk89qHJoPXfzcKh; __Host-user_session_same_site=GJ2FquNK2R7LQszFIYzptfpN0wfc8zUgOEk89qHJoPXfzcKh; logged_in=yes; dotcom_user=adw3r; has_recent_activity=1; color_mode=%7B%22color_mode%22%3A%22dark%22%2C%22light_theme%22%3A%7B%22name%22%3A%22light%22%2C%22color_mode%22%3A%22light%22%7D%2C%22dark_theme%22%3A%7B%22name%22%3A%22dark_dimmed%22%2C%22color_mode%22%3A%22dark%22%7D%7D; preferred_color_mode=dark; tz=Europe%2FKiev; _gh_sess=lxCBQn3nPCar9NLkiJyetDqWpLlBqP4%2BcH%2BKhI2hB%2Bk4LY6WeKtLMwpvUs8CKxaOq1jw5utX5gXzSJ0tLMXyFQJD%2B%2B4aH2b8%2Bwt%2B7ihBw%2BOsF6DRZsxnWLIOb8Pdvg%2FuZncbjHftP4LSxlzQvDTydh%2BMnqwWR3pt20pwQzt6%2FyCu6XLZKpStLmxrxPdQbzj4vAREwOHrOuxT4EQkj3s0qzpztbU%2FESv%2BJOLRhmte36qaIw2QzS5l2sgZilRyfYgAfXF4HQ44mqtgXSpyCpyQHOzftgTc1yuMogpgaA16TTYUmKn5etBVXEuBMS9RbLI6guUMoKAy5bSFTE1AjA%3D%3D--ku2G%2B9n9xkQwdSp1--YS50c%2B8VobLzP5XOENOi%2Fw%3D%3D',
    'if-none-match': 'W/"1be92b25f6984e8763cc7f183a293e8c"',
    'referer': 'https://github.com/jetkai/proxy-list',
    'sec-ch-ua': '"Chromium";v="112", "Google Chrome";v="112", "Not:A-Brand";v="99"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'same-origin',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36',
}


def clear_file(path_to_file):
    with open(path_to_file, 'w') as f:
        f.write('')


def append_to_file(path_to_file, item: str):
    with open(path_to_file, 'a') as file:
        file.write(f'{item}\n')


def get_lines_from_file(path_to_file) -> set:
    with open(path_to_file) as f:
        return set(f.read().strip().splitlines())


def append_iterable_to_file(path_to_file: Path, iterable: set):
    with open(path_to_file, 'a') as file:
        for line in iterable:
            file.write(f'\n{line}')


def save_iterable_to_file(path_to_file: Path, iterable: set):
    with open(path_to_file, 'w') as file:
        file.write('\n'.join(iterable))


def find_source_in_response(response: requests.Response) -> str | None:
    soup = BeautifulSoup(response.text, 'lxml')
    container = soup.find('div', {'id': 'code_search_results'})
    all_a = container.find_all('a')
    for a in all_a:
        values = a.get('data-hydro-click')
        if values:
            loads = json.loads(values)
            url = loads['payload']['result']['url']
            yield url


def get_sources_from_github(depth: int = 10, query: str = 'filename:proxies.txt') -> Generator:
    for p in range(depth):
        params = {
            'p': p,
            'o': 'desc',
            'q': query,
            's': 'indexed',
            'type': 'Code',
        }
        try:
            response = requests.get('https://github.com/search', params=params, cookies=COOKIES, headers=HEADERS,
                                    timeout=10)
            for url in find_source_in_response(response):
                print(url)
                yield url
        except Exception as e:
            print(e)
            yield None


def clean_file_from_duplicates(path_to_file: Path | str) -> NoReturn:
    with open(path_to_file) as file:
        iterable = set(file.read().split('\n'))
        if '' in iterable:
            iterable.remove('')
    with open(path_to_file, 'w') as file:
        file.write('\n'.join(iterable))


def get_files_from_folder(path_to_folder: Path | str) -> tuple[Path]:
    return tuple(Path(path_to_folder, str(file)) for file in os.listdir(path_to_folder))


def get_links_from_file(path_to_file: Path | str) -> tuple[str]:
    clean_file_from_duplicates(path_to_file)
    with open(path_to_file) as file:
        return tuple(set(file.read().split('\n')))


def get_proxies_from_link(source_link: str) -> tuple | None:
    try:
        response = requests.get(source_link, timeout=10)
        text = response.text
        proxies = tuple(set(proxy.group(1) for proxy in set(REGEX_PATTERN.finditer(text))))
        return proxies
    except Exception as error:
        print(error)
        return None


def get_proxies_from_links(links: tuple[str]) -> Generator:
    with ThreadPoolExecutor(len(links)) as worker:
        for res in worker.map(get_proxies_from_link, links):
            yield res


def save_iterable(file_name, iterable: Iterable):
    with open(file_name, 'w') as file_name:
        file_name.write('\n'.join(iterable))


def check_source(link):
    proxies = get_proxies_from_link(link)
    if proxies:
        return link


def get_uncheked_proxies() -> set[str]:
    proxies = set()
    all_links_with_proto: dict[str, tuple] = get_all_links_with_protos_and_clean_if_link_without_proxies()
    for proto, links in all_links_with_proto.items():
        for pool in get_proxies_from_links(links):
            if not pool:
                continue
            for proxy in pool:
                proxy = proxy if any(p in proxy for p in protos) else f'{proto}://{proxy}'
                proxies.add(str(proxy))

    return proxies


def get_all_links_with_protos_and_clean_if_link_without_proxies() -> dict[str, tuple]:
    files = {}
    folder = get_files_from_folder(PATH_TO_SOURCES)

    for file in folder:
        file_name = file.name.removesuffix('.txt')
        files[file_name] = tuple(link for link in get_links_from_file(file))

        with ThreadPoolExecutor(len(files[file_name])) as worker:
            with_proxies = worker.map(check_source, files[file_name])

        sources_with_proxies = [link for link in with_proxies if link]
        save_iterable(file, sources_with_proxies)

    return files
