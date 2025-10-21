"""
Command-line interface for the proxy parser.
"""

import asyncio
import argparse
import sys

from proxy_parser.config import PATH_TO_SOURCES, PROXIES_PATH, INF_MAIN_TIMEOUT_SECONDS
from proxy_parser.file_operations import FileManager, FileManagerJson
from proxy_parser.orchestrator import ProxyOrchestrator
from proxy_parser.parsers import ProxyParser
from loguru import logger

file_manager = FileManagerJson(PATH_TO_SOURCES, PROXIES_PATH)
orchestrator = ProxyOrchestrator(file_manager)
parser = ProxyParser(file_manager)


async def run_single_cycle() -> None:
    """Run a single proxy parsing cycle."""
    try:
        await orchestrator.run_full_cycle()
        logger.info("Single cycle completed successfully")
    except Exception as e:
        logger.error(f"Error during single cycle: {e}")
        sys.exit(1)


async def run_infinite_cycle(timeout: int = INF_MAIN_TIMEOUT_SECONDS) -> None:
    """Run infinite proxy parsing cycles."""
    try:
        await orchestrator.run_infinite_cycle(timeout)
    except KeyboardInterrupt:
        logger.info("Received interrupt signal, shutting down gracefully")
    except Exception as e:
        logger.error(f"Error during infinite cycle: {e}")
        sys.exit(1)


async def update_sources() -> None:
    """Update source files from GitHub."""
    try:
        parser.update_sources()
        logger.info("Sources updated successfully")
    except Exception as e:
        logger.error(f"Error updating sources: {e}")
        sys.exit(1)


async def parse_proxies() -> None:
    """Parse proxies from existing sources."""
    try:
        proxies = await parser.parse_unchecked_proxies()

        if proxies:
            await parser.save_unchecked_proxies(
                proxies, str(PROXIES_PATH / "unchecked_proxies.txt")
            )
            logger.info(f"Parsed {len(proxies)} proxies successfully")
        else:
            logger.warning("No proxies found")
    except Exception as e:
        logger.error(f"Error parsing proxies: {e}")
        sys.exit(1)


async def check_proxies() -> None:
    """Check existing unchecked proxies."""
    try:
        await orchestrator.check_proxies()
        logger.info("Proxy checking completed")
    except Exception as e:
        logger.error(f"Error checking proxies: {e}")
        sys.exit(1)


def main() -> None:
    """Main CLI entry point."""
    arg_parser = argparse.ArgumentParser(
        description="Proxy Parser - Scrape and validate free proxies from GitHub",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  proxy-parser                    # Run infinite mode (default)
  proxy-parser --single          # Run single cycle
  proxy-parser --update-sources  # Update source files only
  proxy-parser --parse           # Parse proxies only
  proxy-parser --check           # Check proxies only
  proxy-parser --timeout 300     # Set custom timeout (seconds)
        """,
    )

    arg_parser.add_argument(
        "--single", action="store_true", help="Run a single parsing cycle and exit"
    )

    arg_parser.add_argument(
        "--update-sources",
        action="store_true",
        help="Update source files from GitHub only",
    )

    arg_parser.add_argument(
        "--parse", action="store_true", help="Parse proxies from existing sources only"
    )

    arg_parser.add_argument(
        "--check", action="store_true", help="Check existing unchecked proxies only"
    )

    arg_parser.add_argument(
        "--timeout",
        type=int,
        default=INF_MAIN_TIMEOUT_SECONDS,
        help=f"Timeout between cycles in seconds (default: {INF_MAIN_TIMEOUT_SECONDS})",
    )

    arg_parser.add_argument(
        "--verbose", "-v", action="store_true", help="Enable verbose logging"
    )

    args = arg_parser.parse_args()

    # Determine which operation to run
    if args.update_sources:
        asyncio.run(update_sources())
    elif args.parse:
        asyncio.run(parse_proxies())
    elif args.check:
        asyncio.run(check_proxies())
    elif args.single:
        asyncio.run(run_single_cycle())
    else:
        # Default: infinite mode
        asyncio.run(run_infinite_cycle(args.timeout))


if __name__ == "__main__":
    main()
