import subprocess
import sqlite3
from flask import Flask, request, render_template_string

app = Flask(__name__)


@app.route("/search")
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


@app.route("/redirect")
def redirect_user():
    """Open redirect vulnerability"""
    url = request.args.get("url", "/")
    return app.redirect(url)


if __name__ == "__main__":
    app.run(debug=True)
