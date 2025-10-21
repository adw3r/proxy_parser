"""
Proxy checking functionality.
"""

import asyncio
import logging
from typing import AsyncGenerator, Tuple, Optional, Dict, Any

from proxy_parser.config import PROXY_CHECK_URL, PROXY_CHECK_TIMEOUT
from proxy_parser.http_client import http_client

logger = logging.getLogger(__name__)


class ProxyChecker:
    """Handles proxy checking operations."""

    def __init__(self, timeout: int = PROXY_CHECK_TIMEOUT):
        self.timeout = timeout

    async def check_proxy(self, proxy: str) -> tuple[str, dict[str, Any], float] | None:
        """
        Check if a proxy is working.

        Args:
            proxy: Proxy string in format protocol://ip:port

        Returns:
            Tuple of (proxy, response_data) or None if check failed
        """
        logger.debug(f"Checking proxy: {proxy}")
        start_time = asyncio.get_event_loop().time()

        try:
            json_response = await http_client.get_json(
                PROXY_CHECK_URL, proxy=proxy, timeout=self.timeout
            )
            elapsed_time: float = asyncio.get_event_loop().time() - start_time

            if json_response and "query" in json_response:
                ip = json_response["query"]
                if ip:
                    logger.debug(
                        f"✓ Proxy {proxy} is working, IP: {ip}, Time: {elapsed_time:.2f}s"
                    )
                    return proxy, json_response, elapsed_time
                else:
                    logger.debug(
                        f"✗ Proxy {proxy} returned no IP, Time: {elapsed_time:.2f}s"
                    )
            else:
                logger.debug(
                    f"✗ Proxy {proxy} returned invalid response, Time: {elapsed_time:.2f}s"
                )

        except Exception as e:
            elapsed_time = asyncio.get_event_loop().time() - start_time
            logger.debug(
                f"✗ Error checking proxy {proxy}: {e}, Time: {elapsed_time:.2f}s"
            )

        return None

    async def check_proxies_generator(
        self, proxies: set[str]
    ) -> AsyncGenerator[tuple[str, dict[str, Any], float], None]:
        """
        Check multiple proxies concurrently.

        Args:
            proxies: Set of proxy strings

        Yields:
            Tuples of (proxy, response_data) for working proxies
        """
        logger.info(f"Starting to check {len(proxies)} proxies concurrently")
        start_time = asyncio.get_event_loop().time()

        # Create tasks for all proxies
        tasks = [self.check_proxy(proxy) for proxy in proxies]

        # Process results as they complete
        working_count = 0
        failed_count = 0

        for result in asyncio.as_completed(tasks):
            try:
                proxy_result = await result
                if proxy_result:
                    working_count += 1
                    yield proxy_result
                else:
                    failed_count += 1
            except Exception as e:
                failed_count += 1
                logger.error(f"✗ Error in proxy checking task: {e}")

        elapsed_time = asyncio.get_event_loop().time() - start_time
        logger.info(
            f"✓ Proxy checking completed - {working_count} working, {failed_count} failed in {elapsed_time:.2f}s"
        )
