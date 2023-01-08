import os
from pathlib import Path
from time import sleep

from proxy_parser.checkers import check_proxy_list
from proxy_parser.config import SAVE_PATH
from proxy_parser.parsers import get_uncheked_proxies, append_proxy_to_file, clean_file


def main():
    all_unchecked_proxies = get_uncheked_proxies()
    path_to_file = Path(SAVE_PATH, 'parsed.txt')
    c = 0

    for proxy in check_proxy_list(all_unchecked_proxies):
        if c == 0 and path_to_file.exists():
            os.remove(path_to_file)
            c += 1
        print(proxy)
        append_proxy_to_file(path_to_file, proxy)

    clean_file(path_to_file)


def infinite_main():
    while True:
        main()
        sleep(120)


if __name__ == '__main__':
    main()
