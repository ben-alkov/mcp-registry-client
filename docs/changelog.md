# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog][], and this project adheres to
[Semantic Versioning][].

## Unreleased - 2025-09-09

### Features

- Initial implementation of MCP Registry Client
- Support for MCP Registry API v0
- Support for server search by name
- Server info retrieval by name
- CLI interface with search and info commands
- Command-line interface with argparse
- Async HTTP client for MCP registry API
- JSON and table output formats
- Comprehensive pytest test suite
- Type-safe Pydantic models
- Modern Python packaging with uv
- Documentation with mkdocs-material
- Code quality tooling (bandit, mypy, ruff)
- Nox-based development workflow

### Security

- No hardcoded secrets or credentials

### Technical Details

- Python 3.12+ support
- httpx for async HTTP requests
- Pydantic v2 for data validation
- argparse for CLI interface
- pytest for testing, with codecov
- mkdocs-material for documentation
- ruff for linting and formatting
- mypy for type checking
- bandit for security analysis
- nox for development workflow automation

## Unrealeased - 2025-09-10 - 12

### Additions

- Refactoring
- Config system: defaults with overrides via "config.toml"
- Async/await support throughout
- Full-featured async client for registry API
- Proper exception hierarchy and error messages
- command pattern for CLI subcommands
- Integration tests
- Benchmark/performance tests
- 93% overall coverage (some modules are still 70 < covered < 90)
- Response caching for repeated server lookups
- Implement request pooling for batch operations
- Request timeout configuration options

For more gritty details, check "agent notes/progress-*.md"

Security:

- Input validation

---

## Release Notes Template

When creating a new release, use this template:

```markdown
## [X.Y.Z] - YYYY-MM-DD

### Added
- New features and functionality

### Changed
- Changes to existing features
- Breaking changes (if any)

### Deprecated
- Features that will be removed in future versions

### Removed
- Features that have been removed

### Fixed
- Bug fixes

### Security
- Security improvements and fixes
```

[Keep a Changelog]: https://keepachangelog.com/en/1.0.0
[Semantic Versioning]: https://semver.org/spec/v2.0.0.html
