import asyncio
from pathlib import Path

from proxy_parser.checkers import check_proxies
from proxy_parser.config import SAVE_PATH, MAIN_TIMEOUT, PATH_TO_SOURCES
from proxy_parser.parsers import get_uncheked_proxies, get_sources_from_github, save_iterable_to_file


async def main():
    queries = {
        'filename:http_proxies.txt': 'http.txt',
        'filename:https_proxies.txt': 'https.txt',
        'filename:socks4_proxies.txt': 'socks4.txt',
        'filename:socks5_proxies.txt': 'socks5.txt'
    }
    for query, file_name in queries.items():
        print(f'searching for {query}')
        links_form_github: set = set(link for link in get_sources_from_github(12, query) if link)
        path_to_http_sources = Path(PATH_TO_SOURCES, file_name)
        save_iterable_to_file(path_to_http_sources, set(links_form_github))

    unchecked_proxies = get_uncheked_proxies()
    print(f'proxies were found {len(unchecked_proxies)}')

    path_to_file = Path(SAVE_PATH, 'parsed.txt')
    checked_proxies: set = await check_proxies(unchecked_proxies)
    print('double checking proxies')
    checked_proxies: set = await check_proxies(checked_proxies)
    save_iterable_to_file(path_to_file, checked_proxies)


async def infinite_main():
    while True:
        print('started parsing!')
        await main()
        print('parsing ends!')
        await asyncio.sleep(MAIN_TIMEOUT)


if __name__ == '__main__':
    asyncio.run(infinite_main())
