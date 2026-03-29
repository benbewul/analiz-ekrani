from __future__ import annotations

from runbook_models import (
    ActivityRec,
    BaSnapshot,
    BppsBillRec,
    InvoiceRec,
    PaymentRec,
    PendingRec,
    PublishAction,
)


def _snap(data: BaSnapshot) -> BaSnapshot:
    return data


MOCK_DB: dict[str, BaSnapshot] = {
    "6092902934": _snap(
        BaSnapshot(
            ba_id="6092902934",
            actions=[
                PublishAction("6092902934", 32, 0, "2026-03-29 15:07"),
                PublishAction("6092902934", 6, 2, "2026-03-29 14:50"),
                PublishAction("6092902934", 27, 2, "2026-03-28 08:25"),
            ],
            invoices=[
                InvoiceRec(
                    "6092902934",
                    "FD41050E42E39D",
                    0,
                    "15.11.2024",
                    "1313.70 TL",
                )
            ],
            payments=[
                PaymentRec("6092902934", "FD41050E42E39D", "Iz bulundu"),
            ],
            pending=[
                PendingRec("FD41050E42E39D", "Pending kaydi var"),
            ],
            bpps=[
                BppsBillRec("FD41050E42E39D", 1, "28.03.2026", "1313.70"),
            ],
            activities=[],
        )
    ),
    "6070166156": _snap(
        BaSnapshot(
            ba_id="6070166156",
            actions=[
                PublishAction("6070166156", 32, 0, "2026-03-29 15:07"),
                PublishAction("6070166156", 6, 1, "2026-03-29 14:45"),
                PublishAction("6070166156", 22, 2, "2026-03-28 17:10"),
            ],
            invoices=[
                InvoiceRec(
                    "6070166156",
                    "FD40950E2ADD45",
                    0,
                    "15.10.2024",
                    "875.50 TL",
                )
            ],
            payments=[],
            pending=[],
            bpps=[],
            activities=[],
        )
    ),
    "6111111111": _snap(
        BaSnapshot(
            ba_id="6111111111",
            actions=[
                PublishAction("6111111111", 32, 2, "2026-03-29 12:00"),
                PublishAction("6111111111", 6, 2, "2026-03-29 11:00"),
            ],
            invoices=[
                InvoiceRec("6111111111", "INV-PAY-NO-27", 0, "01.01.2026", "100 TL"),
            ],
            payments=[
                PaymentRec("6111111111", "INV-PAY-NO-27", "PCC odeme kaydi"),
            ],
            pending=[],
            bpps=[],
            activities=[],
        )
    ),
    "6222222222": _snap(
        BaSnapshot(
            ba_id="6222222222",
            actions=[
                PublishAction("6222222222", 27, 2, "2026-03-20 10:00"),
            ],
            invoices=[
                InvoiceRec("6222222222", "INV-BPPS-ONLY", 0, "01.02.2026", "250 TL"),
            ],
            payments=[],
            pending=[],
            bpps=[BppsBillRec("INV-BPPS-ONLY", 1, "15.03.2026", "250")],
            activities=[],
        )
    ),
    "6333333333": _snap(
        BaSnapshot(
            ba_id="6333333333",
            actions=[
                PublishAction("6333333333", 27, 2, "2026-03-10 09:00"),
            ],
            invoices=[
                InvoiceRec("6333333333", "INV-OPEN", 0, "01.03.2026", "400 TL"),
            ],
            payments=[],
            pending=[],
            bpps=[],
            activities=[],
        )
    ),
    "6444444444": _snap(
        BaSnapshot(
            ba_id="6444444444",
            actions=[
                PublishAction("6444444444", 32, 0, "2026-03-29 16:00"),
            ],
            invoices=[
                InvoiceRec("6444444444", "INV-ACT", 0, "10.03.2026", "300 TL"),
            ],
            payments=[],
            pending=[],
            bpps=[],
            activities=[ActivityRec(9, "MOC BAR = 9")],
        )
    ),
    "6555555555": _snap(
        BaSnapshot(
            ba_id="6555555555",
            actions=[
                PublishAction("6555555555", 32, 2, "2026-03-29 18:00"),
            ],
            invoices=[
                InvoiceRec("6555555555", "INV-OK", 4, "01.01.2025", "0 TL"),
            ],
            payments=[],
            pending=[],
            bpps=[],
            activities=[],
        )
    ),
}


def get_snapshot(ba_id: str) -> BaSnapshot:
    return MOCK_DB.get(ba_id) or BaSnapshot(ba_id=ba_id)
