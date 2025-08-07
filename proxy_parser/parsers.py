"""
Proxy parsing functionality.
"""

import asyncio
from typing import List, Set
from pathlib import Path

from proxy_parser.config import REGEX_PATTERN, SEARCH_QUERIES, DEPTH
from proxy_parser.http_client import http_client, github_client
from proxy_parser.file_operations import FileManager
from loguru import logger


class ProxyParser:
    """Handles proxy parsing operations."""

    def __init__(self, file_manager: FileManager):
        self.file_manager = file_manager

    async def fetch_source(self, source_link: str) -> Set[str]:
        """
        Fetch and parse proxies from a source URL.

        Args:
            source_link: URL to fetch proxies from

        Returns:
            Set of found proxy strings
        """
        logger.info(f"Fetching proxies from source: {source_link}")
        start_time = asyncio.get_event_loop().time()

        text = await http_client.get_text(source_link)
        elapsed_time = asyncio.get_event_loop().time() - start_time

        if not text:
            logger.warning(
                f"✗ No content received from {source_link} in {elapsed_time:.2f}s"
            )
            return set()

        proxies = set()
        for match in REGEX_PATTERN.finditer(text):
            proxy = match.group(1)
            if proxy:
                proxies.add(proxy)

        logger.info(
            f"✓ Parsed {len(proxies)} proxies from {source_link} in {elapsed_time:.2f}s"
        )
        return proxies

    async def get_proxies(self, sources_urls: List[str]) -> List[Set[str]]:
        """
        Fetch proxies from multiple sources concurrently.

        Args:
            sources_urls: List of URLs to fetch from

        Returns:
            List of proxy sets from each source
        """
        logger.info(f"Fetching proxies from {len(sources_urls)} sources concurrently")
        start_time = asyncio.get_event_loop().time()

        tasks = [self.fetch_source(url) for url in sources_urls]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Filter out exceptions and return valid results
        valid_results = []
        failed_count = 0
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"✗ Failed to fetch from {sources_urls[i]}: {result}")
                failed_count += 1
            else:
                valid_results.append(result)

        elapsed_time = asyncio.get_event_loop().time() - start_time
        total_proxies = sum(len(proxy_set) for proxy_set in valid_results)

        logger.info(
            f"✓ Completed fetching from {len(sources_urls)} sources - {len(valid_results)} successful, {failed_count} failed, {total_proxies} total proxies in {elapsed_time:.2f}s"
        )
        return valid_results

    def update_sources(self) -> None:
        """
        Update source files by searching GitHub for proxy files.
        """
        logger.info("Starting GitHub source update")
        start_time = asyncio.get_event_loop().time()

        total_links = 0
        successful_searches = 0

        for query, file_name in SEARCH_QUERIES.items():
            logger.info(f"Searching for {query}")
            path_to_source = self.file_manager.sources_path / file_name

            all_links = set()
            for page in range(DEPTH):
                links_from_github = github_client.search_files(query, page + 1)
                if links_from_github:
                    all_links.update(links_from_github)
                    logger.debug(
                        f"Found {len(links_from_github)} links on page {page + 1} for {query}"
                    )
                else:
                    logger.debug(f"No links found on page {page + 1} for {query}")

            if all_links:
                logger.info(f"✓ Found {len(all_links)} total links for {query}")
                self.file_manager.append_iterable_to_file(path_to_source, all_links)
                self.file_manager.clean_duplicates(path_to_source)
                total_links += len(all_links)
                successful_searches += 1
            else:
                logger.warning(f"✗ No links found for query: {query}")

        elapsed_time = asyncio.get_event_loop().time() - start_time
        logger.info(
            f"✓ GitHub source update completed - {successful_searches}/{len(SEARCH_QUERIES)} searches successful, {total_links} total links in {elapsed_time:.2f}s"
        )

    async def parse_unchecked_proxies(self) -> Set[str]:
        """
        Parse proxies from all source files.

        Returns:
            Set of all found proxy strings
        """
        logger.info("Starting proxy parsing from sources")
        start_time = asyncio.get_event_loop().time()

        sources_list = self.file_manager.get_files_from_folder(
            self.file_manager.sources_path
        )
        sources_dict = self.file_manager.get_sources_dict(sources_list)

        logger.info(f"Found {len(sources_dict)} source files to parse")

        all_proxies = set()

        for protocol, urls in sources_dict.items():
            if not urls:
                logger.warning(f"No URLs found for protocol: {protocol}")
                continue

            logger.info(f"Parsing {protocol} proxies from {len(urls)} sources")
            proxy_sets = await self.get_proxies(urls)

            # Combine all proxies from this protocol
            protocol_proxies = set()
            for proxy_set in proxy_sets:
                protocol_proxies.update(proxy_set)

            # Add protocol prefix
            formatted_proxies = {f"{protocol}://{proxy}" for proxy in protocol_proxies}
            all_proxies.update(formatted_proxies)

            logger.info(f"✓ Found {len(formatted_proxies)} {protocol} proxies")

        elapsed_time = asyncio.get_event_loop().time() - start_time
        logger.info(
            f"✓ Proxy parsing completed - {len(all_proxies)} total proxies found in {elapsed_time:.2f}s"
        )
        return all_proxies

    async def save_unchecked_proxies(self, proxies: Set[str], file_path: str) -> None:
        """
        Save unchecked proxies to file.

        Args:
            proxies: Set of proxy strings
            file_path: Path to save proxies to
        """
        if not proxies:
            logger.warning("No proxies to save")
            return

        logger.info(f"Saving {len(proxies)} proxies to {file_path}")
        self.file_manager.write_lines(Path(file_path), list(proxies))
        logger.info(f"✓ Saved {len(proxies)} proxies to {file_path}")

    async def get_unchecked_proxies(self, file_path: str) -> set[str]:
        """
        Load unchecked proxies from file.

        Args:
            file_path: Path to load proxies from

        Returns:
            Set of proxy strings
        """
        logger.info(f"Loading unchecked proxies from {file_path}")
        lines = self.file_manager.read_lines(Path(file_path))
        proxies = {line.strip() for line in lines if line.strip()}
        logger.info(f"✓ Loaded {len(proxies)} unchecked proxies from {file_path}")
        return proxies
