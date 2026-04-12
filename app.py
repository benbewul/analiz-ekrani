import os

from flask import Flask, jsonify, render_template, request, redirect, url_for

from analyzer import analyze
from mock_provider import get_snapshot, MOCK_DB
from runbook_constants import ACTION_NAMES, action_status_text

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
    elif request.args.get("ba_id"):
        ba_id = request.args["ba_id"].strip()
        snapshot = get_snapshot(ba_id)
        result = analyze(snapshot)

    return render_template("index.html", ba_id=ba_id, result=result,
                           active_page="dashboard")


@app.route("/ba-overview")
def ba_overview():
    accounts = []
    severity_counts = {"danger": 0, "warning": 0, "success": 0}

    for ba_id, snap in MOCK_DB.items():
        last_action = "-"
        status_text = "Normal"
        severity = "success"
        total_debt = "-"

        if snap.actions:
            a = snap.actions[0]
            last_action = ACTION_NAMES.get(a.action_id, f"Action {a.action_id}")
            st = action_status_text(a.action_status)
            if st == "WAITING":
                severity = "warning"
                status_text = "Bekliyor"
            elif a.action_id in (25,) and st == "SUCCESS":
                severity = "danger"
                status_text = "Iptal"
            elif a.action_id == 22 and st == "SUCCESS":
                severity = "danger"
                status_text = "Askida"
            else:
                status_text = st

        if snap.invoices:
            total_debt = snap.invoices[0].amount or "-"

        severity_counts[severity] = severity_counts.get(severity, 0) + 1

        accounts.append({
            "ba_id": ba_id,
            "last_action": last_action,
            "status_text": status_text,
            "severity": severity,
            "total_debt": total_debt,
        })

    stats = {
        **severity_counts,
        "total": len(accounts),
    }

    return render_template("ba_overview.html", accounts=accounts, stats=stats,
                           active_page="ba-overview")


@app.route("/aksiyonlar")
def aksiyonlar():
    return render_template("aksiyonlar.html", active_page="aksiyonlar")


@app.route("/oneriler")
def oneriler():
    return render_template("oneriler.html", active_page="oneriler")


if __name__ == "__main__":
    debug = os.environ.get("FLASK_DEBUG", "1").lower() in ("1", "true", "yes")
    port = int(os.environ.get("PORT", "5000"))
    app.run(host="0.0.0.0", port=port, debug=debug)
