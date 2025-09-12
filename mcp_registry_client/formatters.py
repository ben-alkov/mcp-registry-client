"""Output formatters for the MCP registry client."""

import json
import sys
from typing import Any

from .models import Package, Remote, Server


def format_env_variables(package: Package) -> list[dict[str, Any]]:
    """Format environment variables for a package."""
    if not package.environment_variables:
        return []

    return [
        {
            'name': env.name,
            'description': env.description,
            'is_required': env.is_required,
            'is_secret': env.is_secret,
            'format': env.format_,
        }
        for env in package.environment_variables
    ]


def format_package_info(package: Package) -> dict[str, Any]:
    """Format a single package for display."""
    package_data: dict[str, Any] = {
        'registry_type': package.registry_type,
        'identifier': package.identifier,
        'version': package.version,
    }

    if package.registry_base_url:
        package_data['registry_base_url'] = str(package.registry_base_url)

    if package.runtime_hint:
        package_data['runtime_hint'] = package.runtime_hint

    if package.transport:
        package_data['transport'] = {
            'type': package.transport.type_,
            'url': str(package.transport.url) if package.transport.url else None,
        }

    env_vars = format_env_variables(package)
    if env_vars:
        package_data['environment_variables'] = env_vars

    return package_data


def format_remotes(remotes: list[Remote]) -> list[dict[str, Any]]:
    """Format remotes list for display."""
    return [{'type': remote.type_, 'url': str(remote.url)} for remote in remotes]


def format_server_summary(server: Server) -> dict[str, Any]:
    """Format server information for display."""
    return {
        'name': server.name,
        'description': server.description,
        'version': server.version,
        'status': server.status or 'unknown',
        'repository': server.repository.url if server.repository.url else 'N/A',
        'id': server.meta.official.id_,
        'published_at': server.meta.official.published_at.isoformat(),
        'updated_at': server.meta.official.updated_at.isoformat(),
    }


def format_server_detailed(server: Server) -> dict[str, Any]:
    """Format detailed server information for display."""
    data: dict[str, Any] = {
        'name': server.name,
        'description': server.description,
        'version': server.version,
        'status': server.status or 'unknown',
        'schema': str(server.schema_) if server.schema_ else None,
        'repository': {
            'url': server.repository.url,
            'source': server.repository.source,
            'id': server.repository.id_,
            'subfolder': server.repository.subfolder,
        },
        'metadata': {
            'id': server.meta.official.id_,
            'published_at': server.meta.official.published_at.isoformat(),
            'updated_at': server.meta.official.updated_at.isoformat(),
            'is_latest': server.meta.official.is_latest,
        },
    }

    if server.remotes:
        data['remotes'] = format_remotes(server.remotes)

    if server.packages:
        data['packages'] = [format_package_info(package) for package in server.packages]

    return data


def print_json(data: dict[str, Any] | list[dict[str, Any]], *, indent: int = 2) -> None:
    """Print data as formatted JSON."""
    print(json.dumps(data, indent=indent))  # noqa: T201


def print_table(servers: list[Server], max_description_width: int = 60) -> None:
    """Print servers in a simple table format.

    Args:
        servers: List of servers to display
        max_description_width: Maximum width for description column

    """
    if not servers:
        print('No servers found.')  # noqa: T201
        return

    # Calculate column widths
    name_width = max(len('NAME'), *(len(s.name) for s in servers))
    desc_width = min(
        max_description_width,
        max(len('DESCRIPTION'), *(len(s.description) for s in servers)),
    )
    version_width = max(len('VERSION'), *(len(s.version) for s in servers))

    # Print header
    header = (
        f'{"NAME":<{name_width}} {"DESCRIPTION":<{desc_width}} {"VERSION":<{version_width}}'
    )
    print(header)  # noqa: T201
    print('-' * len(header))  # noqa: T201

    # Print servers
    for server in servers:
        desc = server.description
        if len(desc) > desc_width:
            desc = desc[: desc_width - 3] + '...'

        print(  # noqa: T201
            f'{server.name:<{name_width}} {desc:<{desc_width}} '
            f'{server.version:<{version_width}}'
        )


def print_server_info_human_readable(server: Server) -> None:
    """Print server information in human-readable format."""
    print(f'Name: {server.name}')  # noqa: T201
    print(f'Description: {server.description}')  # noqa: T201
    print(f'Version: {server.version}')  # noqa: T201
    print(f'Status: {server.status or "unknown"}')  # noqa: T201
    print(f'Repository: {server.repository.url if server.repository.url else "N/A"}')  # noqa: T201

    if server.remotes:
        print('\nRemotes:')  # noqa: T201
        for remote in server.remotes:
            print(f'  - {remote.type_}: {remote.url}')  # noqa: T201

    if server.packages:
        print('\nPackages:')  # noqa: T201
        for package in server.packages:
            print(f'  - {package.identifier} ({package.version})')  # noqa: T201


def print_error(message: str) -> None:
    """Print error message to stderr."""
    print(message, file=sys.stderr)  # noqa: T201
