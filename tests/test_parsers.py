"""
Tests for the parsers module.
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from pathlib import Path

from proxy_parser.parsers import ProxyParser
from proxy_parser.file_operations import FileManager


class TestProxyParser:
    """Test cases for ProxyParser class."""

    @pytest.fixture
    def mock_file_manager(self):
        """Create a mock file manager."""
        mock = Mock(spec=FileManager)
        mock.sources_path = Path("/tmp/sources")
        return mock

    @pytest.fixture
    def parser(self, mock_file_manager):
        """Create a ProxyParser instance."""
        return ProxyParser(mock_file_manager)

    async def test_fetch_source_empty_response(self, parser):
        """Test fetching from source with empty response."""
        with patch("proxy_parser.parsers.http_client") as mock_client:
            # Mock the async method properly
            mock_client.get_text = AsyncMock(return_value=None)

            result = await parser.fetch_source("http://example.com")

            assert result == set()
            mock_client.get_text.assert_called_once_with("http://example.com")

    async def test_fetch_source_with_proxies(self, parser):
        """Test fetching from source with proxy data."""
        sample_text = "Some text with proxy 192.168.1.1:8080 and 10.0.0.1:3128"

        with patch("proxy_parser.parsers.http_client") as mock_client:
            # Mock the async method properly
            mock_client.get_text = AsyncMock(return_value=sample_text)

            result = await parser.fetch_source("http://example.com")

            expected = {"192.168.1.1:8080", "10.0.0.1:3128"}
            assert result == expected

    async def test_get_proxies_success(self, parser):
        """Test getting proxies from multiple sources."""
        urls = ["http://source1.com", "http://source2.com"]

        with patch.object(parser, "fetch_source") as mock_fetch:
            mock_fetch.side_effect = [
                {"192.168.1.1:8080", "10.0.0.1:3128"},
                {"172.16.0.1:9090"},
            ]

            result = await parser.get_proxies(urls)

            assert len(result) == 2
            assert result[0] == {"192.168.1.1:8080", "10.0.0.1:3128"}
            assert result[1] == {"172.16.0.1:9090"}

    async def test_get_proxies_with_exceptions(self, parser):
        """Test getting proxies with some sources failing."""
        urls = ["http://source1.com", "http://source2.com"]

        with patch.object(parser, "fetch_source") as mock_fetch:
            mock_fetch.side_effect = [{"192.168.1.1:8080"}, Exception("Network error")]

            result = await parser.get_proxies(urls)

            assert len(result) == 1
            assert result[0] == {"192.168.1.1:8080"}

    def test_update_sources(self, parser):
        """Test updating sources from GitHub."""
        with (
            patch("proxy_parser.parsers.github_client") as mock_github,
            patch.object(parser.file_manager, "append_iterable_to_file") as mock_append,
            patch.object(parser.file_manager, "clean_duplicates") as mock_clean,
        ):
            mock_github.search_files.return_value = [
                "http://github.com/file1",
                "http://github.com/file2",
            ]

            parser.update_sources()

            # Verify that search was called for each query
            assert mock_github.search_files.call_count > 0
            assert mock_append.call_count > 0
            assert mock_clean.call_count > 0
