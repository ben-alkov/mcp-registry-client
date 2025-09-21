# Data Model: Claude Code MCP Registry Integration

**Design Date**: 2025-09-16
**Prerequisites**: research.md complete

## Entity Definitions

### ClaudeSearchRequest

**Purpose**: Represents a search request from Claude Code users for MCP servers
in the registry.

**Fields**:

- `query: Optional[str]` - Natural language search query (e.g., "JIRA",
  "database tools")
- `page: int = 1` - Page number for pagination (1-based indexing)
- `limit: int = 10` - Number of results per page (default 10, max 50)
- `category: Optional[str]` - Filter by category if supported by registry

**Validation Rules**:

- `page` must be >= 1
- `limit` must be between 1 and 50
- `query` can be empty for browsing all servers
- `category` must match registry-supported categories

**Example**:

```python
  ClaudeSearchRequest(
      query="JIRA integration",
      page=1,
      limit=10
  )
```

### ClaudeSearchResponse

**Purpose**: Contains paginated search results formatted for Claude Code presentation.

**Fields**:

- `servers: List[ClaudeServerSummary]` - List of matching servers
- `total_count: int` - Total number of matching servers
- `page: int` - Current page number
- `total_pages: int` - Total number of pages
- `has_next: bool` - Whether more pages are available
- `has_previous: bool` - Whether previous pages exist

**Validation Rules**:

- `servers` list length must not exceed requested limit
- `total_count` must be >= 0
- `page` must be >= 1 and <= `total_pages`
- `total_pages` calculated as `ceil(total_count / limit)`

**Relationships**:

- Contains list of `ClaudeServerSummary` entities
- Derived from core `SearchResponse` with Claude-specific formatting

### ClaudeServerSummary

**Purpose**: Abbreviated server information for search results display.

**Fields**:

- `name: str` - Server identifier (org/repo format)
- `description: str` - Brief description (truncated to 200 chars)
- `repository_url: str` - GitHub repository URL
- `version: Optional[str]` - Latest version if available
- `category: Optional[str]` - Server category
- `tools_count: Optional[int]` - Number of tools provided

**Validation Rules**:

- `name` must follow org/repo pattern (validated regex)
- `description` must be truncated with "..." if > 200 chars
- `repository_url` must be valid GitHub URL
- `version` must follow semver if present

**Example**:

```python
ClaudeServerSummary(
    name="atlassian/mcp-jira",
    description="MCP server for JIRA integration with issue management, project tracking...",
    repository_url="https://github.com/atlassian/mcp-jira",
    version="1.2.0",
    category="project-management",
    tools_count=8
)
```

### ClaudeServerDetail

**Purpose**: Complete server information for detailed view and installation decisions.

**Fields**:

- `name: str` - Server identifier
- `description: str` - Full description
- `repository_url: str` - GitHub repository URL
- `version: str` - Latest version
- `category: Optional[str]` - Server category
- `tools: List[ClaudeToolInfo]` - Available tools
- `installation: ClaudeInstallationInfo` - Installation requirements
- `documentation_url: Optional[str]` - Documentation link
- `license: Optional[str]` - License type
- `author: Optional[str]` - Author/organization
- `tags: List[str]` - Search tags

**Validation Rules**:

- All fields from `ClaudeServerSummary` plus additional detail fields
- `tools` list must not be empty
- `installation` must contain valid installation info
- URLs must be validated format

**Relationships**:

- Contains list of `ClaudeToolInfo` entities
- Contains `ClaudeInstallationInfo` entity
- Extended from core `Server` with Claude-specific formatting

### ClaudeToolInfo

**Purpose**: Information about individual tools provided by an MCP server.

**Fields**:

- `name: str` - Tool name
- `description: str` - Tool description
- `parameters: List[str]` - Parameter names (simplified view)

**Validation Rules**:

- `name` must be valid tool identifier
- `description` must be non-empty
- `parameters` list can be empty

### ClaudeInstallationInfo

**Purpose**: Installation requirements and procedures for an MCP server.

**Fields**:

- `command: str` - Installation command or executable path
- `args: List[str]` - Command arguments
- `env_vars: Dict[str, str]` - Required environment variables
- `requirements: List[str]` - System requirements (e.g., "Node.js >= 18")
- `installation_type: str` - Type: "npm", "pip", "binary", "git", "docker"

**Validation Rules**:

- `command` must be non-empty
- `installation_type` must be from allowed values
- `env_vars` keys must follow environment variable naming

### ClaudeInstallRequest

**Purpose**: User request to install a specific MCP server with configuration preferences.

**Fields**:

- `server_name: str` - Server identifier to install
- `scope: str` - Installation scope: "local", "project", or "user"
- `env_overrides: Dict[str, str] = {}` - Environment variable overrides
- `custom_name: Optional[str]` - Custom server name for configuration

**Validation Rules**:

- `server_name` must match existing server in registry
- `scope` must be one of: "local", "project", "user"
- `env_overrides` keys must be valid environment variable names
- `custom_name` must be valid MCP server identifier if provided

**State Transitions**:

1. `pending` → User submits install request
2. `validating` → Checking server availability and requirements
3. `installing` → Executing installation commands
4. `completed` → Installation successful
5. `failed` → Installation failed with error details

### ClaudeInstallResponse

**Purpose**: Result of an MCP server installation attempt.

**Fields**:

- `status: str` - Installation status: "success", "error", "pending"
- `message: str` - Human-readable status message
- `server_name: str` - Server that was installed
- `scope: str` - Scope where server was installed
- `config_location: Optional[str]` - Path to configuration file
- `next_steps: List[str]` - Suggested next actions

**Validation Rules**:

- `status` must be from allowed values
- `message` must be non-empty and descriptive
- `config_location` must be valid file path if provided
- `next_steps` should provide actionable guidance

**Error Handling**:

- Include specific error codes for different failure types
- Provide rollback instructions for partial failures
- Suggest alternative installation methods when applicable

## Entity Relationships

```text
ClaudeSearchRequest → ClaudeSearchResponse
    └── contains List[ClaudeServerSummary]

ClaudeServerDetail
    ├── contains List[ClaudeToolInfo]
    └── contains ClaudeInstallationInfo

ClaudeInstallRequest → ClaudeInstallResponse
```

## Data Flow Patterns

### Search Flow

1. User provides natural language query
2. `ClaudeSearchRequest` created with pagination
3. Core `RegistryClient` performs search
4. Results mapped to `ClaudeSearchResponse` with `ClaudeServerSummary` list
5. Formatted response returned to Claude Code

### Installation Flow

1. User selects server from search results
2. System creates `ClaudeServerDetail` request
3. User confirms installation with scope choice
4. `ClaudeInstallRequest` created with user preferences
5. Installation process executed with validation
6. `ClaudeInstallResponse` returned with status and next steps

## Validation Strategy

### Input Validation

- Use Pydantic models for all entities
- Runtime validation at API boundaries
- Type hints for comprehensive type checking
- Custom validators for complex business rules

### Error Context Preservation

- Structured error responses with context
- Error codes for programmatic handling
- User-friendly error messages
- Suggested remediation actions

### Performance Considerations

- Pagination for large result sets
- Caching of search results with TTL
- Lazy loading of detailed server information
- Async operations for all I/O

## Implementation Notes

These models extend the existing core models in `mcp_registry_client/models.py`
while adding Claude Code-specific formatting and validation. The design
maintains backward compatibility while providing the structured interfaces
required for Claude Code integration.

All models will be implemented using Pydantic for validation and serialization,
following the constitutional requirement for type safety and modern Python
practices.
