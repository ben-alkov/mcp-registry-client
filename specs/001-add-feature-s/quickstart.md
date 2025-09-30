# Quickstart: Claude Code MCP Registry Integration

## Prerequisites

- Phase 0 research.md complete
- Phase 1 data-model.md and contracts complete
- Core MCP registry client functional

## Integration Test Scenarios

### Scenario 1: Search MCP Servers

**Objective**: Verify users can search for MCP servers using natural language queries

- Test Steps -

1. User asks Claude Code: "Find an MCP server for JIRA in the registry"
2. Claude Code calls `mcp__registry__search_servers` with query="JIRA"
3. System returns formatted list of matching servers
4. User sees readable results with server names, descriptions, and metadata

- Expected Results -

```text
Found 3 MCP servers matching "JIRA":

📦 **atlassian/mcp-jira -
   Comprehensive JIRA integration with issue management and project tracking
   Repository: https://github.com/atlassian/mcp-jira
   Version: 1.2.0 | Tools: 8

📦 **community/jira-simple -
   Lightweight JIRA client for basic issue operations
   Repository: https://github.com/community/jira-simple
   Version: 0.5.1 | Tools: 4

📦 **enterprise/jira-pro -
   Enterprise JIRA integration with advanced workflow support
   Repository: https://github.com/enterprise/jira-pro
   Version: 2.1.0 | Tools: 15

Say "get more info on [server]" for details or "install [server]" to add it.
```

- Validation Criteria -

- ✅ Natural language query processed correctly
- ✅ Registry API called with appropriate parameters
- ✅ Results formatted for human readability
- ✅ Pagination handled appropriately (≤10 results shown)
- ✅ Clear next steps provided to user

### Scenario 2: Browse Paginated Results

**Objective**: Verify pagination works for large result sets

- Test Steps -

1. User asks: "Show me all database MCP servers"
2. System returns first 10 results with pagination indicators
3. User requests: "Show me more results"
4. System returns next page of results

- Expected Results (Page 1) -

```text
Found 25 database MCP servers (showing 1-10)

📦 **postgres/mcp-postgres** ...
📦 **mysql/mcp-mysql** ...
[8 more servers]

Page 1 of 3 | Say "show page 2" or "more results" to continue
```

- Validation Criteria -

- ✅ Pagination metadata correctly calculated
- ✅ Page navigation works intuitively
- ✅ Total count and page indicators accurate
- ✅ "More results" natural language understood

### Scenario 3: Get Server Details

**Objective**: Verify users can get comprehensive server information

- Test Steps -

1. User asks: "Get more info on atlassian/mcp-jira"
2. Claude Code calls `mcp__registry__get_server_info` with server_name
3. System returns detailed server information
4. User sees full description, tools, installation requirements

- Expected Results -

```text
## 📦 atlassian/mcp-jira v1.2.0

**Description**: Comprehensive JIRA integration providing issue management,
project tracking, sprint management, and reporting capabilities. Supports
both cloud and server instances with OAuth2 and API token authentication.

**Tools Available** (8)
• create_issue - Create new JIRA issues
• get_issue - Retrieve issue details
• update_issue - Modify existing issues
• search_issues - Query issues with JQL
• get_projects - List accessible projects
• create_comment - Add comments to issues
• get_sprints - Retrieve sprint information
• get_board - Get board details

**Installation Requirements**
• Node.js >= 18.0.0
• Environment variables: JIRA_URL, JIRA_TOKEN
• Network access to JIRA instance

**Repository**: https://github.com/atlassian/mcp-jira
**License**: MIT | **Author**: Atlassian

Ready to install? Say "install atlassian/mcp-jira" to add it to your configuration.
```

- Validation Criteria -

- ✅ Server identifier validated and found
- ✅ Complete server information retrieved
- ✅ Tools and capabilities clearly listed
- ✅ Installation requirements specified
- ✅ Clear installation prompt provided

### Scenario 4: Install Server with Configuration Target Selection

**Objective**: Verify installation process with scope selection

- Test Steps -

