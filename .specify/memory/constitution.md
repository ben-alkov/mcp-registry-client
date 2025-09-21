# MCP Registry Client Constitution

## Core Principles

### I. Library-First Architecture

Every feature MUST begin as a standalone library with clear boundaries

- Libraries must be self-contained and independently testable
- Each library requires documented purpose and API contracts
- Modular design enables composition without tight coupling
- No organizational-only libraries - each must solve specific problems

### II. CLI Interface Mandate

Every library MUST expose core functionality through command-line interface

- Text-based I/O protocol: stdin/arguments → stdout, errors → stderr
- Support both JSON and human-readable output formats
- Commands must be composable and scriptable
- CLI serves as primary integration and testing interface

### III. Test-First Development (NON-NEGOTIABLE)

Strict Test-Driven Development MUST be followed

- Implementation order: Tests written → User approved → Tests fail → Implementation
- Red-Green-Refactor cycle strictly enforced
- No production code without corresponding tests
- Test coverage minimum 90% with focus on edge cases and error conditions

### IV. Integration-First Testing

Prioritize real-world testing over artificial isolation

- Integration tests MUST use actual API endpoints and services
- Contract tests mandatory before implementation
- Mock/stub usage only when external dependencies are unavailable
- Performance benchmarks required for API interactions

### V. Type Safety and Modern Python

Leverage Python's type system for reliability

- Comprehensive type hints required (mypy strict mode)
- Pydantic models for all external data structures
- Runtime validation at API boundaries
- Python 3.12+ features and modern tooling (uv, ruff, nox)

### VI. Simplicity and Anti-Abstraction

Start simple, add complexity only when proven necessary

- Direct framework/library usage over custom abstractions
- YAGNI principles - no speculative features
- Clear justification required for any abstraction layer
- Prefer composition over inheritance

### VII. Observability

Ensure debuggability and operational transparency

- Structured logging for all API interactions and errors
- Debug modes with detailed request/response tracing
- Error context preservation throughout call chains
- CLI verbose flags for troubleshooting support

### VIII. Versioning & Breaking Changes

Maintain stability while enabling evolution

- Semantic versioning (MAJOR.MINOR.PATCH) strictly enforced
- Breaking changes only in major versions with documented rationale
- Deprecation warnings with 2-version minimum lifecycle
- Migration guides required for all breaking changes

### IX. Backward Compatibility

Protect existing integrations and workflows

- Configuration format stability within major versions
- API contract preservation for minor/patch releases
- Clear upgrade paths with automated migration tools where possible
- Legacy support timeline documented in release notes

## Quality and Performance Standards

### Code Quality Requirements

- Linting: ruff with strict configuration (no violations allowed)
- Security: bandit security analysis for all code
- Format: ruff formatting with consistent style
- Documentation: comprehensive docstrings and usage examples

### Performance Standards

- API response caching with configurable TTL
- Retry logic with exponential backoff for resilience
- Async/await for all I/O operations
- Benchmark tests to prevent performance regressions

### Technology Stack Constraints

- Python 3.12+ only
- httpx for async HTTP operations
- Pydantic for data validation and serialization
- pytest ecosystem for testing (pytest-asyncio, pytest-benchmark)
- Modern Python tooling: uv, ruff, mypy, nox, mkdocs-material

## Development Workflow

### Quality Gates

All code MUST pass these gates before merge

1. **Testing Gate**: All tests pass (unit, integration, benchmark)
2. **Coverage Gate**: ≥90% test coverage maintained
3. **Type Gate**: mypy type checking passes with strict configuration
4. **Lint Gate**: ruff linting passes with zero violations
5. **Security Gate**: bandit security analysis passes
6. **Format Gate**: code follows ruff formatting standards

### Development Environment

- Virtual environments required for all development work
- nox sessions for isolated, reproducible builds
- IDE diagnostics integration for real-time feedback
- Documentation builds required for API changes

### Error Handling Standards

- Custom exception hierarchy (RegistryClientError, RegistryAPIError)
- Centralized error handling with user-friendly messages
- Comprehensive error condition testing
- Graceful degradation for network and API failures

## Governance

### Constitutional Authority

This constitution supersedes all other development practices and guidelines

- All code reviews MUST verify constitutional compliance
- Any deviation requires explicit justification and documentation
- Complexity additions require architectural review and approval
- Quality gates are non-negotiable - no exceptions without amendment

### Amendment Process

Constitutional changes require

- Documented rationale with impact analysis
- Review and approval by project maintainers
- Migration plan for existing code
- Version increment and amendment date update

### Compliance Verification

- nox `quality` session verifies all constitutional requirements
- CI/CD pipeline enforces quality gates automatically
- IDE diagnostics provide real-time compliance feedback
- Documentation updates required for any constitutional changes

**Version**: 1.1.0 | **Ratified**: 2025-09-16 | **Last Amended**: 2025-09-16
