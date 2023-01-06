import re
from configparser import ConfigParser
from pathlib import Path

ROOT_FOLDER = Path(__file__).parent.parent
REGEX_PATTERN = re.compile(
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
SOURCES_PATH = Path(ROOT_FOLDER, 'sources')

cfg = ConfigParser(interpolation=None)
cfg.read("config.ini", encoding="utf-8")
general = cfg["General"]
folders = cfg["Folders"]

TIMEOUT = general.getfloat("Timeout", 10)
MAX_CONNECTIONS = general.getint("MaxConnections", 900)
SORT_BY_SPEED = general.getboolean("SortBySpeed", True)
SAVE_PATH = general.get("SavePath", "")
FOLDER_GETBOOLEAN = folders.getboolean("proxies", True)
PROXIES_ANONYMOUS = folders.getboolean("proxies_anonymous", True)
PROXIES_GEOLOCATION = folders.getboolean("proxies_geolocation", True)
PROXIES_GEOLOCATION_ANONYMOUS = folders.getboolean("proxies_geolocation_anonymous", True)
