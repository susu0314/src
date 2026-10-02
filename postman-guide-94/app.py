"""Local teaching API. Do not expose this development server to the Internet."""
import os
import secrets
import sqlite3
from functools import wraps
from pathlib import Path

from flask import Flask, g, jsonify, request
from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer
from werkzeug.exceptions import BadRequest, HTTPException

app = Flask(__name__)
# A fresh key invalidates old tokens after a server restart.
signer = URLSafeTimedSerializer(secrets.token_hex(32), salt="postman-demo")
DB_PATH = Path(os.environ.get("DEMO_DB", Path(__file__).with_name("demo.sqlite3")))
with sqlite3.connect(DB_PATH) as db:
    db.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT NOT NULL UNIQUE, email TEXT NOT NULL)")


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(_error):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def error(code, message, status):
    response = jsonify(code=code, message=message)
    response.status_code = status
    if status == 401:
        response.headers["WWW-Authenticate"] = 'Bearer realm="postman-demo"'
    return response


def read_json():
    if not request.is_json:
        return None, error("unsupported_media_type", "Use application/json", 415)
    try:
        data = request.get_json()
    except BadRequest:
        return None, error("invalid_json", "Malformed JSON", 400)
    if not isinstance(data, dict):
        return None, error("invalid_fields", "JSON body must be an object", 422)
    return data, None


def require_token(func):
    @wraps(func)
    def wrapped(*args, **kwargs):
        parts = request.headers.get("Authorization", "").split()
        if len(parts) != 2 or parts[0].lower() != "bearer":
            return error("unauthorized", "Missing Bearer token", 401)
        try:
            payload = signer.loads(parts[1], max_age=3600)
        except (BadSignature, SignatureExpired):
            return error("unauthorized", "Invalid or expired token", 401)
        if payload != {"sub": "xiaosu", "role": "developer"}:
            return error("unauthorized", "Invalid token subject", 401)
        g.identity = payload
        return func(*args, **kwargs)
    return wrapped


@app.get("/health")
def health():
    return jsonify(status="ok")


@app.post("/api/login")
def login():
    data, failure = read_json()
    if failure is not None:
        return failure
    if data.get("username") != "xiaosu" or data.get("password") != "demo-pass":
        return error("unauthorized", "Invalid demo credentials", 401)
    token = signer.dumps({"sub": "xiaosu", "role": "developer"})
    return jsonify(access_token=token, token_type="Bearer", expires_in=3600)


@app.get("/api/me")
@require_token
def me():
    return jsonify(id=1001, username=g.identity["sub"], role=g.identity["role"])


@app.get("/api/admin")
@require_token
def admin():
    return error("forbidden", "This demo account has no admin permission", 403)


def validate_user(data, partial=False):
    allowed = {"username", "email"}
    if set(data) - allowed or not data or (not partial and set(data) != allowed):
        return "Provide username and email; PATCH permits a subset"
    for key, value in data.items():
        if not isinstance(value, str) or not value.strip() or len(value) > 200:
            return f"{key} must be a nonempty string of at most 200 characters"
    if "email" in data and "@" not in data["email"]:
        return "email must contain @ (demo validation only)"
    return None


@app.route("/api/users", methods=["GET", "POST"])
@require_token
def users():
    db = get_db()
    if request.method == "GET":
        try:
            page = int(request.args.get("page", "1"))
            limit = int(request.args.get("limit", "10"))
            if page < 1 or not 1 <= limit <= 100:
                raise ValueError
        except ValueError:
            return error("invalid_query", "page >= 1; 1 <= limit <= 100", 400)
        rows = db.execute("SELECT * FROM users ORDER BY id LIMIT ? OFFSET ?", (limit, (page - 1) * limit)).fetchall()
        return jsonify(items=[dict(row) for row in rows], page=page, limit=limit)
    data, failure = read_json()
    if failure is not None:
        return failure
    message = validate_user(data)
    if message:
        return error("invalid_fields", message, 422)
    try:
        with db:
            cursor = db.execute("INSERT INTO users (username, email) VALUES (?, ?)", (data["username"], data["email"]))
    except sqlite3.IntegrityError:
        return error("username_exists", "username already exists", 409)
    response = jsonify(id=cursor.lastrowid, **data)
    response.status_code = 201
    response.headers["Location"] = f"/api/users/{cursor.lastrowid}"
    return response


@app.route("/api/users/<int:user_id>", methods=["GET", "PUT", "PATCH", "DELETE"])
@require_token
def user(user_id):
    db = get_db()
    row = db.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    if row is None:
        return error("not_found", "User does not exist", 404)
    if request.method == "GET":
        return jsonify(dict(row))
    if request.method == "DELETE":
        with db:
            db.execute("DELETE FROM users WHERE id = ?", (user_id,))
        return "", 204
    data, failure = read_json()
    if failure is not None:
        return failure
    message = validate_user(data, partial=request.method == "PATCH")
    if message:
        return error("invalid_fields", message, 422)
    updated = {**dict(row), **data}
    try:
        with db:
            db.execute("UPDATE users SET username = ?, email = ? WHERE id = ?", (updated["username"], updated["email"], user_id))
    except sqlite3.IntegrityError:
        return error("username_exists", "username already exists", 409)
    return jsonify(updated)


@app.errorhandler(HTTPException)
def http_error(exc):
    response = exc.get_response()  # Preserve headers such as Allow on 405.
    response.data = app.json.dumps({"code": "http_error", "message": exc.description})
    response.content_type = "application/json"
    return response


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=int(os.environ.get("DEMO_PORT", "8000")), debug=False)
