import requests
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("payment-tools")


@mcp.tool()
def verify_payment(gateway_url: str, secret_key: str, payment_id: str) -> str:
    """Verify a payment status with an external gateway."""
    headers = {"X-API-Key": secret_key}
    response = requests.get(f"{gateway_url}/payments/{payment_id}", headers=headers)
    return response.json()
