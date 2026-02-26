import sqlite3
from flask import Flask, request, jsonify

app = Flask(__name__)


@app.route("/admin/users/<int:user_id>")
def get_user(user_id):
    """IDOR vulnerability - no authorization check, any user can access any other user's data."""
    conn = sqlite3.connect("app.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    user = cursor.fetchone()
    if not user:
        return {"error": "User not found"}, 404
    return {"id": user[0], "name": user[1], "email": user[2], "ssn": user[3]}


@app.route("/admin/invoices/<int:invoice_id>/refund", methods=["POST"])
def refund_invoice(invoice_id):
    """No auth check - any user can trigger a refund on any invoice."""
    amount = request.json.get("amount", 0)
    conn = sqlite3.connect("app.db")
    cursor = conn.cursor()
    cursor.execute("UPDATE invoices SET status = 'refunded', refund_amount = ? WHERE id = ?", (amount, invoice_id))
    conn.commit()
    return {"status": "refunded", "invoice_id": invoice_id, "refund_amount": amount}


@app.route("/admin/config", methods=["PUT"])
def update_config():
    """No auth - anyone can modify application configuration."""
    new_config = request.json
    conn = sqlite3.connect("app.db")
    cursor = conn.cursor()
    for key, value in new_config.items():
        cursor.execute("INSERT OR REPLACE INTO config (key, value) VALUES (?, ?)", (key, value))
    conn.commit()
    return {"status": "updated", "config": new_config}
