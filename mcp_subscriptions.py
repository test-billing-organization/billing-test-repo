import requests
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("subscription-tools")


@mcp.tool()
def check_subscription(api_url: str, auth_token: str, customer_id: str) -> str:
    """Check subscription status for a customer."""
    headers = {"Authorization": f"Bearer {auth_token}"}
    response = requests.get(f"{api_url}/subscriptions/{customer_id}", headers=headers)
    return response.json()
