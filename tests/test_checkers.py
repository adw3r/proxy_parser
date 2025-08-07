"""
Tests for the checkers module.
"""

import pytest
from unittest.mock import patch, AsyncMock

from proxy_parser.checkers import ProxyChecker


class TestProxyChecker:
    """Test cases for ProxyChecker class."""

    @pytest.fixture
    def checker(self):
        """Create a ProxyChecker instance."""
        return ProxyChecker()

    async def test_check_proxy_success(self, checker):
        """Test successful proxy check."""
        mock_response = {"query": "192.168.1.1", "status": "success"}

        with patch("proxy_parser.checkers.http_client") as mock_client:
            # Mock the async method properly
            mock_client.get_json = AsyncMock(return_value=mock_response)

            result = await checker.check_proxy("http://192.168.1.1:8080")

            assert result is not None
            proxy, response = result
            assert proxy == "http://192.168.1.1:8080"
            assert response is mock_response

    async def test_check_proxy_no_ip(self, checker):
        """Test proxy check with no IP in response."""
        mock_response = {"query": "", "status": "success"}

        with patch("proxy_parser.checkers.http_client") as mock_client:
            # Mock the async method properly
            mock_client.get_json = AsyncMock(return_value=mock_response)

            result = await checker.check_proxy("http://192.168.1.1:8080")

            assert result is None

    async def test_check_proxy_invalid_response(self, checker):
        """Test proxy check with invalid response."""
        with patch("proxy_parser.checkers.http_client") as mock_client:
            # Mock the async method properly
            mock_client.get_json = AsyncMock(return_value=None)

            result = await checker.check_proxy("http://192.168.1.1:8080")

            assert result is None

    async def test_check_proxy_exception(self, checker):
        """Test proxy check with exception."""
        with patch("proxy_parser.checkers.http_client") as mock_client:
            # Mock the async method properly
            mock_client.get_json = AsyncMock(side_effect=Exception("Network error"))

            result = await checker.check_proxy("http://192.168.1.1:8080")

            assert result is None

    async def test_check_proxies_generator(self, checker):
        """Test checking multiple proxies."""
        proxies = {"http://192.168.1.1:8080", "http://10.0.0.1:3128"}
        mock_responses = [
            ("http://192.168.1.1:8080", {"query": "192.168.1.1"}),
            ("http://10.0.0.1:3128", {"query": "10.0.0.1"}),
        ]

        with patch.object(checker, "check_proxy") as mock_check:
            mock_check.side_effect = mock_responses

            results = []
            async for result in checker.check_proxies_generator(proxies):
                results.append(result)

            assert len(results) == 2
            assert results[0] == mock_responses[0]
            assert results[1] == mock_responses[1]

    async def test_check_proxies_generator_with_failures(self, checker):
        """Test checking proxies with some failures."""
        proxies = {"http://192.168.1.1:8080", "http://10.0.0.1:3128"}

        with patch.object(checker, "check_proxy") as mock_check:
            mock_check.side_effect = [
                ("http://192.168.1.1:8080", {"query": "192.168.1.1"}),
                None,  # Second proxy fails
            ]

            results = []
            async for result in checker.check_proxies_generator(proxies):
                results.append(result)

            assert len(results) == 1
            assert results[0] == ("http://192.168.1.1:8080", {"query": "192.168.1.1"})
