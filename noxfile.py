# mypy: ignore-errors

"""Nox sessions for development workflow."""

import nox


@nox.session
def format_source(session) -> None:
    """Format code with ruff."""
    session.install('ruff')
    session.run('ruff', 'format', '.')
    session.run('ruff', 'check', '--fix', '.')


@nox.session
def lint(session) -> None:
    """Run linting and formatting checks."""
    session.install('ruff')
    session.run('ruff', 'check', '.')
    session.run('ruff', 'format', '--check', '.')


@nox.session
def security(session) -> None:
    """Run security analysis with bandit."""
    session.install('bandit')
    session.run('bandit', '-r', 'mcp_registry_client')


@nox.session
def type_check(session) -> None:
    """Run type checking with mypy."""
    session.install('.[dev]')
    session.run('mypy', 'mcp_registry_client')


@nox.session(python=['3.12', '3.13'])
def tests(session) -> None:
    """Run the test suite."""
    session.install('.[dev]')
    session.run('pytest', '-m', 'not benchmark')


@nox.session
def docs(session) -> None:
    """Build documentation."""
    session.install('.[docs]')
    session.run('mkdocs', 'build')


@nox.session(default=False)
def docs_serve(session) -> None:
    """Serve documentation locally."""
    session.install('.[docs]')
    session.run('mkdocs', 'serve')


@nox.session
def quality(session) -> None:
    """Run all quality checks."""
    session.install('.[dev]')
    session.run('nox', '-s', 'format_source')
    session.run('nox', '-s', 'lint')
    session.run('nox', '-s', 'type_check')
    session.run('nox', '-s', 'security')
    session.run('nox', '-s', 'tests')
