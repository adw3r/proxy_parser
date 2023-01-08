import os
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Generator

import requests

from proxy_parser.config import REGEX_PATTERN


def get_files_from_folder(path_to_folder: Path | str) -> tuple[Path]:
    return tuple(Path(path_to_folder, str(file)) for file in os.listdir(path_to_folder))


def get_links_from_file(path_to_file: Path | str) -> tuple[str]:
    with open(path_to_file) as file:
        return tuple(set(file.read().splitlines()))


def get_proxies_from_link(source_link: str) -> Generator | None:
    try:
        response = requests.get(source_link)
        text = response.text
        for proxy in set(REGEX_PATTERN.finditer(text)):
            yield proxy.group(1)
    except Exception as error:
        print(error)
        return None


def get_proxies_from_links(links: set[str]) -> Generator:
    with ThreadPoolExecutor(len(links)) as worker:
        for res in worker.map(get_proxies_from_link, links):
            yield res
