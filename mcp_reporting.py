import requests
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("reporting-tools")


@mcp.tool()
def fetch_billing_summary(report_endpoint: str, access_token: str, account_id: str) -> str:
    """Fetch a billing summary report from the reporting service."""
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(f"{report_endpoint}/accounts/{account_id}/summary", headers=headers)
    return response.json()
