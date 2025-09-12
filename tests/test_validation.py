"""Tests for validation helpers."""

import pytest

from mcp_registry_client.validation import (
    validate_non_empty_string,
    validate_search_term,
    validate_server_name,
)


class TestValidationHelpers:
    """Tests for validation helper functions."""

    def test_validate_non_empty_string_success(self) -> None:
        """Test successful validation of non-empty string."""
        # Should not raise any exception
        validate_non_empty_string('valid-string', 'test field')
        validate_non_empty_string('   valid-string   ', 'test field')  # with whitespace

    def test_validate_non_empty_string_empty(self) -> None:
        """Test validation failure with empty string."""
        with pytest.raises(ValueError, match='test field cannot be empty'):
            validate_non_empty_string('', 'test field')

    def test_validate_non_empty_string_whitespace_only(self) -> None:
        """Test validation failure with whitespace-only string."""
        with pytest.raises(ValueError, match='test field cannot be empty'):
            validate_non_empty_string('   ', 'test field')

    def test_validate_search_term_success(self) -> None:
        """Test successful search term validation."""
        # Should not raise any exception
        validate_search_term('test')
        validate_search_term('valid-search-term')
        validate_search_term('   valid-term   ')  # with whitespace

    def test_validate_search_term_empty(self) -> None:
        """Test search term validation failure with empty string."""
        with pytest.raises(ValueError, match='Search term cannot be empty'):
            validate_search_term('')

    def test_validate_search_term_whitespace_only(self) -> None:
        """Test search term validation failure with whitespace-only string."""
        with pytest.raises(ValueError, match='Search term cannot be empty'):
            validate_search_term('   ')

    def test_validate_server_name_success(self) -> None:
        """Test successful server name validation."""
        # Should not raise any exception
        validate_server_name('test-server')
        validate_server_name('valid-server-name')
        validate_server_name('   valid-server   ')  # with whitespace

    def test_validate_server_name_empty(self) -> None:
        """Test server name validation failure with empty string."""
        with pytest.raises(ValueError, match='Server name cannot be empty'):
            validate_server_name('')

    def test_validate_server_name_whitespace_only(self) -> None:
        """Test server name validation failure with whitespace-only string."""
        with pytest.raises(ValueError, match='Server name cannot be empty'):
            validate_server_name('   ')
