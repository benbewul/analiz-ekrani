from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class PublishAction:
    bill_account_code: str
    action_id: int
    action_status: int
    creation_date: str


@dataclass
class InvoiceRec:
    inv_ba_id: str
    inv_number: str
    request_status: int
    inv_due_date: str
    amount: str = ""


@dataclass
class PaymentRec:
    pymnt_ba_id: str
    pymnt_inv_id: str
    note: str = "Kayit var"


@dataclass
class PendingRec:
    inv_number: str
    state: str = "Pending kaydi var"


@dataclass
class BppsBillRec:
    bill_number: str
    bill_status: int
    pay_date: str = "-"
    amount: str = "-"


@dataclass
class ActivityRec:
    moc_bar: int | None
    note: str = ""


@dataclass
class BaSnapshot:
    ba_id: str
    actions: list[PublishAction] = field(default_factory=list)
    invoices: list[InvoiceRec] = field(default_factory=list)
    payments: list[PaymentRec] = field(default_factory=list)
    pending: list[PendingRec] = field(default_factory=list)
    bpps: list[BppsBillRec] = field(default_factory=list)
    activities: list[ActivityRec] = field(default_factory=list)
