import os
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Generator, NoReturn

import requests

from proxy_parser.config import PATH_TO_SOURCES
from proxy_parser.config import REGEX_PATTERN


def append_proxy_to_file(path_to_file: Path | str, proxy: str) -> NoReturn:
    with open(path_to_file, 'a') as file:
        file.write(f'{proxy}\n')


def clean_file(path_to_file: Path | str) -> NoReturn:
    with open(path_to_file) as file:
        iterable = set(file.read().split('\n'))
        iterable.remove('')
    with open(path_to_file, 'w') as file:
        file.write('\n'.join(iterable))


def get_files_from_folder(path_to_folder: Path | str) -> tuple[Path]:
    return tuple(Path(path_to_folder, str(file)) for file in os.listdir(path_to_folder))


def get_links_from_file(path_to_file: Path | str) -> tuple[str]:
    with open(path_to_file) as file:
        return tuple(set(file.read().splitlines()))


def get_proxies_from_link(source_link: str) -> tuple | None:
    try:
        response = requests.get(source_link)
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


def get_uncheked_proxies() -> tuple[str]:
    proxies = set()

    all_links_with_proto: dict[str, tuple] = get_all_links_with_protos()
    for proto, links in all_links_with_proto.items():
        for pool in get_proxies_from_links(links):
            for proxy in pool:
                proxies.add(f'{proto}://{proxy}')

    return tuple(proxies)


def get_all_links_with_protos() -> dict[str, tuple]:
    files = {}

    for file in get_files_from_folder(PATH_TO_SOURCES):
        file_name = file.name.removesuffix('.txt')
        files[file_name] = tuple(link for link in get_links_from_file(file))

    return files
