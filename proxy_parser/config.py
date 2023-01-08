import re
from configparser import ConfigParser
from pathlib import Path

ROOT_FOLDER = Path(__file__).parent.parent
cfg: ConfigParser = ConfigParser(interpolation=None)
cfg.read(Path(ROOT_FOLDER, "config.ini"), encoding="utf-8")
general = cfg["General"]

PATH_TO_SOURCES: Path = Path(ROOT_FOLDER, 'sources')
SAVE_PATH: Path = Path(general.get("SavePath", ""))
MAX_CONNECTIONS: int = int(general.get("MaxConnections", '100'))
TIMEOUT: int = int(general.get('Timeout', '10'))

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
