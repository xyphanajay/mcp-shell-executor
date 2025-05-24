# MCP Shell Executor

A comprehensive Model Context Protocol (MCP) server that enables LLMs to execute shell commands on Linux systems with advanced safety features and output management.

## Features

- **Safe Command Execution**: Execute bash commands with timeout protection and output limits
- **Script Support**: Run multi-line bash scripts from string content
- **Security Options**: Optional command allowlisting and working directory validation
- **Comprehensive Output**: Formatted results including exit codes, stdout, stderr
- **System Information**: Built-in resources for system info and current directory
- **Error Handling**: Robust error handling for various failure scenarios

## Installation

### Prerequisites

- Python 3.8 or higher
- Linux-based operating system
- MCP Python SDK

### Setup

1. Clone the repository:
```bash
git clone https://github.com/xyphanajay/mcp-shell-executor.git
cd mcp-shell-executor
```

2. Install dependencies:
```bash
# Using uv (recommended)
uv add "mcp[cli]"

# Or using pip
pip install "mcp[cli]"
```

3. Install the server:
```bash
# Install in Claude Desktop
mcp install server.py --name "Shell Executor"

# Or test in development mode
mcp dev server.py
```

## Usage

### Tools

#### `run_bash_command`
Execute a single bash command:
```python
run_bash_command(
    command="ls -la",
    working_directory="/tmp",  # Optional
    timeout=30                 # Optional (seconds)
)
```

#### `run_bash_script`
Execute a multi-line bash script:
```python
run_bash_script(
    script_content="""#!/bin/bash
    echo "System Information:"
    uname -a
    date
    uptime
    """,
    working_directory="/home/user",  # Optional
    timeout=60                       # Optional (seconds)
)
```

### Resources

- `system://info` - Get detailed system information
- `pwd://current` - Get current working directory

### Prompts

- `bash_helper` - Get comprehensive usage examples and documentation

## Configuration

You can customize the server behavior by modifying these constants in `server.py`:

```python
MAX_OUTPUT_LENGTH = 10000    # Maximum characters in output
TIMEOUT_SECONDS = 30         # Default command timeout
ALLOWED_COMMANDS = None      # List of allowed commands (None = allow all)
```

### Security Configuration

For enhanced security, set `ALLOWED_COMMANDS` to restrict available commands:

```python
ALLOWED_COMMANDS = [
    "ls", "pwd", "whoami", "date", "uptime",
    "df", "free", "ps", "top", "htop"
]
```

## Examples

### Basic Commands
```bash
# List directory contents
run_bash_command("ls -la")

# Check disk usage
run_bash_command("df -h")

# View system processes
run_bash_command("ps aux")
```

### Advanced Scripts
```bash
# System monitoring script
run_bash_script("""
#!/bin/bash
echo "=== System Monitor ==="
echo "Date: $(date)"
echo "Uptime: $(uptime)"
echo "Disk Usage:"
df -h
echo "Memory Usage:"
free -h
echo "Load Average:"
cat /proc/loadavg
""")
```

### Working Directory Management
```bash
# Execute command in specific directory
run_bash_command("pwd && ls -la", working_directory="/var/log")
```

## Security Considerations

⚠️ **Important Security Notes**:

- Commands execute with the same permissions as the server process
- Consider running in a containerized environment for production use
- Use a dedicated user account with limited permissions
- Set `ALLOWED_COMMANDS` to restrict available commands
- Monitor command execution for suspicious activity
- Be cautious with destructive commands

## Output Format

All command executions return structured output:

```
Command: ls -la
Exit Code: 0
Working Directory: /home/user

STDOUT:
total 12
drwxr-xr-x 3 user user 4096 May 24 10:30 .
drwxr-xr-x 3 user user 4096 May 24 10:29 ..
-rw-r--r-- 1 user user  220 May 24 10:29 .bash_logout

STDERR:
(none)
```

## Error Handling

The server handles various error conditions:

- **Command timeout**: Commands that exceed the timeout limit
- **Invalid working directory**: Non-existent directories
- **Permission errors**: Insufficient permissions for command execution
- **Command not found**: Invalid or non-existent commands
- **Output truncation**: Large outputs are truncated with a warning

## Development

### Testing

```bash
# Run in development mode
mcp dev server.py

# Test with MCP Inspector
mcp dev server.py --inspector
```

### Customization

Extend the server by:

1. Adding new tools for specific command categories
2. Implementing custom security validators
3. Adding logging and monitoring capabilities
4. Creating specialized script templates

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Submit a pull request

## License

MIT License - see LICENSE file for details.

## Support

For issues and questions:
- Open an issue on GitHub
- Check the MCP documentation: https://modelcontextprotocol.io
- Review the MCP specification: https://spec.modelcontextprotocol.io

---

**Disclaimer**: This tool executes system commands and should be used responsibly. Always review commands before execution and implement appropriate security measures for your environment.
