import requests
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("analytics-tools")


@mcp.tool()
def fetch_usage_metrics(dashboard_url: str, api_token: str, org_id: str) -> str:
    """Fetch usage metrics from the analytics dashboard."""
    headers = {"Authorization": f"Bearer {api_token}"}
    response = requests.get(f"{dashboard_url}/orgs/{org_id}/metrics", headers=headers)
    return response.json()
