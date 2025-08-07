"""
HTTP client utilities for proxy parsing.
"""

import time
import asyncio
from typing import Optional, Dict, Any, List
import httpx
import requests
from bs4 import BeautifulSoup
from loguru import logger

from proxy_parser.config import SEMAPHORE, DEFAULT_HEADERS, MAX_CONNECTIONS


class HTTPClient:
    """HTTP client for making requests with proper error handling."""

    def __init__(self, headers: Optional[Dict[str, str]] = None):
        self.headers = headers or DEFAULT_HEADERS.copy()

    async def get_text(self, url: str, timeout: int = 10) -> Optional[str]:
        """
        Fetch text content from URL with proper error handling.

        Args:
            url: URL to fetch
            timeout: Request timeout in seconds

        Returns:
            Text content or None if request failed
        """
        logger.debug(f"Making GET request to: {url}")
        start_time = asyncio.get_event_loop().time()

        try:
            async with SEMAPHORE:
                timeout_config = httpx.Timeout(timeout)
                async with httpx.AsyncClient(
                    headers=self.headers, timeout=timeout_config, limits=httpx.Limits(max_connections=MAX_CONNECTIONS, max_keepalive_connections=MAX_CONNECTIONS)
                ) as client:
                    response = await client.get(url)
                    elapsed_time = asyncio.get_event_loop().time() - start_time

                    if response.status_code == 200:
                        content_length = len(response.text)
                        logger.info(
                            f"✓ GET {url} - Status: {response.status_code}, Size: {content_length} chars, Time: {elapsed_time:.2f}s"
                        )
                        return response.text
                    else:
                        logger.warning(
                            f"✗ GET {url} - Status: {response.status_code}, Time: {elapsed_time:.2f}s"
                        )
                        return None
        except httpx.TimeoutException:
            elapsed_time = asyncio.get_event_loop().time() - start_time
            logger.warning(f"✗ GET {url} - Timeout after {elapsed_time:.2f}s")
            return None
        except Exception as e:
            elapsed_time = asyncio.get_event_loop().time() - start_time
            logger.error(f"✗ GET {url} - Error: {e}, Time: {elapsed_time:.2f}s")
            return None

    async def get_json(
        self, url: str, proxy: str, timeout: int = 10
    ) -> Optional[Dict[str, Any]]:
        """
        Fetch JSON content from URL with optional proxy.

        Args:
            url: URL to fetch
            proxy: Optional proxy to use
            timeout: Request timeout in seconds

        Returns:
            JSON response or None if request failed
        """
        proxy_info = f" via {proxy}" if proxy else ""
        logger.debug(f"Making JSON GET request to: {url}{proxy_info}")
        start_time = asyncio.get_event_loop().time()

        try:
            async with SEMAPHORE:
                timeout_config = httpx.Timeout(timeout)

                # httpx uses proxy parameter directly
                if proxy.startswith(('http://', 'https://')):
                    proxy_url = proxy
                elif proxy.startswith('socks5://'):
                    # SOCKS5 proxies are supported with httpx[socks]
                    proxy_url = proxy
                elif proxy.startswith('socks4://'):
                    # httpx[socks] doesn't support SOCKS4, skip these
                    logger.warning(f"✗ JSON GET {url}{proxy_info} - SOCKS4 proxies not supported by httpx, skipping")
                    return None
                else:
                    # Assume HTTP proxy
                    proxy_url = f"http://{proxy}"

                async with httpx.AsyncClient(
                    headers=self.headers, 
                    timeout=timeout_config,
                    proxy=proxy_url, limits=httpx.Limits(
                            max_connections=MAX_CONNECTIONS, max_keepalive_connections=MAX_CONNECTIONS
                        )
                ) as client:
                    response = await client.get(url)
                    elapsed_time = asyncio.get_event_loop().time() - start_time

                    if response.status_code == 200:
                        try:
                            json_data = response.json()
                            logger.info(
                                f"✓ JSON GET {url}{proxy_info} - Status: {response.status_code}, Time: {elapsed_time:.2f}s"
                            )
                            return json_data
                        except Exception as e:
                            logger.error(
                                f"✗ JSON GET {url}{proxy_info} - Invalid JSON: {e}, Time: {elapsed_time:.2f}s"
                            )
                            return None
                    else:
                        logger.warning(
                            f"✗ JSON GET {url}{proxy_info} - Status: {response.status_code}, Time: {elapsed_time:.2f}s"
                        )
                        return None
        except httpx.TimeoutException:
            elapsed_time = asyncio.get_event_loop().time() - start_time
            logger.warning(
                f"✗ JSON GET {url}{proxy_info} - Timeout after {elapsed_time:.2f}s"
            )
            return None
        except Exception as e:
            elapsed_time = asyncio.get_event_loop().time() - start_time
            logger.error(
                f"✗ JSON GET {url}{proxy_info} - Error: {e}, Time: {elapsed_time:.2f}s"
            )
            return None


class GitHubClient:
    """Client for GitHub search operations."""

    def __init__(self):
        self.base_url = "https://github.com/search"
        self.headers = DEFAULT_HEADERS.copy()

    def search_files(self, query: str, page: int = 1) -> Optional[List[str]]:
        """
        Search for files on GitHub.

        Args:
            query: Search query
            page: Page number

        Returns:
            List of file URLs or None if search failed
        """

        start_time = time.time()
        logger.info(f"Searching GitHub for: {query} (page {page})")

        params = {
            "p": page,
            "q": query,
            "type": "code",
        }

        try:
            response = requests.get(
                self.base_url,
                params=params,
                headers=self.headers,
                timeout=10,
            )
            elapsed_time = time.time() - start_time

            if not response.ok:
                logger.warning(
                    f"✗ GitHub search '{query}' - Status: {response.status_code}, Time: {elapsed_time:.2f}s"
                )
                return None

            soup = BeautifulSoup(response.text, "lxml")
            all_a = soup.find_all("a", {"data-testid": "link-to-search-result"})
            results = [f"https://github.com{a.get('href')}" for a in all_a]

            logger.info(
                f"✓ GitHub search '{query}' - Found {len(results)} results, Status: {response.status_code}, Time: {elapsed_time:.2f}s"
            )
            return results

        except Exception as e:
            elapsed_time = time.time() - start_time
            logger.error(
                f"✗ GitHub search '{query}' - Error: {e}, Time: {elapsed_time:.2f}s"
            )
            return None


# Global instances
http_client = HTTPClient()
github_client = GitHubClient()
