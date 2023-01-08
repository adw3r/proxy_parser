import os
from pathlib import Path

import requests

from proxy_parser.config import REGEX_PATTERN


def get_files_from_folder(path_to_folder: Path | str) -> tuple[Path]:
    return tuple(Path(path_to_folder, str(file)) for file in os.listdir(path_to_folder))


def get_links_from_file(path_to_file: Path | str) -> set[str]:
    with open(path_to_file) as file:
        return set(file.read().splitlines())


def get_proxies_from_link(source_link: str) -> set[str]:
    response = requests.get(source_link)
    text = response.text
    proxies = {proxy.group(1) for proxy in set(REGEX_PATTERN.finditer(text))}
    return proxies
