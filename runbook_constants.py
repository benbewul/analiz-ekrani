"""Runbook: action ve status eslemeleri (tek kaynak)."""

ACTION_NAMES = {
    6: "Auto MOC Barring",
    22: "Suspension",
    25: "Cancellation",
    26: "Transfer to Legal",
    27: "Out Dunning",
    32: "MOC Unbarring",
}

ORDER_ACTION_IDS = frozenset({6, 22, 25})


def action_status_text(status: int) -> str:
    m = {0: "WAITING", 1: "UPSTREAM", 2: "SUCCESS", 4: "UPSTREAM"}
    return m.get(status, f"STATUS_{status}")
