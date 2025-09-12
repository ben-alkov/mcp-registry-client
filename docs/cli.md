# CLI Reference

The `mcp-registry` command-line tool provides an easy way to search and explore
MCP servers from the registry.

## Global Options

These options are available for all commands:

### `--verbose`, `-v`

Enable verbose logging output.

```bash
mcp-registry --verbose search
```

### `--json`

Output results in JSON format instead of human-readable tables.

```bash
mcp-registry --json search
```

## Commands

### `search`

Search for MCP servers in the registry.

**Usage:**

```bash
mcp-registry search [OPTIONS]
```

**Options:**

- `--name NAME`: Filter servers by name (partial matching supported)

**Examples:**

Search all servers:

```bash
mcp-registry search
```

Search for Gmail-related servers:

```bash
mcp-registry search --name gmail
```

Get search results as JSON:

```bash
mcp-registry search --json --name postgres
```

**Output Format:**

Default table format:

```text
NAME                     VERSION    DESCRIPTION
ai.waystation/gmail      0.3.1      Read emails, send messages, and manage...
app.getdialer/dialer     1.0.0      An MCP server that provides your you m...
```

JSON format:

```json
[
  {
    "name": "ai.waystation/gmail",
    "description": "Read emails, send messages, and manage labels in your Gmail account.",
    "version": "0.3.1",
    "status": "active",
    "repository": "https://github.com/waystation-ai/mcp",
    "id": "00b9d4aa-56ab-4f32-9f9f-3b9d48ed023f",
    "published_at": "2025-09-09T14:46:07.969809594Z",
    "updated_at": "2025-09-09T14:46:07.969809594Z"
  }
]
```

### `info`

Get detailed information about a specific server.

**Usage:**

```bash
mcp-registry info [OPTIONS] SERVER_NAME
```

**Arguments:**

- `SERVER_NAME`: The name of the server to get information about

**Examples:**

Get server information:

```bash
mcp-registry info "ai.waystation/gmail"
```

Get server info as JSON:

```bash
mcp-registry info --json "ai.waystation/gmail"
```

**Output Format:**

Default human-readable format:

```text
Name: ai.waystation/gmail
Description: Read emails, send messages, and manage labels in your Gmail account.
Version: 0.3.1
Status: active
Repository: https://github.com/waystation-ai/mcp
ID: 00b9d4aa-56ab-4f32-9f9f-3b9d48ed023f
Published: 2025-09-09 14:46:07.969810+00:00
Updated: 2025-09-09 14:46:07.969810+00:00

Remotes (2):
  - streamable-http: https://waystation.ai/gmail/mcp
  - sse: https://waystation.ai/gmail/mcp/sse
```

JSON format includes complete server details including packages, environment
variables, and metadata.

## Exit Codes

- `0`: Success
- `1`: Error (API error, server not found, etc.)
- `130`: Interrupted by user (Ctrl+C)

## Environment Variables

Currently, no environment variables are used by the CLI tool. All configuration
is done through command-line options.

## Examples

### Find all database-related servers

```bash
mcp-registry search --name database
```

### Get complete information about a specific server

```bash
mcp-registry info --json "io.github.domdomegg/airtable-mcp-server"
```

### Search and filter with external tools

```bash
# Find all servers and filter with jq
mcp-registry search --json | jq '.[] | select(.description | contains("API"))'

# Get server names only
mcp-registry search --json | jq -r '.[].name'
```

### Verbose output for debugging

```bash
mcp-registry --verbose search --name test
```
