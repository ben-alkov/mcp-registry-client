"""Tests for Pydantic models."""

from datetime import datetime

import pytest
from pydantic import ValidationError

from mcp_registry_client.models import (
    OfficialMeta,
    Repository,
    SearchResponse,
    Server,
    ServerMeta,
)


class TestRepository:
    """Tests for Repository model."""

    def test_minimal_repository(self) -> None:
        """Test repository with minimal required fields."""
        repo = Repository(url='https://github.com/example/repo', source='github')
        assert repo.url == 'https://github.com/example/repo'
        assert repo.source == 'github'
        assert repo.id_ is None
        assert repo.subfolder is None

    def test_full_repository(self) -> None:
        """Test repository with all fields."""
        repo = Repository(
            url='https://github.com/example/repo',
            source='github',
            id='12345',
            subfolder='packages/server',
        )
        assert repo.url == 'https://github.com/example/repo'
        assert repo.source == 'github'
        assert repo.id_ == '12345'
        assert repo.subfolder == 'packages/server'


class TestOfficialMeta:
    """Tests for OfficialMeta model."""

    def test_official_meta(self) -> None:
        """Test official metadata parsing."""
        now = datetime.now()
        meta = OfficialMeta(
            id_='test-id',
            published_at=now,
            updated_at=now,
            is_latest=True,
        )
        assert meta.id_ == 'test-id'
        assert meta.published_at == now
        assert meta.updated_at == now
        assert meta.is_latest is True


class TestServerMeta:
    """Tests for ServerMeta model."""

    def test_server_meta_alias(self) -> None:
        """Test server metadata with alias field."""
        now = datetime.now()
        data = {
            'io.modelcontextprotocol.registry/official': {
                'id': 'test-id',
                'published_at': now,
                'updated_at': now,
                'is_latest': True,
            },
        }
        meta = ServerMeta.model_validate(data)
        assert meta.official.id_ == 'test-id'
        assert meta.official.is_latest is True


class TestServer:
    """Tests for Server model."""

    def test_minimal_server(self) -> None:
        """Test server with minimal required fields."""
        now = datetime.now()
        data = {
            'name': 'test-server',
            'description': 'A test server',
            'status': 'active',
            'repository': {'url': 'https://github.com/test/repo', 'source': 'github'},
            'version': '1.0.0',
            '_meta': {
                'io.modelcontextprotocol.registry/official': {
                    'id': 'test-id',
                    'published_at': now,
                    'updated_at': now,
                    'is_latest': True,
                },
            },
        }
        server = Server.model_validate(data)
        assert server.name == 'test-server'
        assert server.description == 'A test server'
        assert server.status == 'active'
        assert server.version == '1.0.0'
        assert server.repository.url == 'https://github.com/test/repo'
        assert server.meta.official.id_ == 'test-id'

    def test_server_with_schema(self) -> None:
        """Test server with schema field."""
        now = datetime.now()
        data = {
            '$schema': 'https://example.com/schema.json',
            'name': 'test-server',
            'description': 'A test server',
            'status': 'active',
            'repository': {'url': 'https://github.com/test/repo', 'source': 'github'},
            'version': '1.0.0',
            '_meta': {
                'io.modelcontextprotocol.registry/official': {
                    'id': 'test-id',
                    'published_at': now,
                    'updated_at': now,
                    'is_latest': True,
                },
            },
        }
        server = Server.model_validate(data)
        assert str(server.schema_) == 'https://example.com/schema.json'

    def test_server_missing_required_field(self) -> None:
        """Test server validation fails with missing required field."""
        data = {
            'description': 'A test server',
            'status': 'active',
            'repository': {'url': 'https://github.com/test/repo', 'source': 'github'},
            'version': '1.0.0',
        }
        with pytest.raises(ValidationError):
            Server.model_validate(data)

    def test_server_without_status(self) -> None:
        """Test server without status field."""
        now = datetime.now()
        data = {
            'name': 'test-server',
            'description': 'A test server',
            'repository': {'url': 'https://github.com/test/repo', 'source': 'github'},
            'version': '1.0.0',
            '_meta': {
                'io.modelcontextprotocol.registry/official': {
                    'id': 'test-id',
                    'published_at': now,
                    'updated_at': now,
                    'is_latest': True,
                },
            },
        }
        server = Server.model_validate(data)
        assert server.name == 'test-server'
        assert server.description == 'A test server'
        assert server.status is None
        assert server.version == '1.0.0'

    def test_server_with_inactive_status(self) -> None:
        """Test server with inactive status."""
        now = datetime.now()
        data = {
            'name': 'test-server',
            'description': 'A test server',
            'status': 'inactive',
            'repository': {'url': 'https://github.com/test/repo', 'source': 'github'},
            'version': '1.0.0',
            '_meta': {
                'io.modelcontextprotocol.registry/official': {
                    'id': 'test-id',
                    'published_at': now,
                    'updated_at': now,
                    'is_latest': True,
                },
            },
        }
        server = Server.model_validate(data)
        assert server.name == 'test-server'
        assert server.description == 'A test server'
        assert server.status == 'inactive'
        assert server.version == '1.0.0'


class TestSearchResponse:
    """Tests for SearchResponse model."""

    def test_empty_search_response(self) -> None:
        """Test search response with empty servers list."""
        data: dict[str, list] = {'servers': []}
        response = SearchResponse.model_validate(data)
        assert response.servers == []

    def test_search_response_with_servers(self) -> None:
        """Test search response with servers."""
        now = datetime.now()
        data = {
            'servers': [
                {
                    'name': 'test-server-1',
                    'description': 'First test server',
                    'status': 'active',
                    'repository': {
                        'url': 'https://github.com/test/repo1',
                        'source': 'github',
                    },
                    'version': '1.0.0',
                    '_meta': {
                        'io.modelcontextprotocol.registry/official': {
                            'id': 'test-id-1',
                            'published_at': now,
                            'updated_at': now,
                            'is_latest': True,
                        },
                    },
                },
                {
                    'name': 'test-server-2',
                    'description': 'Second test server',
                    'status': 'active',
                    'repository': {
                        'url': 'https://github.com/test/repo2',
                        'source': 'github',
                    },
                    'version': '2.0.0',
                    '_meta': {
                        'io.modelcontextprotocol.registry/official': {
                            'id': 'test-id-2',
                            'published_at': now,
                            'updated_at': now,
                            'is_latest': True,
                        },
                    },
                },
            ],
        }
        response = SearchResponse.model_validate(data)
        assert len(response.servers) == 2
        assert response.servers[0].name == 'test-server-1'
        assert response.servers[1].name == 'test-server-2'
