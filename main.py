import asyncio
import os
import pathlib
import re
from configparser import ConfigParser
from pathlib import Path
from random import shuffle
from shutil import rmtree
from time import perf_counter, sleep
from typing import Callable, Dict, List, Optional, Set, Tuple, Union

from aiohttp import ClientSession
from aiohttp_socks import ProxyConnector
from rich.console import Console
from rich.progress import (
    BarColumn,
    MofNCompleteColumn,
    Progress,
    TaskID,
    TaskProgressColumn,
    TextColumn,
)
from rich.table import Table


class Proxy:
    __slots__ = (
        "geolocation",
        "ip",
        "is_anonymous",
        "socket_address",
        "timeout",
    )

    def __init__(self, socket_address: str, ip: str) -> None:
        """
        Args:
            socket_address: ip:port
        """
        self.socket_address = socket_address
        self.ip = ip

    async def check(
            self, sem: asyncio.Semaphore, proto: str, timeout: float
    ) -> None:
        async with sem:
            proxy_url = f"{proto}://{self.socket_address}"
            start = perf_counter()
            async with ProxyConnector.from_url(proxy_url) as connector:
                async with ClientSession(connector=connector) as session:
                    async with session.get(
                            "http://ip-api.com/json/?fields=8217",
                            timeout=timeout,
                            raise_for_status=True,
                    ) as response:
                        data = await response.json()
        self.timeout = perf_counter() - start
        self.is_anonymous = self.ip != data["query"]
        self.geolocation = "|{}|{}|{}".format(
            data["country"], data["regionName"], data["city"]
        )

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Proxy):
            return NotImplemented
        return self.socket_address == other.socket_address

    def __hash__(self) -> int:
        return hash(self.socket_address)


class Folder:
    __slots__ = ("for_anonymous", "for_geolocation", "path")

    def __init__(self, path: Path, folder_name: str) -> None:
        self.path = path / folder_name
        self.for_anonymous = "anon" in folder_name
        self.for_geolocation = "geo" in folder_name

    def remove(self) -> None:
        try:
            rmtree(self.path)
        except FileNotFoundError:
            pass

    def create(self) -> None:
        self.path.mkdir(parents=True, exist_ok=True)


def timeout_sort_key(proxy: Proxy) -> float:
    return proxy.timeout


def natural_sort_key(proxy: Proxy) -> Tuple[int, ...]:
    return tuple(map(int, proxy.socket_address.replace(":", ".").split(".")))


