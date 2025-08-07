"""
Main entry point for the proxy parser.
"""

import asyncio
import sys

from proxy_parser.config import PATH_TO_SOURCES, PROXIES_PATH, INF_MAIN_TIMEOUT_SECONDS
from proxy_parser.file_operations import FileManager
from proxy_parser.orchestrator import ProxyOrchestrator
from loguru import logger


async def main() -> None:
    """Run a single proxy parsing cycle."""
    try:
        file_manager = FileManager(PATH_TO_SOURCES, PROXIES_PATH)
        orchestrator = ProxyOrchestrator(file_manager)
        await orchestrator.run_full_cycle()
    except Exception as e:
        logger.error(f"Error in main: {e}")
        sys.exit(1)


async def infinite_main() -> None:
    """Run infinite proxy parsing cycles."""
    try:
        file_manager = FileManager(PATH_TO_SOURCES, PROXIES_PATH)
        orchestrator = ProxyOrchestrator(file_manager)
        await orchestrator.run_infinite_cycle(INF_MAIN_TIMEOUT_SECONDS)
    except KeyboardInterrupt:
        logger.info("Received interrupt signal, shutting down gracefully")
    except Exception as e:
        logger.error(f"Error in infinite main: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(infinite_main())
