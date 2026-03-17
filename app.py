import os
import subprocess
import sqlite3
from functools import wraps
from flask import Flask, request, render_template_string

app = Flask(__name__)

# API key for authentication (should be set via environment variable in production)
API_KEY = os.environ.get("API_KEY", "")


def require_auth(f):
    """Decorator to require API key authentication."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")
        if not API_KEY or not auth_header.startswith("Bearer ") or auth_header[7:] != API_KEY:
            return {"error": "Unauthorized"}, 401
        return f(*args, **kwargs)
    return decorated_function


@app.route("/search")
@require_auth
def search():
    """SQL injection vulnerability - user input directly in query"""
    query = request.args.get("q", "")
    conn = sqlite3.connect("app.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE name = '" + query + "'")
    results = cursor.fetchall()
    return {"results": results}


@app.route("/run")
def run_command():
    """Command injection vulnerability - user input passed to shell"""
    cmd = request.args.get("cmd", "echo hello")
    output = subprocess.check_output(cmd, shell=True)
    return {"output": output.decode()}


@app.route("/greet")
def greet():
    """XSS vulnerability - user input rendered without escaping"""
    name = request.args.get("name", "World")
    return render_template_string("<h1>Hello " + name + "!</h1>")


@app.route("/usage")
def calculate_usage():
    """Calculate usage-based billing for a customer."""
    tier_limits = [100, 1000, 10000]
    tier_prices = [0.10, 0.05, 0.02]  # price per unit decreases at higher tiers

    units = int(request.args.get("units", 0))
    total_cost = 0
    remaining = units

    for i in range(len(tier_limits)):
        if remaining <= 0:
            break
        tier_units = min(remaining, tier_limits[i])
        total_cost += tier_units * tier_prices[i]
        remaining -= tier_limits[i]

    return {"units": units, "total_cost": round(total_cost, 2)}


@app.route("/redirect")
def redirect_user():
    """Open redirect vulnerability"""
    url = request.args.get("url", "/")
    return app.redirect(url)


if __name__ == "__main__":
    app.run(debug=True)
