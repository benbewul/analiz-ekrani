import os

from flask import Flask, render_template, request

app = Flask(__name__)

ACTION_MAP = {
    6: "Auto MOC Barring",
    22: "Suspension",
    25: "Cancellation",
    27: "Out Dunning",
    32: "MOC Unbarring",
}

MOCK_CASES = {
    "6092902934": {
        "summary_type": "warning",
        "summary_title": "BPPS retry değerlendirmesi önerilir",
        "summary_text": "Fatura PCC tarafında request_status=0 görünüyor. BPPS bill_status=1 ve pending/payment izi bulunduğu için kayıtlar takılmış olabilir. Müdahale yapılmadan önce manuel kontrol önerilir.",
        "cards": [
            {"title": "Son Action", "value": "32 - MOC Unbarring", "status": "waiting"},
            {"title": "Invoice", "value": "request_status = 0", "status": "danger"},
            {"title": "BPPS Bill", "value": "bill_status = 1", "status": "warning"},
            {"title": "Öneri", "value": "Retry kontrolü", "status": "warning"},
        ],
        "actions": [
            {"action_id": 32, "action_name": "MOC Unbarring", "action_status": 0, "status_text": "WAITING", "date": "2026-03-29 15:07"},
            {"action_id": 6, "action_name": "Auto MOC Barring", "action_status": 2, "status_text": "SUCCESS", "date": "2026-03-29 14:50"},
            {"action_id": 27, "action_name": "Out Dunning", "action_status": 2, "status_text": "SUCCESS", "date": "2026-03-28 08:25"},
        ],
        "invoice_rows": [
            {"inv_number": "FD41050E42E39D", "request_status": 0, "inv_due_date": "15.11.2024", "amount": "1313.70 TL"},
        ],
        "payment_rows": [
            {"pymnt_inv_id": "FD41050E42E39D", "pymnt_ba_id": "6092902934", "payment_state": "İz bulundu"},
        ],
        "pending_rows": [
            {"inv_number": "FD41050E42E39D", "state": "Pending kaydı var"},
        ],
        "bpps_rows": [
            {"bill_number": "FD41050E42E39D", "bill_status": 1, "pay_date": "28.03.2026", "amount": "1313.70"},
        ],
        "recommendations": [
            "Önce pending/payment izi manuel kontrol edilmeli.",
            "BPPS retry ihtiyacı değerlendirilmeli.",
            "Şimdilik uygulama yalnızca öneri üretir; müdahale yapmaz.",
        ],
    },
    "6070166156": {
        "summary_type": "info",
        "summary_title": "TIBCO yönlendirmesi önerilir",
        "summary_text": "MOC Unbarring (32) aksiyonu status=0 bekliyor. Önceki order aksiyonu 6 ve upstream statü geçmişi bulunduğu için bu durum TIBCO kontrolü gerektiriyor olabilir.",
        "cards": [
            {"title": "Son Action", "value": "32 - MOC Unbarring", "status": "waiting"},
            {"title": "Önceki Order", "value": "6 - Auto MOC Barring", "status": "info"},
            {"title": "Invoice", "value": "request_status = 0", "status": "danger"},
            {"title": "Öneri", "value": "TIBCO kontrolü", "status": "info"},
        ],
        "actions": [
            {"action_id": 32, "action_name": "MOC Unbarring", "action_status": 0, "status_text": "WAITING", "date": "2026-03-29 15:07"},
            {"action_id": 6, "action_name": "Auto MOC Barring", "action_status": 1, "status_text": "UPSTREAM", "date": "2026-03-29 14:45"},
            {"action_id": 22, "action_name": "Suspension", "action_status": 2, "status_text": "SUCCESS", "date": "2026-03-28 17:10"},
        ],
        "invoice_rows": [
            {"inv_number": "FD40950E2ADD45", "request_status": 0, "inv_due_date": "15.10.2024", "amount": "875.50 TL"},
        ],
        "payment_rows": [],
        "pending_rows": [],
        "bpps_rows": [],
        "recommendations": [
            "MOC Unbarring bekleme sebebi önceki order aksiyonu ile birlikte değerlendirilmeli.",
            "Case TIBCO ekibine yönlendirilmeye uygun olabilir.",
            "Bu demo yalnızca karar destek amaçlıdır.",
        ],
    },
}

DEFAULT_CASE = {
    "summary_type": "success",
    "summary_title": "Demo sonuç üretildi",
    "summary_text": "Bu BA_ID için hazır mock kayıt bulunamadı. Yine de arayüz akışını görmek için örnek bir sonuç gösteriliyor.",
    "cards": [
        {"title": "Son Action", "value": "27 - Out Dunning", "status": "success"},
        {"title": "Invoice", "value": "request_status = 4", "status": "warning"},
        {"title": "BPPS Bill", "value": "Kayıt yok", "status": "neutral"},
        {"title": "Öneri", "value": "Manuel kontrol", "status": "warning"},
    ],
    "actions": [
        {"action_id": 27, "action_name": "Out Dunning", "action_status": 2, "status_text": "SUCCESS", "date": "2026-03-29 10:15"},
    ],
    "invoice_rows": [
        {"inv_number": "DEMO-INVOICE-001", "request_status": 4, "inv_due_date": "02.04.2026", "amount": "520.00 TL"},
    ],
    "payment_rows": [],
    "pending_rows": [],
    "bpps_rows": [],
    "recommendations": [
        "Gerçek DB bağlantısı eklenince bu alan dinamik çalışacak.",
        "Şu an amaç ekran akışını göstermek.",
    ],
}

@app.route("/", methods=["GET", "POST"])
def dashboard():
    ba_id = ""
    result = None
    if request.method == "POST":
        ba_id = request.form.get("ba_id", "").strip()
        result = MOCK_CASES.get(ba_id, DEFAULT_CASE)
    return render_template("index.html", ba_id=ba_id, result=result)


if __name__ == "__main__":
    debug = os.environ.get("FLASK_DEBUG", "1").lower() in ("1", "true", "yes")
    port = int(os.environ.get("PORT", "5000"))
    app.run(host="0.0.0.0", port=port, debug=debug)
