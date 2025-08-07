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
DEFAULT_HEADERS: Dict[str, str] = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    'Cookie': "__Host-user_session_same_site=n0lZU5cz_MrxkmqJ6blVniZG6eLGZzO2k_Xj--u9lqaf6krt;dotcom_user=adw3r;cpu_bucket=xlg;saved_user_sessions=77853696%3An0lZU5cz_MrxkmqJ6blVniZG6eLGZzO2k_Xj--u9lqaf6krt;_device_id=12ef26caf437743336766591bf83575b;_gh_sess=Z2IDE2aBTu7R6mlOvqWx2yRZOikSHasKLbVVV2UCPY7hh2rLJ32v0n4rZ7I%2BNRn1kXxLextrEYyugMnficgwBD8EXSyry%2FVS%2BCCzTdzw6jDQmsgfvYbW1kPH4ne1t0fhHvoLbuDUJNCvBH8gEYAlbFtSU4brVo3DvvBr7%2FrE6cgndAXv59CDrUTItSI%2FE7OyuKtJ0hfFvtFl0QWA%2BakTYr08iks5DsMVlG23yFJT1b8%2Bd0JTMU8KdftXOh%2Bt2cZYsHdd4iesMXl0znQoTOqOaw0bO%2B3sEQYw%2BbwdP49DYtuGt3xRWHhlIJHDe958TUImy7zCo%2BJxb3ThUHFK%2FMdxOAowdaSlaZ1zoIzhqBaV7GVLFSRkcDQ3GyaI5XClZSm61rKvBQoGyZtYhQog%2BTsdZaLtUxHvSFdPEx5dBI4eWJia9GKyOeSeRxHwfHMUt0Xln2IvmZQ7ur%2BmRb%2FnYKD1H7NeG7Hyrd%2FDuzzcJpWha2yr6v5h5CpovsW3S6iyG5acZZwWe8UYeFsaimTjugMcotroG0OBb6LECu8uftljyCmoDPFRhlkUIx0i2AhyPVI8DQtDNy215mALvsUgYnbv5dsYSeIz8qHo0e8itqIgiX86iMio9nT381YO%2FdTPLHwF4f5K5b5%2BVYEskiMjpnmPKUKCRYZumZlzJSbOG5kug4iH%2FWNXCrvQ9sKCcPOhiGIiikzzrpLfWEyUfKQY%2F47X5Yo7LpcZr%2B1nefDuHeJrsIHXEDt%2FFhbbsjEuLpc6ZgQI4%2FbKIayefjcJ1uY4qzs%2BTUbed1dWxkmBfJ1sOB2gJp%2BAv%2FS%2FmPGXfBwrVnT%2Bwoic29t9CFQnvFBnv%2FiPUAciLAfLNsRo2he%2FXA1I1NPIr7LGKy5SxJe8Hi0jZQ2jDA2y3h6bFuIk6Wacm6tPSFPj1e%2FIesh6osy58eXGOZXucpUDcMWH5t4bgfY%2FR1AC%2F%2BzZfkzXuHiNOBRuv8s8Qfqq7z3pNEEAYmrdLVl6vpkQixdxTKSncdtTTw%3D%3D--5QS1c3BGp48uJL6A--a9QTkCX1AH5SFcQ%2F5154XA%3D%3D;_octo=GH1.1.902835436.1750611110;color_mode=%7B%22color_mode%22%3A%22dark%22%2C%22light_theme%22%3A%7B%22name%22%3A%22light%22%2C%22color_mode%22%3A%22light%22%7D%2C%22dark_theme%22%3A%7B%22name%22%3A%22dark_dimmed%22%2C%22color_mode%22%3A%22dark%22%7D%7D;logged_in=yes;preferred_color_mode=dark;tz=Europe%2FKiev;tz=Europe%2FKiev;user_session=n0lZU5cz_MrxkmqJ6blVniZG6eLGZzO2k_Xj--u9lqaf6krt"
}

# Proxy checking settings
PROXY_CHECK_URL = "http://ip-api.com/json/?fields=8217"
PROXY_CHECK_TIMEOUT = 10
