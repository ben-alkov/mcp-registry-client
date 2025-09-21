
# Implementation Plan: Claude Code MCP Registry Integration

**Branch**: `001-add-feature-s` | **Date**: 2025-09-16 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/001-add-feature-s/spec.md`

## Execution Flow (/plan command scope)

1. Load feature spec from Input path
   → If not found: ERROR "No feature spec at {path}"
2. Fill Technical Context (scan for NEEDS CLARIFICATION)
   → Detect Project Type from context (web=frontend+backend)
   → Set Structure Decision based on project type
3. Fill the Constitution Check section based on the content of the constitution document.
4. Evaluate Constitution Check section below
   → If violations exist: Document in Complexity Tracking
   → If no justification possible: ERROR "Simplify approach first"
   → Update Progress Tracking: Initial Constitution Check
5. Execute Phase 0 → research.md
   → If NEEDS CLARIFICATION remain: ERROR "Resolve unknowns"
6. Execute Phase 1 → contracts, data-model.md, quickstart.md, agent-specific
   template file (e.g., `CLAUDE.md` for Claude Code,
   `.github/copilot-instructions.md` for GitHub Copilot, or `GEMINI.md` for
   Gemini CLI).
7. Re-evaluate Constitution Check section
   → If new violations: Refactor design, return to Phase 1
   → Update Progress Tracking: Post-Design Constitution Check
8. Plan Phase 2 → Describe task generation approach (DO NOT create tasks.md)
9. STOP - Ready for /tasks command

**IMPORTANT**: The /plan command STOPS at step 7. Phases 2-4 are executed by other commands:

- Phase 2: /tasks command creates tasks.md
- Phase 3-4: Implementation execution (manual or via tools)

## Summary

This feature enables Claude Code to search and install MCP servers from the
registry through natural language conversation. Users can discover servers,
browse paginated results, view detailed information, and install servers with
configuration target selection. The implementation extends the existing MCP
registry client with Claude Code-specific integration capabilities.

## Technical Context

- **Language/Version**: Python 3.12+ (existing project constraint)
- **Primary Dependencies**: httpx (async HTTP), pydantic (data validation),
  click (CLI)
- **Storage**: N/A (stateless API client)
- **Testing**: pytest with asyncio, integration tests against real registry API
- **Target Platform**: Claude Code CLI environment (Linux/macOS/Windows)
- **Project Type**: single (library extension)
- **Performance Goals**: <2s search response, <1s server details retrieval
- **Constraints**: Must work offline-first with caching, handle API rate limits gracefully
- **Scale/Scope**: Support 1000+ registry servers, handle concurrent searches

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### I. Library-First Architecture: ✅ PASS

- Feature extends existing library with clear boundaries
- Self-contained Claude Code integration module
- Independent testability through CLI interface

### II. CLI Interface Mandate: ✅ PASS

- Extends existing CLI with Claude Code-specific commands
- JSON and human-readable output support
- Composable and scriptable interface

### III. Test-First Development: ✅ PASS

- TDD approach mandated
- Integration tests with real registry API
- Contract tests for Claude Code integration

### IV. Integration-First Testing: ✅ PASS

- Tests against actual MCP registry endpoints
- Contract tests for Claude Code integration
- Performance benchmarks for search operations

### V. Type Safety and Modern Python: ✅ PASS

- Extends existing Pydantic models
- Comprehensive type hints required
- Python 3.12+ features usage

### VI. Simplicity and Anti-Abstraction: ✅ PASS

- Direct extension of existing client architecture
- No new abstraction layers needed
- Leverages existing patterns

### VII. Observability: ✅ PASS

- Structured logging for Claude Code interactions
- Debug modes for troubleshooting
- Error context preservation

### VIII. Versioning & Breaking Changes: ✅ PASS

- Non-breaking addition to existing API
- Semantic versioning compliance

### IX. Backward Compatibility: ✅ PASS

- Additive changes only
- Existing functionality preserved

## Project Structure

### Documentation (this feature)

```text
specs/001-add-feature-s/
├── plan.md              # This file (/plan command output)
├── research.md          # Phase 0 output (/plan command)
├── data-model.md        # Phase 1 output (/plan command)
├── quickstart.md        # Phase 1 output (/plan command)
├── contracts/           # Phase 1 output (/plan command)
└── tasks.md             # Phase 2 output (/tasks command - NOT created by /plan)
```

### Source Code (repository root)

```text
# Single project structure (existing)
mcp_registry_client/
├── models.py           # Extend with Claude Code models
├── client.py           # Extend with Claude Code methods
├── claude_integration.py # New: Claude Code specific logic
├── cli.py              # Extend with Claude Code commands
└── commands/
    └── claude.py       # New: Claude Code command handlers

