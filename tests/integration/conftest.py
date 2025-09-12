"""Configuration for integration tests."""

import pytest


def pytest_configure(config):
    """Configure pytest for integration tests."""
    config.addinivalue_line('markers', 'integration: mark test as integration test')


def pytest_collection_modifyitems(items):
    """Modify test collection to handle integration test markers."""
    for item in items:
        # Add slow marker to all integration tests
        if 'integration' in item.keywords:
            item.add_marker(pytest.mark.slow)
