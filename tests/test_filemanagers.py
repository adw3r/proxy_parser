import pathlib
import tempfile
from pathlib import Path

import pytest

from proxy_parser.file_operations import FileManagerJson


class TestFileManagerJson:
    """Test cases for FileManagerJson class."""

    def test_append_to_file(self):
        """Test append_to_file method."""
        with tempfile.TemporaryDirectory() as dir:
            print(dir)
            proxies_path = pathlib.Path(dir, 'proxies.json')
            file_manager = FileManagerJson(pathlib.Path(dir), proxies_path)
            file_manager.append_to_file(proxies_path, {'test': 'test'})

            res = file_manager.get_sources_dict([proxies_path])
            print(res)