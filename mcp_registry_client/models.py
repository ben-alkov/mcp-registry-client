"""Pydantic models for MCP registry API responses."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field, HttpUrl


class Repository(BaseModel):
    """Repository information for an MCP server."""

    url: str
    source: str
    id_: str | None = Field(None, alias='id')
    subfolder: str | None = None

    model_config = {'populate_by_name': True}


class Remote(BaseModel):
    """Remote endpoint configuration for an MCP server."""

    type_: str = Field(alias='type')
    url: HttpUrl

    model_config = {'populate_by_name': True}


class EnvironmentVariable(BaseModel):
    """Environment variable configuration for a package."""

    name: str
    description: str | None = None
    is_required: bool | None = None
    is_secret: bool | None = None
    format_: str | None = Field(None, alias='format')

    model_config = {'populate_by_name': True}


class PackageArgument(BaseModel):
    """Package argument configuration."""

    name: str | None = None  # Made optional to handle missing names
    type_: str = Field(alias='type')
    description: str | None = None
    format_: str | None = Field(None, alias='format')
    is_required: bool | None = None
    default: str | int | bool | None = None
    value: str | None = None

    model_config = {'populate_by_name': True}


class Transport(BaseModel):
    """Transport configuration for a package."""

    type_: str = Field(alias='type')
    url: str | None = None  # Changed from HttpUrl to str to handle templates

    model_config = {'populate_by_name': True}


class Package(BaseModel):
    """Package information for an MCP server."""

    registry_type: str
    identifier: str
    version: str
    registry_base_url: HttpUrl | None = None
    runtime_hint: str | None = None
    file_sha256: str | None = None
    transport: Transport | None = None
    environment_variables: list[EnvironmentVariable] | None = None
    package_arguments: list[PackageArgument] | None = None


class OfficialMeta(BaseModel):
    """Official registry metadata."""

    id_: str = Field(alias='id')
    published_at: datetime
    updated_at: datetime
    is_latest: bool

    model_config = {'populate_by_name': True}


class ServerMeta(BaseModel):
    """Server metadata container."""

    official: OfficialMeta = Field(alias='io.modelcontextprotocol.registry/official')

    model_config = {'populate_by_name': True}


class Server(BaseModel):
    """MCP server definition."""

    schema_: HttpUrl | None = Field(None, alias='$schema')
    name: str
    description: str
    status: str | None = None
    repository: Repository
    version: str
    remotes: list[Remote] | None = None
    packages: list[Package] | None = None
    meta: ServerMeta = Field(alias='_meta')

    model_config = {'populate_by_name': True}


class SearchResponse(BaseModel):
    """Response from the servers search endpoint."""

    servers: list[Server]


class RegistryError(BaseModel):
    """Error response from the registry API."""

    error: str
    message: str | None = None
    details: dict[str, Any] | None = None
