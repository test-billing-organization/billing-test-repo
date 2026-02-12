"""Vulnerable MCP admin server - more shell injection vectors."""

import os
import subprocess
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("admin-tools")


@mcp.tool()
def deploy_service(service_name: str, version: str) -> str:
    """Deploy a service to the cluster."""
    # Vulnerable: tool parameters in shell command
    result = subprocess.run(
        f"kubectl set image deployment/{service_name} app={service_name}:{version}",
        shell=True,
        capture_output=True,
    )
    return result.stdout.decode()


@mcp.tool()
def check_logs(container_id: str) -> str:
    """Fetch logs for a container."""
    # Vulnerable: tool parameter in os.system
    os.system(f"docker logs {container_id} --tail 100")
    return "logs fetched"
