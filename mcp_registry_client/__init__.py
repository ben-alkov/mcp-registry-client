"""MCP Registry Client - A Python client for the MCP server registry."""

from .client import RegistryClient, RegistryClientError, RegistryAPIError
from .models import Server, SearchResponse, Repository, Package

__version__ = '0.1.0'

__all__ = [
    'RegistryClient',
    'RegistryClientError',
    'RegistryAPIError',
    'Server',
    'SearchResponse',
    'Repository',
    'Package',
]
