#!/usr/bin/env python3
"""
MCP Server for executing bash commands on Linux host.
Provides tools to run shell commands and return their output.
"""

import asyncio
import subprocess
import shlex
import os
from typing import Optional
from mcp.server.fastmcp import FastMCP

# Create the MCP server
mcp = FastMCP("Bash Command Server")

# Configuration
MAX_OUTPUT_LENGTH = 10000  # Maximum characters in command output
TIMEOUT_SECONDS = 30       # Command timeout in seconds
ALLOWED_COMMANDS = None    # Set to list of allowed commands for security, None = allow all


@mcp.tool()
async def run_bash_command(
    command: str,
    working_directory: Optional[str] = None,
    timeout: Optional[int] = None
) -> str:
    """
    Execute a bash command on the Linux host system.
    
    Args:
        command: The bash command to execute
        working_directory: Optional working directory to execute the command in
        timeout: Optional timeout in seconds (default: 30)
    
    Returns:
        String containing the command output, exit code, and any errors
    """
    
    # Security check - if allowed commands are specified, enforce them
    if ALLOWED_COMMANDS is not None:
        command_parts = shlex.split(command)
        if not command_parts or command_parts[0] not in ALLOWED_COMMANDS:
            return f"Error: Command '{command_parts[0] if command_parts else command}' is not allowed"
    
    # Set working directory
    cwd = working_directory if working_directory else os.getcwd()
    if working_directory and not os.path.exists(working_directory):
        return f"Error: Working directory '{working_directory}' does not exist"
    
    # Set timeout
    cmd_timeout = timeout if timeout is not None else TIMEOUT_SECONDS
    
    try:
        # Execute the command
        process = await asyncio.create_subprocess_shell(
            command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=cwd
        )
        
        # Wait for completion with timeout
        stdout, stderr = await asyncio.wait_for(
            process.communicate(),
            timeout=cmd_timeout
        )
        
        # Decode output
        stdout_text = stdout.decode('utf-8', errors='replace')
        stderr_text = stderr.decode('utf-8', errors='replace')
        
        # Truncate output if too long
        if len(stdout_text) > MAX_OUTPUT_LENGTH:
            stdout_text = stdout_text[:MAX_OUTPUT_LENGTH] + "\n... (output truncated)"
        if len(stderr_text) > MAX_OUTPUT_LENGTH:
            stderr_text = stderr_text[:MAX_OUTPUT_LENGTH] + "\n... (output truncated)"
        
        # Format response
        result = f"Command: {command}\n"
        result += f"Exit Code: {process.returncode}\n"
        result += f"Working Directory: {cwd}\n\n"
        
        if stdout_text:
            result += f"STDOUT:\n{stdout_text}\n"
        
        if stderr_text:
            result += f"STDERR:\n{stderr_text}\n"
        
        if not stdout_text and not stderr_text:
            result += "No output produced.\n"
            
        return result
        
    except asyncio.TimeoutError:
        return f"Error: Command '{command}' timed out after {cmd_timeout} seconds"
    
    except Exception as e:
        return f"Error executing command '{command}': {str(e)}"


@mcp.tool()
async def run_bash_script(
    script_content: str,
    working_directory: Optional[str] = None,
    timeout: Optional[int] = None
) -> str:
    """
    Execute a bash script from string content.
    
    Args:
        script_content: The bash script content to execute
        working_directory: Optional working directory to execute the script in
        timeout: Optional timeout in seconds (default: 30)
    
    Returns:
        String containing the script output, exit code, and any errors
    """
    
    # Set working directory
    cwd = working_directory if working_directory else os.getcwd()
    if working_directory and not os.path.exists(working_directory):
        return f"Error: Working directory '{working_directory}' does not exist"
    
    # Set timeout
    cmd_timeout = timeout if timeout is not None else TIMEOUT_SECONDS
    
    try:
        # Execute the script
        process = await asyncio.create_subprocess_exec(
            'bash', '-c', script_content,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=cwd
        )
        
        # Wait for completion with timeout
        stdout, stderr = await asyncio.wait_for(
            process.communicate(),
            timeout=cmd_timeout
        )
        
        # Decode output
        stdout_text = stdout.decode('utf-8', errors='replace')
        stderr_text = stderr.decode('utf-8', errors='replace')
        
        # Truncate output if too long
        if len(stdout_text) > MAX_OUTPUT_LENGTH:
            stdout_text = stdout_text[:MAX_OUTPUT_LENGTH] + "\n... (output truncated)"
        if len(stderr_text) > MAX_OUTPUT_LENGTH:
            stderr_text = stderr_text[:MAX_OUTPUT_LENGTH] + "\n... (output truncated)"
        
        # Format response
        result = f"Script Content:\n{script_content[:200]}{'...' if len(script_content) > 200 else ''}\n\n"
        result += f"Exit Code: {process.returncode}\n"
        result += f"Working Directory: {cwd}\n\n"
        
        if stdout_text:
            result += f"STDOUT:\n{stdout_text}\n"
        
        if stderr_text:
            result += f"STDERR:\n{stderr_text}\n"
        
        if not stdout_text and not stderr_text:
            result += "No output produced.\n"
            
        return result
        
    except asyncio.TimeoutError:
        return f"Error: Script timed out after {cmd_timeout} seconds"
    
    except Exception as e:
        return f"Error executing script: {str(e)}"


@mcp.resource("system://info")
def get_system_info() -> str:
    """Get basic system information"""
    try:
        import platform
        info = []
        info.append(f"System: {platform.system()}")
        info.append(f"Node: {platform.node()}")
        info.append(f"Release: {platform.release()}")
        info.append(f"Version: {platform.version()}")
        info.append(f"Machine: {platform.machine()}")
        info.append(f"Processor: {platform.processor()}")
        info.append(f"Python Version: {platform.python_version()}")
        return "\n".join(info)
    except Exception as e:
        return f"Error getting system info: {str(e)}"


@mcp.resource("pwd://current")
def get_current_directory() -> str:
    """Get the current working directory"""
    return f"Current working directory: {os.getcwd()}"


@mcp.prompt()
def bash_helper() -> str:
    """Get help and examples for using the bash command tools"""
    return """
This MCP server provides tools to execute bash commands on the Linux host system.

Available tools:
1. run_bash_command - Execute a single bash command
2. run_bash_script - Execute a bash script from string content

Available resources:
1. system://info - Get system information
2. pwd://current - Get current working directory

Examples:
- List files: run_bash_command("ls -la")
- Check disk usage: run_bash_command("df -h")
- Run in specific directory: run_bash_command("pwd", working_directory="/tmp")
- Multi-line script: run_bash_script("#!/bin/bash\necho 'Hello'\ndate\nuptime")

Security notes:
- Commands run with the permissions of the server process
- Output is truncated at 10,000 characters
- Commands timeout after 30 seconds by default
- Be careful with destructive commands
"""


if __name__ == "__main__":
    # Run the server
    mcp.run()
