"""Vulnerable MCP server - shell injection via tool parameters (v2)."""

import subprocess
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("billing-tools")


@mcp.tool()
def run_report(report_name: str) -> str:
    """Generate a billing report by name."""
    # Vulnerable: tool parameter passed directly to shell command
    result = subprocess.check_output(
        f"python generate_report.py {report_name}", shell=True
    )
    return result.decode()


@mcp.tool()
def lookup_customer(customer_id: str) -> str:
    """Look up customer billing details."""
    # Vulnerable: tool parameter used in os.system
    import os

    os.system(f"grep {customer_id} /var/data/customers.csv")
    return "done"
