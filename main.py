import asyncio
import os
from pathlib import Path
from time import sleep

import aiohttp

import proxy_parser.config
from proxy_parser.checkers import check_proxy_list, URL
from proxy_parser.config import SAVE_PATH, MAIN_TIMEOUT
from proxy_parser.parsers import get_uncheked_proxies, append_string_to_file, clean_file, get_sources_from_github, \
    PATH_TO_SOURCES, save_iterable_to_tile


async def check_proxy(semaphore, proxy):
    async with semaphore:
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(10)) as session:
                response = await session.get(URL, proxy=proxy)
                try:
                    json_response = await response.json()
                    ip = json_response['query']
                    if ip:
                        print(proxy)
                        return proxy
                except Exception as e:
                    # logging.exception(e)
                    pass
        except Exception as e:
            # logging.exception(e)
            pass


async def check_proxies(proxies):
    semaphore = asyncio.Semaphore(proxy_parser.config.MAX_CONNECTIONS)
    tasks = []
    for proxy in proxies:
        tasks.append(asyncio.create_task(check_proxy(proxy=proxy, semaphore=semaphore)))
    result = await asyncio.gather(*tasks)
    return [p for p in result if p]


async def main():
    for link in get_sources_from_github(15):
        if not link:
            break
        print(link)
        append_string_to_file(Path(PATH_TO_SOURCES, 'http.txt'), link)
    path_to_file = Path(SAVE_PATH, 'parsed.txt')
    unchecked_proxies = get_uncheked_proxies()
    print(f'proxies found {len(unchecked_proxies)}')
    checked_proxies = await check_proxies(unchecked_proxies)
    save_iterable_to_tile(path_to_file, checked_proxies)
    clean_file(path_to_file)


async def infinite_main():
    while True:
        print('started parsing!')
        await main()
        print('parsing ends!')
        await asyncio.sleep(MAIN_TIMEOUT)


if __name__ == '__main__':
    asyncio.run(infinite_main())
