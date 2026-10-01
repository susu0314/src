import os

import redis
from flask import Flask, jsonify, request

app = Flask(__name__)
store = redis.Redis.from_url(
    os.getenv("REDIS_URL", "redis://redis:6379/0"),
    decode_responses=True,
    socket_connect_timeout=2,
    socket_timeout=2,
)
COUNTER_KEY = "docker-demo:counter"


@app.get("/")
def index():
    return jsonify(
        service="flask-redis-demo",
        endpoints={"health": "/health", "counter": "/counter"},
    )


@app.get("/health")
def health():
    try:
        store.ping()
    except redis.RedisError:
        return jsonify(status="unavailable", dependency="redis"), 503
    return jsonify(status="ok")


@app.route("/counter", methods=["GET", "POST"])
def counter():
    try:
        if request.method == "POST":
            value = store.incr(COUNTER_KEY)
        else:
            value = int(store.get(COUNTER_KEY) or 0)
    except redis.RedisError:
        return jsonify(error="Redis is unavailable; retry later"), 503
    return jsonify(counter=value)
