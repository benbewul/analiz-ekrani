"""Runbook kurallari: mock snapshot -> UI result dict."""

from __future__ import annotations

from runbook_constants import ACTION_NAMES, ORDER_ACTION_IDS, action_status_text
from runbook_models import BaSnapshot, PublishAction


def _severity_rank(t: str) -> int:
    return {"success": 0, "info": 1, "warning": 2, "danger": 3, "neutral": 1}.get(t, 0)


def _max_severity(a: str, b: str) -> str:
    return a if _severity_rank(a) >= _severity_rank(b) else b


def _sort_desc(actions: list) -> list:
    return sorted(actions, key=lambda x: x.creation_date, reverse=True)


def _sort_asc(actions: list) -> list:
    return sorted(actions, key=lambda x: x.creation_date)


def _actions_for_template(snapshot: BaSnapshot) -> list[dict]:
    return [
        {
            "action_id": a.action_id,
            "action_name": ACTION_NAMES.get(a.action_id, str(a.action_id)),
            "action_status": a.action_status,
            "status_text": action_status_text(a.action_status),
            "date": a.creation_date,
        }
        for a in _sort_desc(snapshot.actions)
    ]


def _find_action_32(snapshot: BaSnapshot) -> PublishAction | None:
    hits = [a for a in snapshot.actions if a.action_id == 32]
    return _sort_desc(hits)[0] if hits else None


def _prev_order_before(act32: PublishAction, snapshot: BaSnapshot) -> PublishAction | None:
    asc = _sort_asc(snapshot.actions)
    try:
        idx = asc.index(act32)
    except ValueError:
        return None
    for j in range(idx - 1, -1, -1):
        if asc[j].action_id in ORDER_ACTION_IDS:
            return asc[j]
    return None


def _primary_invoice(snapshot: BaSnapshot):
    for inv in snapshot.invoices:
        if inv.request_status == 0:
            return inv
    return snapshot.invoices[0] if snapshot.invoices else None


def _bpps_for_inv(inv_number, snapshot: BaSnapshot):
    if not inv_number:
        return None
    for b in snapshot.bpps:
        if b.bill_number == inv_number:
            return b
    return None


def _payments_for_inv(inv_number, snapshot: BaSnapshot):
    if not inv_number:
        return []
    return [p for p in snapshot.payments if p.pymnt_inv_id == inv_number]


def _pending_for_inv(inv_number, snapshot: BaSnapshot):
    if not inv_number:
        return []
    return [p for p in snapshot.pending if p.inv_number == inv_number]


def _activity_moc(snapshot: BaSnapshot):
    for a in snapshot.activities:
        if a.moc_bar is not None:
            return a.moc_bar
    return None


