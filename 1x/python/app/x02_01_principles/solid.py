"""Part A — SOLID (Java + Python). Each principle: Violation, then Fix, then a `<name>_demo()`.

- Running domain: orders -> payments -> notifications.
- Interfaces use typing.Protocol (structural) or abc.ABC (nominal); models are dataclasses.
- The "catch" for each principle is in its demo comment and in docs/02.01.core-principles.md.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import MutableSequence
from dataclasses import dataclass, field
from decimal import ROUND_HALF_UP, Decimal
from typing import Protocol, runtime_checkable

CENT = Decimal("0.01")


# ===== 1.1 SRP — one module answers to one actor =====


@dataclass(frozen=True)
class SrpOrder:
    id: str
    customer_email: str
    subtotal: Decimal


class SrpViolationOrderService:
    """God service: finance (tax), ops (storage) and marketing (email copy) all edit this class."""

    def __init__(self) -> None:
        self._table: dict[str, Decimal] = {}
        self._outbox: list[str] = []

    def place(self, order: SrpOrder) -> str:
        total = (order.subtotal * Decimal("1.08")).quantize(CENT, ROUND_HALF_UP)  # finance rule
        self._table[order.id] = total  # ops concern
        self._outbox.append(f"Hi! Your order {order.id} costs {total}")  # marketing copy
        return f"placed {order.id} total={total} mails={len(self._outbox)}"


@dataclass
class SrpPriceCalculator:
    """Finance owns this: tax and rounding change here only."""

    tax_rate: Decimal

    def total(self, order: SrpOrder) -> Decimal:
        return (order.subtotal * (1 + self.tax_rate)).quantize(CENT, ROUND_HALF_UP)


@dataclass
class SrpOrderRepository:
    """Ops owns this: storage changes here only."""

    rows: dict[str, Decimal] = field(default_factory=dict)

    def save(self, order_id: str, total: Decimal) -> None:
        self.rows[order_id] = total


@dataclass
class SrpOrderNotifier:
    """Marketing owns this: wording and channel change here only."""

    outbox: list[str] = field(default_factory=list)

    def confirmed(self, order: SrpOrder, total: Decimal) -> None:
        self.outbox.append(f"Order {order.id} confirmed: {total}")


@dataclass
class SrpOrderService:
    """Coordinator with no rules of its own."""

    prices: SrpPriceCalculator
    repo: SrpOrderRepository
    notifier: SrpOrderNotifier

    def place(self, order: SrpOrder) -> str:
        total = self.prices.total(order)
        self.repo.save(order.id, total)
        self.notifier.confirmed(order, total)
        return f"placed {order.id} total={total} stored={len(self.repo.rows)} mails={len(self.notifier.outbox)}"


def srp_demo() -> str:
    # Shows identical output; only the change cost differs (tax change edits SrpPriceCalculator only).
    # Use when different actors change the same class.
    # Catch: split by actor, not by method; dozens of one-method classes is the opposite failure.
    order = SrpOrder("o-1", "a@example.com", Decimal("100.00"))
    good = SrpOrderService(SrpPriceCalculator(Decimal("0.08")), SrpOrderRepository(), SrpOrderNotifier())
    return f"SRP violation: {SrpViolationOrderService().place(order)}\nSRP fix:       {good.place(order)}"


# ===== 1.2 OCP — add behavior by adding code =====


class OcpViolationProcessor:
    """Every new payment method edits and retests this if-chain."""

    def pay(self, method: str, amount: Decimal) -> str:
        if method == "CARD":
            return f"card charged {amount}"
        if method == "PAYPAL":
            return f"paypal charged {amount}"
        raise ValueError(f"unsupported method {method}")


class PaymentMethod(Protocol):
    name: str

    def charge(self, amount: Decimal) -> str: ...


@dataclass(frozen=True)
class Card:
    name: str = "CARD"

    def charge(self, amount: Decimal) -> str:
        return f"card charged {amount}"


@dataclass(frozen=True)
class PayPal:
    name: str = "PAYPAL"

    def charge(self, amount: Decimal) -> str:
        return f"paypal charged {amount}"


@dataclass(frozen=True)
class ApplePay:
    """Added later with zero edits to the processor."""

    name: str = "APPLE_PAY"

    def charge(self, amount: Decimal) -> str:
        return f"apple pay charged {amount}"


class OcpPaymentProcessor:
    """Registry replaces the if-chain; duplicate names fail fast at construction."""

    def __init__(self, methods: list[PaymentMethod]) -> None:
        self._methods: dict[str, PaymentMethod] = {}
        for m in methods:
            if m.name in self._methods:
                raise ValueError(f"duplicate payment method {m.name}")
            self._methods[m.name] = m

    def pay(self, method: str, amount: Decimal) -> str:
        if method not in self._methods:
            raise ValueError(f"unsupported method {method}; known={sorted(self._methods)}")
        return self._methods[method].charge(amount)


def ocp_demo() -> str:
    # Shows ApplePay added without touching the processor.
    # Use when variants arrive over time and are independent.
    # Catch: you only close against variation you have seen; speculative interfaces are YAGNI debt.
    good = OcpPaymentProcessor([Card(), PayPal(), ApplePay()])
    return (
        f"OCP violation: {OcpViolationProcessor().pay('CARD', Decimal('10'))}\n"
        f"OCP fix:       {good.pay('APPLE_PAY', Decimal('10'))}"
    )


# ===== 1.3 LSP — subtypes keep the base promises =====


class LspViolationPayment:
    """Base promise: refund() returns a refund id."""

    def __init__(self, amount: Decimal) -> None:
        self.amount = amount

    def refund(self) -> str:
        return f"refund-{self.amount}"


class LspViolationGiftCard(LspViolationPayment):
    """Breaks the promise; callers written for LspViolationPayment crash."""

    def refund(self) -> str:
        raise NotImplementedError("gift cards are not refundable")


def lsp_violation_refund_all(payments: list[LspViolationPayment]) -> list[str]:
    """The smell: callers need isinstance checks to survive the subtype."""
    return ["skipped gift card" if isinstance(p, LspViolationGiftCard) else p.refund() for p in payments]


class Refundable(ABC):
    """Capability: only types that can honor refund() implement it."""

    amount: Decimal

    @abstractmethod
    def refund(self) -> str: ...


@dataclass(frozen=True)
class CardPayment(Refundable):
    amount: Decimal

    def refund(self) -> str:
        return f"refund-card-{self.amount}"


@dataclass(frozen=True)
class GiftCardPayment:
    """Not Refundable, so it can't be passed where a refund is expected."""

    amount: Decimal


