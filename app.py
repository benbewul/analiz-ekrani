import os

from flask import Flask, jsonify, render_template, request

from analyzer import analyze
from mock_provider import get_snapshot

app = Flask(__name__)


@app.get("/health")
def health():
    return jsonify({"status": "ok"})


@app.route("/", methods=["GET", "POST"])
def dashboard():
    ba_id = ""
    result = None
    if request.method == "POST":
        ba_id = request.form.get("ba_id", "").strip()
        snapshot = get_snapshot(ba_id)
        result = analyze(snapshot)
    return render_template("index.html", ba_id=ba_id, result=result)


if __name__ == "__main__":
    debug = os.environ.get("FLASK_DEBUG", "1").lower() in ("1", "true", "yes")
    port = int(os.environ.get("PORT", "5000"))
    app.run(host="0.0.0.0", port=port, debug=debug)
