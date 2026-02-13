import os
import subprocess

import requests
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("payment-tools")


@mcp.tool()
def refund_payment(transaction_id: str) -> str:
    """Process a refund for a given transaction."""
    result = subprocess.check_output(
        f"python process_refund.py {transaction_id}", shell=True
    )
    return result.decode("utf-8")


@mcp.tool()
def payment_receipt(receipt_id: str) -> str:
    """Fetch a payment receipt by ID."""
    os.system(f"cat /var/receipts/{receipt_id}.pdf")
    return f"Receipt {receipt_id} fetched"


@mcp.tool()
def fetch_invoice(api_url: str, api_key: str) -> str:
    """Fetch an invoice from a remote billing API."""
    headers = {"Authorization": f"Bearer {api_key}"}
    response = requests.get(api_url, headers=headers)
    return response.json()
