import asyncio
from typing import AsyncGenerator

import aiohttp

from proxy_parser import config

URL = 'http://ip-api.com/json/?fields=8217'


async def check_proxy(semaphore: asyncio.Semaphore, proxy: str) -> str | None:
    try:
        async with semaphore:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(config.TIMEOUT)) as session:
                async with session.get(URL, proxy=proxy) as response:
                    json_response = await response.json()
                    ip = json_response['query']
                    if ip:
                        return proxy, json_response
    except Exception as e:
        return None


async def check_proxies_generator(proxies: set) -> AsyncGenerator:
    semaphore = asyncio.Semaphore(config.MAX_CONNECTIONS)
    tasks = []
    for proxy in proxies:
        tas = asyncio.create_task(check_proxy(proxy=proxy, semaphore=semaphore))
        tasks.append(tas)
    for p in asyncio.as_completed(tasks):
        await_p = None
        try:
            await_p = await p
        except:
            pass
        if await_p:
            yield await_p
