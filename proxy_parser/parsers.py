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
    'user_session': 'ltHnngOmNE_u6xWjJxxmz_KUQY0D7tma7_GdBj2um-77sHE6',
    '__Host-user_session_same_site': 'ltHnngOmNE_u6xWjJxxmz_KUQY0D7tma7_GdBj2um-77sHE6',
    'logged_in': 'yes',
    'dotcom_user': 'alexeyNaidiuk',
    'preferred_color_mode': 'dark',
    'tz': 'Europe%2FKiev',
    'has_recent_activity': '1',
    'color_mode': '%7B%22color_mode%22%3A%22auto%22%2C%22light_theme%22%3A%7B%22name%22%3A%22light%22%2C%22color_mode%22%3A%22light%22%7D%2C%22dark_theme%22%3A%7B%22name%22%3A%22dark%22%2C%22color_mode%22%3A%22dark%22%7D%7D',
    '_gh_sess': 'WrIJmVnYAGa2Wt9pAChSuSTMec4lqT5QOG9qDCdpt%2Bn9GJmJ81UungaS0i589Dj1JlMOmr%2FLj1YcZ7t5vHED9hZ1Ql%2BLH%2BMzzhwMCx35fP5%2FS1T7uDJjEskS7y38i%2FVb6ga3mcnYva0%2FMpAie01M79fuWbctghYnXamrrk91IgkkcJ7mH7g%2BPD0PGQ6fXKgAZFauPPEnqGeTQkETzpR60xueaEVBAthHGIu2lp7ixzZSC6jXQMtPsGeYYkqO%2FoLAbh%2Bzb%2FXbiCdZkrtRB8EAbmgu65AN2jM6TaumejFCMdj86a1GZdBz6APgRjFpNb87UBuH%2B60uvd2Hcmae9DaPIHA0d1yXHm6k--PaRGxVHOAaHgcnT4--vjiZXfPvcWSdfEedyhw3yA%3D%3D',
}

HEADERS = {
    'authority': 'github.com',
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'accept-language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
    # 'cookie': '_octo=GH1.1.2045407306.1670336220; _device_id=4080764a6f93b98d37a7aba816e05ad3; user_session=ltHnngOmNE_u6xWjJxxmz_KUQY0D7tma7_GdBj2um-77sHE6; __Host-user_session_same_site=ltHnngOmNE_u6xWjJxxmz_KUQY0D7tma7_GdBj2um-77sHE6; logged_in=yes; dotcom_user=alexeyNaidiuk; preferred_color_mode=dark; tz=Europe%2FKiev; has_recent_activity=1; color_mode=%7B%22color_mode%22%3A%22auto%22%2C%22light_theme%22%3A%7B%22name%22%3A%22light%22%2C%22color_mode%22%3A%22light%22%7D%2C%22dark_theme%22%3A%7B%22name%22%3A%22dark%22%2C%22color_mode%22%3A%22dark%22%7D%7D; _gh_sess=WrIJmVnYAGa2Wt9pAChSuSTMec4lqT5QOG9qDCdpt%2Bn9GJmJ81UungaS0i589Dj1JlMOmr%2FLj1YcZ7t5vHED9hZ1Ql%2BLH%2BMzzhwMCx35fP5%2FS1T7uDJjEskS7y38i%2FVb6ga3mcnYva0%2FMpAie01M79fuWbctghYnXamrrk91IgkkcJ7mH7g%2BPD0PGQ6fXKgAZFauPPEnqGeTQkETzpR60xueaEVBAthHGIu2lp7ixzZSC6jXQMtPsGeYYkqO%2FoLAbh%2Bzb%2FXbiCdZkrtRB8EAbmgu65AN2jM6TaumejFCMdj86a1GZdBz6APgRjFpNb87UBuH%2B60uvd2Hcmae9DaPIHA0d1yXHm6k--PaRGxVHOAaHgcnT4--vjiZXfPvcWSdfEedyhw3yA%3D%3D',
    'referer': 'https://github.com/alexeyNaidiuk/proxy_parser',
    'sec-ch-ua': '"Chromium";v="110", "Not A(Brand";v="24", "Google Chrome";v="110"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'same-origin',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36',
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
        file.writelines(iterable)


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
