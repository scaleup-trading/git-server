# Installation Guide

This guide provides detailed steps to set up the Multi-Repository Git MCP Server for use with Claude Desktop.

## Prerequisites
- **Python**: Version 3.11 or higher
- **Docker**: Latest version with Docker Compose (optional for non-Docker setup)
- **Git**: Installed on your system
- **Claude Desktop**: Configured and running
- **Project Directory**: A directory containing one or more Git repositories (e.g., `/Users/john/Projects`)

## Setup Instructions

### 1. Clone the Repository
Clone or download the project to your local machine:
```bash
git clone https://github.com/your-username/git-mcp-server.git
cd git-mcp-server
```

### 2. Install Dependencies
Install Python dependencies listed in `requirements.txt`:
```bash
pip install -r requirements.txt
```

Alternatively, use the provided `setup.sh` script to automate dependency installation:
```bash
./scripts/setup.sh /path/to/your/projects
```

This script:
- Checks for Python and Git
- Installs dependencies
- Configures the base repository directory

### 3. Configure Docker (Optional)
If using Docker, build the image:
```bash
./scripts/build.sh
```

Run the container, mounting your repositories and state directories:
```bash
./scripts/run_docker_mcp.sh /path/to/your/projects
```
This mounts `/path/to/your/projects` as `/repos` and `/app/state` for persistent state.

### 4. Restart Claude Desktop
Ensure Claude Desktop is running and configured to connect to the MCP server. Restart it after setup to detect the server.

## Verifying Setup
Run the test script to verify the setup:
```bash
./scripts/test_mcp.sh /path/to/your/projects
```
This checks:
- Repository discovery
- File tracking
- Workspace creation
- Server connectivity

## Troubleshooting
- **Docker Issues**: Ensure Docker is running and you have permissions for `/repos` and `/app/state`.
- **Dependency Errors**: Verify Python 3.11 and `pip` are installed.
- **Claude Connection**: Check the server logs in `/app/state` for connection issues.

For further details, see [usage.md](usage.md) for workflows or contact [Your Contact Information] for support.