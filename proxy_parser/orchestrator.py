"""
Main orchestrator for proxy parsing operations.
"""
import asyncio
import logging
from typing import Set

from proxy_parser.config import NOT_CHECKED_PROXIES_FILE, CHECKED_PROXIES_FILE
from proxy_parser.parsers import ProxyParser
from proxy_parser.checkers import ProxyChecker
from proxy_parser.file_operations import FileManager

logger = logging.getLogger(__name__)


class ProxyOrchestrator:
    """Orchestrates the entire proxy parsing workflow."""
    
    def __init__(self, file_manager: FileManager):
        self.file_manager = file_manager
        self.parser = ProxyParser(file_manager)
        self.checker = ProxyChecker()
    
    async def run_full_cycle(self) -> None:
        """
        Run a complete proxy parsing cycle:
        1. Update sources from GitHub
        2. Parse proxies from sources
        3. Check proxies for validity
        """
        logger.info("🚀 Starting full proxy parsing cycle")
        cycle_start_time = asyncio.get_event_loop().time()
        
        try:
            # Step 1: Update sources
            logger.info("📡 Step 1: Updating sources from GitHub")
            step1_start = asyncio.get_event_loop().time()
            self.parser.update_sources()
            step1_time = asyncio.get_event_loop().time() - step1_start
            logger.info(f"✅ Step 1 completed in {step1_time:.2f}s")
            
            # Step 2: Parse proxies
            logger.info("🔍 Step 2: Parsing proxies from sources")
            step2_start = asyncio.get_event_loop().time()
            unchecked_proxies = await self.parser.parse_unchecked_proxies()
            step2_time = asyncio.get_event_loop().time() - step2_start
            
            if not unchecked_proxies:
                logger.warning("⚠️ No proxies found in this cycle")
                return
            
            logger.info(f"✅ Step 2 completed - {len(unchecked_proxies)} proxies found in {step2_time:.2f}s")
            
            # Save unchecked proxies
            logger.info("💾 Saving unchecked proxies")
            await self.parser.save_unchecked_proxies(
                unchecked_proxies, 
                str(NOT_CHECKED_PROXIES_FILE)
            )
            
            # Step 3: Check proxies
            logger.info("🔧 Step 3: Checking proxies for validity")
            step3_start = asyncio.get_event_loop().time()
            await self.check_proxies()
            step3_time = asyncio.get_event_loop().time() - step3_start
            logger.info(f"✅ Step 3 completed in {step3_time:.2f}s")
            
            cycle_time = asyncio.get_event_loop().time() - cycle_start_time
            logger.info(f"🎉 Full cycle completed successfully in {cycle_time:.2f}s")
            
        except Exception as e:
            cycle_time = asyncio.get_event_loop().time() - cycle_start_time
            logger.error(f"❌ Error during full cycle after {cycle_time:.2f}s: {e}")
            raise
    
    async def check_proxies(self) -> None:
        """
        Check all unchecked proxies and save working ones.
        """
        # Load unchecked proxies
        logger.info("📂 Loading unchecked proxies for validation")
        unchecked_proxies = await self.parser.get_unchecked_proxies(
            str(NOT_CHECKED_PROXIES_FILE)
        )
        
        if not unchecked_proxies:
            logger.warning("⚠️ No unchecked proxies to check")
            return
        
        logger.info(f"🔍 Starting validation of {len(unchecked_proxies)} proxies")
        
        # Clear checked proxies file
        self.file_manager.clear_file(CHECKED_PROXIES_FILE)
        
        # Check proxies and save working ones
        working_count = 0
        start_time = asyncio.get_event_loop().time()
        
        async for proxy, response_data in self.checker.check_proxies_generator(unchecked_proxies):
            if proxy and response_data:
                self.file_manager.append_to_file(CHECKED_PROXIES_FILE, proxy)
                working_count += 1
                logger.debug(f"✅ Working proxy: {proxy}")
        
        elapsed_time = asyncio.get_event_loop().time() - start_time
        success_rate = (working_count / len(unchecked_proxies)) * 100 if unchecked_proxies else 0
        
        logger.info(f"📊 Proxy validation summary: {working_count}/{len(unchecked_proxies)} working ({success_rate:.1f}% success rate) in {elapsed_time:.2f}s")
    
    async def run_infinite_cycle(self, timeout_seconds: int) -> None:
        """
        Run infinite proxy parsing cycles with specified timeout.
        
        Args:
            timeout_seconds: Seconds to wait between cycles
        """
        logger.info(f"🔄 Starting infinite proxy parsing with {timeout_seconds}s timeout between cycles")
        cycle_count = 0
        
        while True:
            cycle_count += 1
            logger.info(f"🔄 Starting cycle #{cycle_count}")
            
            try:
                await self.run_full_cycle()
                
                # Wait before next cycle
                logger.info(f"⏳ Waiting {timeout_seconds} seconds before next cycle")
                await asyncio.sleep(timeout_seconds)
                
            except KeyboardInterrupt:
                logger.info("🛑 Received interrupt signal, stopping infinite cycle")
                break
            except Exception as e:
                logger.error(f"❌ Error in infinite cycle #{cycle_count}: {e}")
                logger.info(f"⏳ Waiting {timeout_seconds} seconds before retry")
                await asyncio.sleep(timeout_seconds)