tests/
├── contract/           # Claude Code integration contracts
├── integration/        # Claude Code integration tests
└── unit/              # Unit tests for new components
```

**Structure Decision**: Option 1 (single project) - extends existing MCP registry client

## Phase 0: Outline & Research

1. **Extract unknowns from Technical Context** above:
   - Claude Code MCP tool integration patterns
   - Claude Code configuration management (global vs project)
   - Claude Code error handling and user feedback conventions
   - MCP server installation procedures and validation

2. **Generate and dispatch research agents**:

   Task: "Research Claude Code MCP tool integration patterns for registry integration"
   Task: "Find best practices for Claude Code configuration management patterns"
   Task: "Research Claude Code error handling and user feedback conventions"
   Task: "Find MCP server installation procedures and validation approaches"

3. **Consolidate findings** in `research.md` using format:
   - Decision: [what was chosen]
   - Rationale: [why chosen]
   - Alternatives considered: [what else evaluated]

**Output**: research.md with all unknowns resolved

## Phase 1: Design & Contracts

- Prerequisites: research.md complete -

1. **Extract entities from feature spec** → `data-model.md`:
   - ClaudeSearchRequest (query, pagination params)
   - ClaudeSearchResponse (servers, pagination info)
   - ClaudeServerDetail (full server information)
   - ClaudeInstallRequest (server ID, config target)
   - ClaudeInstallResponse (status, configuration)

2. **Generate API contracts** from functional requirements:
   - Claude Code search endpoint interface
   - Claude Code server detail interface
   - Claude Code installation interface
   - Error response schemas
   - Output OpenAPI schemas to `/contracts/`

3. **Generate contract tests** from contracts:
   - Test Claude Code search integration
   - Test Claude Code server detail retrieval
   - Test Claude Code installation flow
   - Tests must fail (no implementation yet)

4. **Extract test scenarios** from user stories:
   - Search MCP servers scenario
   - Browse paginated results scenario
   - Get server details scenario
   - Install server with config selection scenario

5. **Update agent file incrementally** (O(1) operation):
   - Run `.specify/scripts/bash/update-agent-context.sh claude` for Claude Code
   - Add Claude Code integration context
   - Update with MCP registry integration capabilities
   - Keep under 150 lines for token efficiency

**Output**: data-model.md, /contracts/*, failing tests, quickstart.md, CLAUDE.md

## Phase 2: Task Planning Approach

- This section describes what the /tasks command will do - DO NOT execute during /plan -

**Task Generation Strategy**:

- Load `.specify/templates/tasks-template.md` as base
- Generate tasks from Phase 1 design docs (contracts, data model, quickstart)
- Each contract → contract test task [P]
- Each entity → model creation task [P]
- Each user story → integration test task
- Implementation tasks to make tests pass

**Ordering Strategy**:

- TDD order: Tests before implementation
- Dependency order: Models before services before CLI
- Mark [P] for parallel execution (independent files)

**Estimated Output**: 20-25 numbered, ordered tasks in tasks.md

**IMPORTANT**: This phase is executed by the /tasks command, NOT by /plan

## Phase 3+: Future Implementation

- These phases are beyond the scope of the /plan command -

**Phase 3**: Task execution (/tasks command creates tasks.md)
**Phase 4**: Implementation (execute tasks.md following constitutional principles)
**Phase 5**: Validation (run tests, execute quickstart.md, performance validation)

## Complexity Tracking

- Fill ONLY if Constitution Check has violations that must be justified -

No constitutional violations identified - all requirements align with existing architecture.

## Progress Tracking

- This checklist is updated during execution flow -

**Phase Status**:

- [x] Phase 0: Research complete (/plan command)
- [x] Phase 1: Design complete (/plan command)
- [x] Phase 2: Task planning complete (/plan command - describe approach only)
- [ ] Phase 3: Tasks generated (/tasks command)
- [ ] Phase 4: Implementation complete
- [ ] Phase 5: Validation passed

**Gate Status**:

- [x] Initial Constitution Check: PASS
- [x] Post-Design Constitution Check: PASS
- [x] All NEEDS CLARIFICATION resolved
- [x] Complexity deviations documented

---
*Based on Constitution v1.1.0 - See `.specify/memory/constitution.md`*