1. User says: "Install atlassian/mcp-jira"
2. Claude Code prompts for installation scope choice
3. User selects scope (local/project/user)
4. System installs server with chosen configuration
5. User receives confirmation and next steps

- Expected Interaction -

```text
User: "Install atlassian/mcp-jira"

Claude Code: "I found the MCP server 'atlassian/mcp-jira' in the registry.

Where would you like to install it?

🔒 **Local** (recommended): Private to you in this project only
📁 **Project**: Shared with your team (adds to .mcp.json)
🌐 **User**: Available across all your projects

Choose local, project, or user (default: local):"

User: "project"

Claude Code: "✅ Successfully installed atlassian/mcp-jira with project scope!

📁 Configuration added to .mcp.json
🔧 Set these environment variables
   • JIRA_URL=https://your-domain.atlassian.net
   • JIRA_TOKEN=your-api-token

📖 Documentation: https://github.com/atlassian/mcp-jira#setup

The server will be available after you restart Claude Code or run /mcp to refresh."
```

- Validation Criteria -

- ✅ Server availability validated before installation
- ✅ Clear scope options presented with explanations
- ✅ User choice processed correctly
- ✅ Installation executes with proper scope
- ✅ Configuration files updated appropriately
- ✅ Clear next steps and setup instructions provided

### Scenario 5: Handle Error Cases

**Objective**: Verify graceful error handling and user guidance

- Test Cases -

#### A. Server Not Found

```text
User: "Get info on nonexistent/server"
Expected: "I couldn't find 'nonexistent/server' in the registry.
Did you mean 'existing/server'? Or try searching with different keywords."
```

#### B. Network Error

```text
User: "Search for database servers"
Expected: "I'm having trouble connecting to the MCP registry right now.
Please check your internet connection and try again."
```

#### C. Installation Failure

```text
User: "Install problematic/server"
Expected: "❌ Installation of 'problematic/server' failed
Missing required dependency: Node.js >= 18.0.0

Please install Node.js and try again, or check the server documentation
for alternative installation methods."
```

- Validation Criteria -

- ✅ Errors caught and handled gracefully
- ✅ User-friendly error messages provided
- ✅ Actionable guidance given
- ✅ Conversation flow maintained (no crashes)

## Performance Validation

### Response Time Requirements

- **Search queries**: < 2 seconds
- **Server details**: < 1 second
- **Installation**: < 30 seconds

### Caching Behavior

- Search results cached for 5 minutes
- Server details cached for 15 minutes
- Cache invalidation on installation

### Concurrent Operations

- Multiple searches supported simultaneously
- Installation operations serialized per scope

## Integration Checklist

### Pre-Implementation Tests

- [ ] Core registry client functional
- [ ] MCP server framework set up
- [ ] Claude Code test environment ready

### Contract Tests (Must Fail Before Implementation)

- [ ] `test_search_servers_contract()` - validates tool interface
- [ ] `test_get_server_info_contract()` - validates server detail interface
- [ ] `test_install_server_contract()` - validates installation interface
- [ ] `test_error_response_format()` - validates error handling format

### Integration Tests

- [ ] `test_search_with_natural_language()` - Scenario 1
- [ ] `test_pagination_flow()` - Scenario 2
- [ ] `test_server_detail_retrieval()` - Scenario 3
- [ ] `test_installation_with_scope_selection()` - Scenario 4
- [ ] `test_error_handling_scenarios()` - Scenario 5

### End-to-End Validation

- [ ] User story acceptance tests pass
- [ ] Performance requirements met
- [ ] Error recovery verified
- [ ] Configuration persistence confirmed

## Ready-to-Ship Criteria

1. ✅ All contract tests passing
2. ✅ All integration test scenarios validated
3. ✅ Performance benchmarks met
4. ✅ Error handling comprehensive
5. ✅ User experience smooth and intuitive
6. ✅ Documentation complete and accurate
7. ✅ Security considerations addressed
8. ✅ Constitutional compliance verified

This quickstart provides the complete validation framework for Claude Code MCP
registry integration, ensuring robust functionality and excellent user
experience.