def contract_holds(r: Refundable) -> bool:
    """Mini contract test: run the same behavioral checks against every implementation."""
    rid = r.refund()
    return rid.startswith("refund-") and rid.endswith(str(r.amount))


def lsp_demo() -> str:
    # Shows isinstance smell vs a capability split; stdlib does the same with Sequence vs MutableSequence.
    # Use when a subtype "can't" do something the base promises.
    # Catch: type checkers check signatures, not behavior; contract tests catch the rest.
    ten = Decimal("10")
    bad = lsp_violation_refund_all([LspViolationPayment(ten), LspViolationGiftCard(ten)])
    card = CardPayment(ten)
    return (
        f"LSP violation: {bad}\n"
        f"LSP fix:       {card.refund()} contract_holds={contract_holds(card)} "
        f"gift_card_refundable={isinstance(GiftCardPayment(ten), Refundable)}\n"
        f"stdlib split:  tuple is MutableSequence={isinstance((1, 2), MutableSequence)}"
    )


# ===== 1.4 ISP — clients depend only on what they use =====


@dataclass(frozen=True)
class IspOrder:
    id: str
    status: str


class IspViolationOrderStore(ABC):
    """Fat interface: the read-only report must implement or fake every method."""

    @abstractmethod
    def find_all(self) -> list[IspOrder]: ...

    @abstractmethod
    def save(self, order: IspOrder) -> None: ...

    @abstractmethod
    def purge_older_than_days(self, days: int) -> int: ...

    @abstractmethod
    def export_csv(self) -> str: ...


