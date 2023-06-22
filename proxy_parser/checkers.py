import asyncio
from typing import AsyncGenerator

import aiohttp

from proxy_parser import config

URL = 'http://ip-api.com/json/?fields=8217'

semaphore = asyncio.BoundedSemaphore(config.MAX_CONNECTIONS)


async def check_proxy(session, proxy: str) -> tuple[str, dict] | None:
    try:
        async with config.SEMAPHORE:
            async with session.get(URL, proxy=proxy, timeout=aiohttp.ClientTimeout(20)) as response:
                json_response = await response.json()
                ip = json_response['query']
                if ip:
                    proxy_json_response = proxy, json_response
                    print(proxy_json_response)
                    return proxy_json_response
    except Exception as e:
        print(e)
        return None


async def check_proxies_generator(proxies: set[str]) -> AsyncGenerator:
    async with aiohttp.ClientSession() as session:
        cors = [check_proxy(session, proxy) for proxy in proxies]
        for result in asyncio.as_completed(cors):
            try:
                await_p = await result
                if await_p:
                    yield await_p
            except Exception as err:
                print(err)
                yield None
