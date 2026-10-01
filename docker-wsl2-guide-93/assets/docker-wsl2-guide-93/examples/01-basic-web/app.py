from flask import Flask, jsonify

app = Flask(__name__)


@app.get("/")
def index():
    return jsonify(message="Hello from a Linux container", project="docker-demo")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=False)
