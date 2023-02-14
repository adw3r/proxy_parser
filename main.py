import asyncio
from pathlib import Path
from typing import AsyncGenerator

from proxy_parser.checkers import check_proxies_generator
from proxy_parser.config import SAVE_PATH, MAIN_TIMEOUT, PATH_TO_SOURCES
from proxy_parser.parsers import get_uncheked_proxies, clear_file, \
    append_to_file, get_sources_from_github, append_iterable_to_file, clean_file_from_duplicates, get_lines_from_file

queries = {
    'filename:http_proxies.txt': 'http.txt',
    'filename:https_proxies.txt': 'https.txt',
    'filename:socks5_proxies.txt': 'socks5.txt',
    'filename:socks4_proxies.txt': 'socks4.txt',
}


async def main():
    await update_sources()

    path_to_file = Path(SAVE_PATH, 'parsed.txt')

    unchecked_proxies = get_uncheked_proxies()  # todo replace with aiohttp

    checked_proxies_generator: AsyncGenerator = check_proxies_generator(set(unchecked_proxies))
    clear_file(path_to_file)
    async for proxy, json_resp in checked_proxies_generator:
        print(proxy, json_resp)
        append_to_file(Path(path_to_file), proxy)

    checked_proxies = get_lines_from_file(path_to_file)

    checked_proxies_generator: AsyncGenerator = check_proxies_generator(set(checked_proxies))
    clear_file(path_to_file)
    async for proxy, json_resp in checked_proxies_generator:
        print(proxy, json_resp)
        append_to_file(Path(path_to_file), proxy)


async def update_sources():
    for query, file_name in queries.items():
        print(f'searching for {query}')
        links_form_github: set = set(link for link in get_sources_from_github(7, query) if link)
        if links_form_github:
            path_to_http_sources = Path(PATH_TO_SOURCES, file_name)
            append_iterable_to_file(path_to_http_sources, links_form_github)
            clean_file_from_duplicates(path_to_http_sources)


async def infinite_main():
    while True:
        print('started parsing!')
        await main()
        print('parsing ends!')
        await asyncio.sleep(MAIN_TIMEOUT)


if __name__ == '__main__':
    asyncio.run(infinite_main())
