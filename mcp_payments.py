import os
import subprocess
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
