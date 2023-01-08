from proxy_parser.config import PATH_TO_SOURCES
from proxy_parser.parsers import get_files_from_folder, get_links_from_file


def get_all_links_with_protos() -> dict[str, tuple]:

    files = {}

    for file in get_files_from_folder(PATH_TO_SOURCES):
        file_name = file.name.removesuffix('.txt')
        print(file_name)
        files[file_name] = tuple(link for link in get_links_from_file(file))
    return files
