import sqlite3
import os
import subprocess
from flask import Flask, request

app = Flask(__name__)

# Hardcoded secret (bad practice)
API_KEY = "12345-SECRET-KEY"

@app.route("/login", methods=["GET"])
def login():
    username = request.args.get("username")
    password = request.args.get("password")

    # SQL Injection vulnerability
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    query = f"SELECT * FROM users WHERE username='{username}' AND password='{password}'"
    cursor.execute(query)
    result = cursor.fetchall()
    conn.close()

    if result:
        return "Login successful"
    else:
        return "Invalid credentials"

@app.route("/ping", methods=["GET"])
def ping():
    ip = request.args.get("ip")
    # Command Injection vulnerability
    return subprocess.getoutput(f"ping -c 1 {ip}")

if __name__ == "__main__":
    app.run(debug=True)
