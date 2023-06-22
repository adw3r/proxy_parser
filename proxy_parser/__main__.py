import asyncio
import datetime
from typing import AsyncGenerator

from proxy_parser import config, parsers, checkers
from proxy_parser.parsers import get_uncheked_proxies


async def check_proxies():
    unchecked_proxies_set = await get_uncheked_proxies()
    checked_proxies_generator: AsyncGenerator = checkers.check_proxies_generator(unchecked_proxies_set)
    parsers.clear_file(config.CHECKED_PROXIES_FILE)
    async for proxy, json_resp in checked_proxies_generator:
        print(proxy, json_resp)
        parsers.append_to_file(config.CHECKED_PROXIES_FILE, proxy)


async def main():
    # await update_sources()
    await parsers.parse_unchecked_proxies()
    await check_proxies()


async def infinite_main():
    while True:
        print('started parsing!')
        await main()
        awaiking_time = datetime.datetime.now() + datetime.timedelta(seconds=config.INF_MAIN_TIMEOUT_SECONDS)
        print(f'parsing will start at {awaiking_time}!')
        await asyncio.sleep(config.INF_MAIN_TIMEOUT_SECONDS)


if __name__ == '__main__':
    asyncio.run(infinite_main())