class ProxyScraperChecker:
    """HTTP, SOCKS4, SOCKS5 proxies scraper and checker."""

    __slots__ = (
        "all_folders",
        "console",
        "enabled_folders",
        "path",
        "proxies_count",
        "proxies",
        "regex",
        "sem",
        "sort_by_speed",
        "sources",
        "timeout",
    )

    def __init__(
            self,
            *,
            timeout: float,
            max_connections: int,
            sort_by_speed: bool,
            save_path: str,
            proxies: bool,
            proxies_anonymous: bool,
            proxies_geolocation: bool,
            proxies_geolocation_anonymous: bool,
            http_sources: Optional[str],
            socks4_sources: Optional[str],
            socks5_sources: Optional[str],
            console: Optional[Console] = None,
    ) -> None:
        """HTTP, SOCKS4, SOCKS5 proxies scraper and checker.

        Args:
            timeout: How many seconds to wait for the connection. The
                higher the number, the longer the check will take and
                the more proxies you get.
            max_connections: Maximum concurrent connections. Don't set
                higher than 900, please.
            sort_by_speed: Set to False to sort proxies alphabetically.
            save_path: Path to the folder where the proxy folders will
                be saved. Leave empty to save the proxies to the current
                directory.
        """
        self.path = Path(save_path)
        folders_mapping = {
            "proxies": proxies,
            "proxies_anonymous": proxies_anonymous,
            "proxies_geolocation": proxies_geolocation,
            "proxies_geolocation_anonymous": proxies_geolocation_anonymous,
        }
        self.all_folders = tuple(
            Folder(self.path, folder_name) for folder_name in folders_mapping
        )
        self.enabled_folders = tuple(
            folder
            for folder in self.all_folders
            if folders_mapping[folder.path.name]
        )
        if not self.enabled_folders:
            raise ValueError("all folders are disabled in the config")

        self.regex = re.compile(
            r"(?:^|\D)?(("
            + r"(?:[1-9]|[1-9]\d|1\d{2}|2[0-4]\d|25[0-5])"  # 1-255
            + r"\."
            + r"(?:\d|[1-9]\d|1\d{2}|2[0-4]\d|25[0-5])"  # 0-255
            + r"\."
            + r"(?:\d|[1-9]\d|1\d{2}|2[0-4]\d|25[0-5])"  # 0-255
            + r"\."
            + r"(?:\d|[1-9]\d|1\d{2}|2[0-4]\d|25[0-5])"  # 0-255
            + r"):"
            + (
                    r"(?:\d|[1-9]\d{1,3}|[1-5]\d{4}|6[0-4]\d{3}"
                    + r"|65[0-4]\d{2}|655[0-2]\d|6553[0-5])"
            )  # 0-65535
            + r")(?:\D|$)"
        )

        self.sort_by_speed = sort_by_speed
        self.timeout = timeout
        self.sources = {
            proto: frozenset(filter(None, sources.splitlines()))
            for proto, sources in (
                ("http", http_sources),
                ("socks4", socks4_sources),
                ("socks5", socks5_sources),
            )
            if sources
        }
        self.proxies: Dict[str, Set[Proxy]] = {
            proto: set() for proto in self.sources
        }
        self.proxies_count = {proto: 0 for proto in self.sources}
        self.console = console or Console()
        self.sem = asyncio.Semaphore(max_connections)

    async def fetch_source(
            self,
            session: ClientSession,
            source: str,
            proto: str,
            progress: Progress,
            task: TaskID,
    ) -> None:
        """Get proxies from source.

        Args:
            source: Proxy list URL.
            proto: http/socks4/socks5.
        """
        source = source.strip()
        try:
            async with session.get(source, timeout=15) as response:
                status = response.status
                text = await response.text()
        except Exception as e:
            msg = f"{source} | Error"
            exc_str = str(e)
            if exc_str and exc_str != source:
                msg += f": {exc_str}"
            self.console.print(msg)
        else:
            proxies = tuple(self.regex.finditer(text))
            if proxies:
                for proxy in proxies:
                    proxy_obj = Proxy(proxy.group(1), proxy.group(2))
                    self.proxies[proto].add(proxy_obj)
            else:
                msg = f"{source} | No proxies found"
                if status != 200:
                    msg += f" | Status code {status}"
                self.console.print(msg)
        progress.update(task, advance=1)

    async def check_proxy(
            self, proxy: Proxy, proto: str, progress: Progress, task: TaskID
    ) -> None:
        """Check if proxy is alive."""
        try:
            await proxy.check(self.sem, proto, self.timeout)
        except Exception as e:
            # Too many open files
            if isinstance(e, OSError) and e.errno == 24:
                self.console.print(
                    "[red]Please, set MAX_CONNECTIONS to lower value."
                )

            self.proxies[proto].remove(proxy)
        progress.update(task, advance=1)

    async def fetch_all_sources(self, progress: Progress) -> None:
        tasks = {
            proto: progress.add_task(
                f"[yellow]Scraper [red]:: [green]{proto.upper()}",
                total=len(sources),
            )
            for proto, sources in self.sources.items()
        }
        headers = {
            "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; rv:107.0)"
                    + " Gecko/20100101 Firefox/107.0"
            )
        }
        async with ClientSession(headers=headers) as session:
            coroutines = (
                self.fetch_source(
                    session, source, proto, progress, tasks[proto]
                )
                for proto, sources in self.sources.items()
                for source in sources
            )
            await asyncio.gather(*coroutines)

        # Remember total count so we could print it in the table
        for proto, proxies in self.proxies.items():
            self.proxies_count[proto] = len(proxies)

    async def check_all_proxies(self, progress: Progress) -> None:
        tasks = {
            proto: progress.add_task(
                f"[yellow]Checker [red]:: [green]{proto.upper()}",
                total=len(proxies),
            )
            for proto, proxies in self.proxies.items()
        }
        coroutines = [
            self.check_proxy(proxy, proto, progress, tasks[proto])
            for proto, proxies in self.proxies.items()
            for proxy in proxies
        ]
        shuffle(coroutines)
        await asyncio.gather(*coroutines)

    def save_proxies(self) -> None:
        """Delete old proxies and save new ones."""
        sorted_proxies = self.sorted_proxies.items()
        for folder in self.all_folders:
            folder.remove()
        for folder in self.enabled_folders:
            folder.create()
            for proto, proxies in sorted_proxies:
                text = "\n".join(
                    proxy.socket_address + proxy.geolocation
                    if folder.for_geolocation
                    else proxy.socket_address
                    for proxy in proxies
                    if (proxy.is_anonymous if folder.for_anonymous else True)
                )
                file = folder.path / f"{proto}.txt"
                file.write_text(text, encoding="utf-8")

    async def main(self) -> None:
        with self._progress as progress:
            await self.fetch_all_sources(progress)
            await self.check_all_proxies(progress)

        table = Table()
        table.add_column("Protocol", style="cyan")
        table.add_column("Working", style="magenta")
        table.add_column("Total", style="green")
        for proto, proxies in self.proxies.items():
            working = len(proxies)
            total = self.proxies_count[proto]
            percentage = working / total * 100 if total else 0
            table.add_row(
                proto.upper(), f"{working} ({percentage:.1f}%)", str(total)
            )
        self.console.print(table)

        self.save_proxies()
        self.console.print(
            "[green]Proxy folders have been created in the "
            + f"{self.path.resolve()} folder."
            + "\nThank you for using proxy-scraper-checker :)"
        )

    @property
    def sorted_proxies(self) -> Dict[str, List[Proxy]]:
        key: Union[
            Callable[[Proxy], float], Callable[[Proxy], Tuple[int, ...]]
        ] = (timeout_sort_key if self.sort_by_speed else natural_sort_key)
        return {
            proto: sorted(proxies, key=key)
            for proto, proxies in self.proxies.items()
        }

    @property
    def _progress(self) -> Progress:
        return Progress(
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            MofNCompleteColumn(),
            console=self.console,
        )