@runtime_checkable
class OrderReader(Protocol):
    """Declared by the consumer; any object with find_all() fits, without inheriting."""

    def find_all(self) -> list[IspOrder]: ...


class OrderWriter(Protocol):
    def save(self, order: IspOrder) -> None: ...


@dataclass
class InMemoryOrderStore:
    """Implements reader and writer roles structurally; no base class needed."""

    rows: dict[str, IspOrder] = field(default_factory=dict)

    def find_all(self) -> list[IspOrder]:
        return list(self.rows.values())

    def save(self, order: IspOrder) -> None:
        self.rows[order.id] = order


def nightly_report(reader: OrderReader) -> str:
    """Depends on the reader role only."""
    return f"paid={sum(1 for o in reader.find_all() if o.status == 'PAID')}"


def isp_demo() -> str:
    # Shows a reader-only dependency satisfied structurally by a Protocol.
    # Use when clients use disjoint parts of an interface.
    # Catch: one Protocol per method fragments the design; split by client role.
    store = InMemoryOrderStore()
    store.save(IspOrder("o-1", "PAID"))
    store.save(IspOrder("o-2", "NEW"))
    return (
        f"ISP violation: IspViolationOrderStore forces 4 abstract methods on every client fake\n"
        f"ISP fix:       nightly_report(OrderReader) -> {nightly_report(store)} "
        f"is_reader={isinstance(store, OrderReader)}"
    )


# ===== 1.5 DIP — policy owns the interface =====


@dataclass(frozen=True)
class DipOrder:
    id: str
    customer_id: str


class _PostgresOrderTable:
    def insert(self, order_id: str) -> None:  # would run INSERT INTO orders ...
        pass


class _SmtpMailer:
    def send(self, to: str, body: str) -> None:  # would open an SMTP socket
        pass


class DipViolationOrderService:
    """Constructs its own details: untestable without Postgres and SMTP."""

    def __init__(self) -> None:
        self._table = _PostgresOrderTable()
        self._mailer = _SmtpMailer()

    def place(self, order: DipOrder) -> str:
        self._table.insert(order.id)
        self._mailer.send(order.customer_id, f"placed {order.id}")
        return f"placed {order.id} via hard-wired Postgres + SMTP"


class OrderRepository(Protocol):
    """Port shaped on domain needs, not on a vendor API."""

    def save(self, order: DipOrder) -> None: ...


class Notifier(Protocol):
    def notify(self, customer_id: str, message: str) -> None: ...


@dataclass
class DipOrderService:
    """Policy: depends only on its own ports."""

    repo: OrderRepository
    notifier: Notifier

    def place(self, order: DipOrder) -> str:
        self.repo.save(order)
        self.notifier.notify(order.customer_id, f"placed {order.id}")
        return f"placed {order.id}"


@dataclass
class InMemoryOrderRepository:
    rows: dict[str, DipOrder] = field(default_factory=dict)

    def save(self, order: DipOrder) -> None:
        self.rows[order.id] = order


@dataclass
class RecordingNotifier:
    sent: list[str] = field(default_factory=list)

    def notify(self, customer_id: str, message: str) -> None:
        self.sent.append(f"{customer_id}:{message}")


def dip_demo() -> str:
    # Shows the policy running with in-memory adapters.
    # Use at I/O, vendor and team boundaries.
    # Catch: a Protocol mirroring one class forever is indirection without benefit.
    repo, notifier = InMemoryOrderRepository(), RecordingNotifier()
    result = DipOrderService(repo, notifier).place(DipOrder("o-1", "c-9"))
    return (
        f"DIP violation: {DipViolationOrderService().place(DipOrder('o-0', 'c-0'))}\n"
        f"DIP fix:       {result} stored={len(repo.rows)} notified={notifier.sent}"
    )
