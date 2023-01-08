from pathlib import Path

from proxy_parser.checkers import check_proxy_list
from proxy_parser.config import SAVE_PATH
from proxy_parser.parsers import get_uncheked_proxies, append_proxy_to_file


def main():
    all_unchecked_proxies = get_uncheked_proxies()

    for proxy in check_proxy_list(all_unchecked_proxies):
        print(proxy)
        append_proxy_to_file(Path(SAVE_PATH, 'parsed.txt'), proxy)


if __name__ == '__main__':
    main()
