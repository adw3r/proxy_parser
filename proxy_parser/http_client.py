"""
HTTP client utilities for proxy parsing.
"""

import asyncio
import logging
from typing import Optional, Dict, Any, List
import httpx
import requests
from bs4 import BeautifulSoup

from proxy_parser.config import SEMAPHORE, DEFAULT_HEADERS

logger = logging.getLogger(__name__)


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
        logger.info(f"Making GET request to: {url}")
        start_time = asyncio.get_event_loop().time()

        try:
            async with SEMAPHORE:
                timeout_config = httpx.Timeout(timeout)
                async with httpx.AsyncClient(
                    headers=self.headers, timeout=timeout_config
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
        self, url: str, proxy: Optional[str] = None, timeout: int = 10
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
        logger.info(f"Making JSON GET request to: {url}{proxy_info}")
        start_time = asyncio.get_event_loop().time()

        try:
            async with SEMAPHORE:
                timeout_config = httpx.Timeout(timeout)

                # httpx uses proxy parameter directly
                proxy_url = None
                if proxy:
                    # Handle different proxy schemes
                    if proxy.startswith(('http://', 'https://')):
                        proxy_url = proxy
                    elif proxy.startswith('socks5://'):
                        # SOCKS5 proxies are now supported with httpx[socks]
                        proxy_url = proxy
                    elif proxy.startswith('socks4://'):
                        # SOCKS4 proxies are now supported with httpx[socks]
                        proxy_url = proxy
                    else:
                        # Assume HTTP proxy
                        proxy_url = f"http://{proxy}"

                async with httpx.AsyncClient(
                    headers=self.headers, 
                    timeout=timeout_config, 
                    proxy=proxy_url
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
        # Note: In production, these should be configurable and not hardcoded
        self.cookies = {
            "_octo": "GH1.1.2045407306.1670336220",
            "_device_id": "4080764a6f93b98d37a7aba816e05ad3",
            "user_session": "GJ2FquNK2R7LQszFIYzptfpN0wfc8zUgOEk89qHJoPXfzcKh",
            "__Host-user_session_same_site": "GJ2FquNK2R7LQszFIYzptfpN0wfc8zUgOEk89qHJoPXfzcKh",
            "logged_in": "yes",
            "dotcom_user": "adw3r",
            "color_mode": "%7B%22color_mode%22%3A%22dark%22%2C%22light_theme%22%3A%7B%22name%22%3A%22light%22%2C%22color_mode%22%3A%22light%22%7D%2C%22dark_theme%22%3A%7B%22name%22%3A%22dark_dimmed%22%2C%22color_mode%22%3A%22dark%22%7D%7D",
            "preferred_color_mode": "dark",
            "tz": "Europe%2FKiev",
            "has_recent_activity": "1",
            "_gh_sess": "q7aH3Q2vx6NV1WTTA0MFUcTzyhObT0evWl5c6LDusWpknBgE5%2B7fUN%2Fot6SUptY9n%2BoPiaXP694p1FIa2FGtOH1Mspzxzjm2bO0xvJDFd3e3jDab2I%2B42HrIBlZ3ZaINaok%2B9pIJuKxfi0U4PEjBuGB4HR764mOpc7glON1NrJ%2FFbXk%2Bn%2FFJWYvRheKTeeotpS7qIGb2sd91zheolHgHgiIJU9R%2FUJlSm20p0dM7TvGx9Vh0NlWRPBMLbfzc6PCV7KnibmO45YF7VAjyzD0OjuVzpMwYcGLvTdMRYY4Xe1SkIOlpJOsHD%2BkyZMFCE3Kc9VmKn%2B%2BXDXRvYAZpmg%3D%3D--Mv%2Bp%2FNXaXIsdeTAY--ZwQfQks6oKqHZvK%2BrkwHsQ%3D%3D",
        }

    def search_files(self, query: str, page: int = 1) -> Optional[List[str]]:
        """
        Search for files on GitHub.

        Args:
            query: Search query
            page: Page number

        Returns:
            List of file URLs or None if search failed
        """
        import time

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
                cookies=self.cookies,
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