def analyze(snapshot: BaSnapshot) -> dict:
    """Runbook adimlari: veri kontrol et, oneri uret."""
    actions_t = _actions_for_template(snapshot)
    inv = _primary_invoice(snapshot)
    inv_no = inv.inv_number if inv else None
    bpps = _bpps_for_inv(inv_no, snapshot)
    pays = _payments_for_inv(inv_no, snapshot)
    pends = _pending_for_inv(inv_no, snapshot)

    has_27 = any(a.action_id == 27 for a in snapshot.actions)
    has_payment = len(snapshot.payments) > 0

    act32 = _find_action_32(snapshot)
    prev_ord = _prev_order_before(act32, snapshot) if act32 else None
    moc_bar = _activity_moc(snapshot)

    stype = "success"
    stitle = "Aksiyon basarili, ek mudahale gerekmiyor"
    stext = "Kritik uyari bulunmadi; runbook kurallarina gore ek oneri uretilmedi."
    recs: list[str] = []

    # --- bos BA_ID ---
    if not snapshot.actions and not snapshot.invoices:
        return _empty_result()

    # --- 7.1: Out Dunning eksik ---
    if has_payment and not has_27:
        stype = _max_severity(stype, "warning")
        stitle = "Odeme sonrasi Out Dunning aksiyonu beklenirken kayit bulunamadi"
        stext = ("PCC odeme tarafinda kayit var ancak K_EAI_QUEUE_PUBLISH uzerinde "
                 "ACTION_ID=27 (Out Dunning) gorulmedi.")
        recs.append("Out Dunning akisi manuel kontrol edilmelidir (runbook 7.1).")

    # --- 7.2: MOC Unbarring ---
    if act32:
        if act32.action_status == 2:
            stype = _max_severity(stype, "success")
            stitle = "MOC Unbarring basarili"
            stext = "ACTION_ID=32 (MOC Unbarring) basarili (status=2). Ek mudahale gerekmez."
            recs.append("Aksiyon basarili, ek mudahale gerekmiyor (runbook 7.2.1).")
        elif act32.action_status == 0:
            stype = _max_severity(stype, "info")
            stitle = "MOC Unbarring beklemede, TIBCO kontrolu onerilir"
            stext = "MOC Unbarring (32) WAITING; onceki order aksiyonu degerlendirilmeli."
            if prev_ord and prev_ord.action_status in (1, 4):
                recs.append("Onceki order aksiyonu upstream (1/4) - TIBCO yonlendirmesi degerlendirilsin (runbook 7.2.2).")
            else:
                stype = _max_severity(stype, "warning")
                recs.append("Aksiyon zinciri manuel kontrol edilmelidir (runbook 7.2.2 alt senaryo).")

    # --- 7.3: Invoice 0 + BPPS bill 1 ---
    if inv and inv.request_status == 0 and bpps and bpps.bill_status == 1:
        if not pays and not pends:
            stype = _max_severity(stype, "warning")
            stitle = "BPPS'de odeme var ancak PCC'ye iletilmemis olabilir"
            stext = "REQUEST_STATUS=0 ve BPPS BILL_STATUS=1; PCC payment/pending izi yok."
            recs.append("PCC-BPPS iletim kontrolu yapilmalidir (runbook 7.3.1).")
        else:
            stype = _max_severity(stype, "warning")
            stitle = "Pending/Payment sureci kilitlenmis olabilir; BPPS retry degerlendirin"
            stext = "REQUEST_STATUS=0, BPPS BILL_STATUS=1 ve payment/pending izi var."
            recs.append("Kayitlar manuel kontrol edilmeli; BPPS retry degerlendirilmeli (runbook 7.3.2).")

    # --- 7.4: Invoice 0, BPPS yok, payment yok ---
    if inv and inv.request_status == 0 and not bpps and not pays:
        stype = _max_severity(stype, "info")
        stitle = "Fatura odenmemis gorunuyor; mevcut durum normal olabilir"
        stext = "Invoice REQUEST_STATUS=0, BPPS ve PCC payment yok."
        recs.append("Mevcut durumda aksiyon cikmamasi normal kabul edilebilir (runbook 7.4).")

    # --- 7.5: MOC BAR = 9 ---
    if moc_bar == 9:
        stype = _max_severity(stype, "warning")
        stitle = "Activity: MOC BAR = 9 - unbar ihtiyaci degerlendirin"
        stext = "MOC BAR=9; MOC Unbarring ayrica kontrol edilmeli."
        recs.append("MOC Unbarring aksiyonu kontrol edilmelidir (runbook 7.5).")

    # --- kartlar ---
    desc = _sort_desc(snapshot.actions)
    first = desc[0] if desc else None

    def _first_status():
        if not first:
            return "neutral"
        if first.action_status == 0:
            return "waiting"
        if first.action_status == 2:
            return "success"
        return "info"

    son_action = (f"{first.action_id} - {ACTION_NAMES.get(first.action_id, str(first.action_id))}"
                  if first else "Kayit yok")
    inv_card = f"request_status = {inv.request_status}" if inv else "Kayit yok"
    inv_st = "danger" if inv and inv.request_status == 0 else ("warning" if inv else "neutral")
    bpps_card = f"bill_status = {bpps.bill_status}" if bpps else "Kayit yok"
    bpps_st = "warning" if bpps and bpps.bill_status == 1 else ("neutral" if not bpps else "info")
    pay_card, pay_st = ("Kayit var", "info") if pays else ("Kayit yok", "neutral")
    pend_card, pend_st = ("Kayit var", "warning") if pends else ("Kayit yok", "neutral")
    act_note = "Kayit yok" if not snapshot.activities else f"MOC BAR = {moc_bar if moc_bar is not None else '-'}"
    act_st = "danger" if moc_bar == 9 else "neutral"

    cards = [
        {"title": "Son Action", "value": son_action, "status": _first_status()},
        {"title": "Invoice", "value": inv_card, "status": inv_st},
        {"title": "BPPS Bill", "value": bpps_card, "status": bpps_st},
        {"title": "PCC Payment", "value": pay_card, "status": pay_st},
        {"title": "PCC Pending", "value": pend_card, "status": pend_st},
        {"title": "Activity", "value": act_note, "status": act_st},
    ]

    recs = _uniq(recs)
    if not recs:
        recs = ["Runbook kurallari icin ek oneri uretilmedi.",
                "Faz 1 mudahale etmez; yalnizca okuma ve oneri uretir."]

    return {
        "summary_type": stype,
        "summary_title": stitle,
        "summary_text": stext,
        "cards": cards,
        "actions": actions_t,
        "invoice_rows": [{"inv_number": i.inv_number, "request_status": i.request_status,
                          "inv_due_date": i.inv_due_date, "amount": i.amount} for i in snapshot.invoices],
        "payment_rows": [{"pymnt_inv_id": p.pymnt_inv_id, "pymnt_ba_id": p.pymnt_ba_id,
                          "payment_state": p.note} for p in snapshot.payments],
        "pending_rows": [{"inv_number": p.inv_number, "state": p.state} for p in snapshot.pending],
        "bpps_rows": [{"bill_number": b.bill_number, "bill_status": b.bill_status,
                       "pay_date": b.pay_date, "amount": b.amount} for b in snapshot.bpps],
        "activity_rows": [{"moc_bar": a.moc_bar, "note": a.note} for a in snapshot.activities],
        "recommendations": recs,
    }


def _uniq(seq: list[str]) -> list[str]:
    out, seen = [], set()
    for x in seq:
        if x not in seen:
            seen.add(x)
            out.append(x)
    return out


def _empty_result() -> dict:
    neutral = {"title": "", "value": "Kayit yok", "status": "neutral"}
    return {
        "summary_type": "info",
        "summary_title": "Kayit bulunamadi",
        "summary_text": "Bu BA_ID icin mock veri yok. Ornek: 6092902934, 6070166156, 6111111111, 6222222222, 6333333333, 6444444444, 6555555555",
        "cards": [{**neutral, "title": t} for t in
                  ["Son Action", "Invoice", "BPPS Bill", "PCC Payment", "PCC Pending", "Activity"]],
        "actions": [],
        "invoice_rows": [],
        "payment_rows": [],
        "pending_rows": [],
        "bpps_rows": [],
        "activity_rows": [],
        "recommendations": ["Mock veritabaninda bu BA_ID icin senaryo tanimlanmamis.",
                            "Faz 1 mudahale etmez; yalnizca okuma ve oneri uretir."],
    }