def get_proxies(path: Path | str) -> list:
    with open(path) as file:
        return file.read().split('\n')


def save_proxies(path: Path | str, proxies: list):
    with open(path, 'w') as file:
        file.write('\n'.join(proxies))


async def main() -> None:
    cfg = ConfigParser(interpolation=None)
    cfg.read("config.ini", encoding="utf-8")
    general = cfg["General"]
    folders = cfg["Folders"]
    http = cfg["HTTP"]
    socks4 = cfg["SOCKS4"]
    socks5 = cfg["SOCKS5"]
    socks4_sources = socks4.get("Sources")
    http_sources = http.get("Sources")
    socks5_sources = socks5.get("Sources")
    checker = ProxyScraperChecker(timeout=general.getfloat("Timeout", 10),
                                  max_connections=general.getint("MaxConnections", 900),
                                  sort_by_speed=general.getboolean("SortBySpeed", True),
                                  save_path=general.get("SavePath", ""), proxies=folders.getboolean("proxies", True),
                                  proxies_anonymous=folders.getboolean("proxies_anonymous", True),
                                  proxies_geolocation=folders.getboolean("proxies_geolocation", True),
                                  proxies_geolocation_anonymous=folders.getboolean("proxies_geolocation_anonymous",
                                                                                   True),
                                  http_sources=http_sources if http.getboolean("Enabled", True) else None,
                                  socks4_sources=socks4_sources if socks4.getboolean("Enabled", True) else None,
                                  socks5_sources=socks5_sources if socks5.getboolean("Enabled", True) else None, )
    await checker.main()

    proxies_folder = r'C:\Users\Administrator\Desktop\proxy-scraper-checker\proxies'
    parsed_path = pathlib.Path(proxies_folder, 'parsed.txt')
    if parsed_path.exists():
        os.remove(parsed_path)
    proxies = []
    for file in os.listdir(proxies_folder):
        proxies += [f'{file[:-4]}://{proxy}' for proxy in get_proxies(Path(proxies_folder, file))]
    target_database_proxies_folder = r'C:\Users\Administrator\Desktop\targetDatabaseProject\proxies'
    parsed_path = pathlib.Path(target_database_proxies_folder, 'parsed.txt')
    save_proxies(parsed_path, proxies)


if __name__ == "__main__":
    while True:
        asyncio.run(main())
        print('sleeping')
        sleep(240)
