import asyncio
import re
from configparser import ConfigParser
from pathlib import Path
from typing import Dict


ROOT_FOLDER = Path(__file__).parent.parent
config: ConfigParser = ConfigParser(interpolation=None)
config.read(Path(ROOT_FOLDER, "config.ini"), encoding="utf-8")

GENERAL = config["General"]

# Paths
PATH_TO_SOURCES: Path = Path(ROOT_FOLDER, "sources")
if not PATH_TO_SOURCES.exists():
    PATH_TO_SOURCES.mkdir()

PROXIES_PATH: Path = Path(ROOT_FOLDER / "proxies")
PROXIES_PATH.mkdir(parents=True, exist_ok=True)

NOT_CHECKED_PROXIES_FILE = Path(PROXIES_PATH, "unchecked_proxies.txt")
CHECKED_PROXIES_FILE = Path(PROXIES_PATH, "parsed.txt")

# Network settings
MAX_CONNECTIONS: int = GENERAL.getint("MaxConnections", "1000")
TIMEOUT: int = GENERAL.getint("Timeout", "10")
INF_MAIN_TIMEOUT_SECONDS: int = GENERAL.getint("MainTimeout", "240")
DEPTH = GENERAL.getint("ParsingDepth", "7")

# Semaphore for connection limiting
SEMAPHORE = asyncio.Semaphore(MAX_CONNECTIONS)

# Regex pattern for IP:port matching
REGEX_PATTERN: re.Pattern = re.compile(
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

# Search queries for different proxy types
SEARCH_QUERIES: Dict[str, str] = {
    "path:http_proxies.txt": "http.txt",
    "path:proxies.txt": "http.txt",
    "path:https_proxies.txt": "https.txt",
    "path:socks5_proxies.txt": "socks5.txt",
    "path:socks4_proxies.txt": "socks4.txt",
}

# HTTP client settings
SESSION_COOKIES: str = GENERAL.get("GitHubCookies", "")
DEFAULT_HEADERS: Dict[str, str] = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    'Cookie': SESSION_COOKIES
}

# Proxy checking settings
PROXY_CHECK_URL = "http://ip-api.com/json/?fields=8217"
PROXY_CHECK_TIMEOUT = GENERAL.getint("ProxyCheckTimeout", "2")
