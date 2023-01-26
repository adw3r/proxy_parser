import asyncio

import aiohttp

from proxy_parser import config

URL = 'http://ip-api.com/json/?fields=8217'


async def check_proxy(semaphore, proxy):
    try:
        async with semaphore:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(config.TIMEOUT)) as session:
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


async def check_proxies(proxies: set) -> set[str]:
    semaphore = asyncio.Semaphore(config.MAX_CONNECTIONS)
    tasks = []
    for proxy in proxies:
        try:
            tas = asyncio.create_task(check_proxy(proxy=proxy, semaphore=semaphore))
            tasks.append(tas)
        except:
            pass
    result = await asyncio.gather(*tasks)
    return set(p for p in result if p)
