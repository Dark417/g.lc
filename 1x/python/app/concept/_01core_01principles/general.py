"""Part B — general design principles (Java + Python). Violation, then Fix, then `<name>_demo()`.

- Same running domain as solid.py: orders -> payments -> notifications.
- Each demo comment states what it shows, when to use it, and the catch.
"""

from __future__ import annotations

import importlib
import threading
from collections.abc import Callable, Iterable, Mapping
from dataclasses import dataclass, field
from decimal import ROUND_HALF_UP, Decimal
from typing import Protocol

from app.shared.retry import call_with_retry

CENT = Decimal("0.01")


# ===== 2.1 DRY — one home per piece of knowledge =====


def dry_violation_checkout_tax(subtotal: Decimal) -> Decimal:
    return (subtotal * Decimal("0.08")).quantize(CENT, ROUND_HALF_UP)


def dry_violation_invoice_tax(subtotal: Decimal) -> Decimal:
    """Copy that drifted: someone changed the rate here only."""
    return (subtotal * Decimal("0.0825")).quantize(CENT, ROUND_HALF_UP)


@dataclass(frozen=True)
class TaxPolicy:
    """Single source of truth for the tax rule."""

    rate: Decimal

    def tax(self, subtotal: Decimal) -> Decimal:
        return (subtotal * self.rate).quantize(CENT, ROUND_HALF_UP)


def valid_api_amount(amount: Decimal) -> bool:
    """Looks like valid_backfill_amount, but has a different owner and reason to change: keep separate."""
    return Decimal("0") < amount <= Decimal("10000")


def valid_backfill_amount(amount: Decimal) -> bool:
    return Decimal("0") < amount <= Decimal("10000")


def dry_demo() -> str:
    # Shows drifted copies vs one policy.
    # Use for business rules, schemas and constants with one owner.
    # Catch: merging look-alike code with different owners creates the wrong abstraction.
    sub = Decimal("100.00")
    return (
        f"DRY violation: checkout={dry_violation_checkout_tax(sub)} invoice={dry_violation_invoice_tax(sub)}\n"
        f"DRY fix:       both={TaxPolicy(Decimal('0.08')).tax(sub)}\n"
        f"kept separate: api={valid_api_amount(sub)} backfill={valid_backfill_amount(sub)}"
    )


# ===== 2.2 KISS — simplest design that meets real requirements =====


@dataclass(frozen=True)
class KissRule:
    fact: str
    op: str
    threshold: Decimal
    fee: Decimal


@dataclass
class KissViolationRuleEngine:
    """Stringly-typed engine for a two-rule fee; readers must simulate it."""

    rules: list[KissRule]

    def evaluate(self, facts: dict[str, str]) -> Decimal:
        ops: dict[str, Callable[[Decimal, Decimal], bool]] = {"gt": lambda a, b: a > b, "eq": lambda a, b: a == b}
        return sum((r.fee for r in self.rules if ops[r.op](Decimal(facts[r.fact]), r.threshold)), Decimal("0"))


def shipping_fee(weight_kg: Decimal, express: bool) -> Decimal:
    """Direct code; still validates input (simple, not simplistic)."""
    if weight_kg < 0:
        raise ValueError("weight must be >= 0")
    fee = Decimal("12") if weight_kg > 5 else Decimal("5")
    return fee + Decimal("10") if express else fee


def kiss_demo() -> str:
    # Shows the same fee from an engine and from five lines.
    # Use when rules are few and owned by engineers.
    # Catch: if business users edit hundreds of rules without deploys, an engine is essential complexity.
    engine = KissViolationRuleEngine(
        [
            KissRule("weight", "gt", Decimal("-1"), Decimal("5")),
            KissRule("weight", "gt", Decimal("5"), Decimal("7")),
            KissRule("express", "eq", Decimal("1"), Decimal("10")),
        ]
    )
    return (
        f"KISS violation: engine fee={engine.evaluate({'weight': '7', 'express': '1'})}\n"
        f"KISS fix:       shipping_fee(7, express) = {shipping_fee(Decimal('7'), True)}"
    )


# ===== 2.3 YAGNI — don't build what nobody needs yet =====


class YagniOnlyProvider:
    def charge(self, amount: Decimal) -> str:
        return f"charged {amount}"


class YagniViolationPluginLoader:
    """Dynamic loading for a single provider: typos fail at runtime, IDEs can't follow it."""

    def load(self, path: str) -> YagniOnlyProvider:
        module_name, _, cls_name = path.partition(":")
        cls = getattr(importlib.import_module(module_name), cls_name)
        return cls()


@dataclass
class CardGateway:
    """Concrete now; the idempotency key is kept because adding it later breaks the public API."""

    processed: dict[str, str] = field(default_factory=dict)
    _lock: threading.Lock = field(default_factory=threading.Lock, repr=False)

    def charge(self, idempotency_key: str, amount: Decimal) -> str:
        with self._lock:
            if idempotency_key not in self.processed:
                self.processed[idempotency_key] = f"charge-{idempotency_key}-{amount}"
            return self.processed[idempotency_key]


def yagni_demo() -> str:
    # Shows a plugin loader for one plugin vs a concrete class; a retry with the same key charges once.
    # Use YAGNI for features and extension points.
    # Catch: never for retrofit-expensive properties (idempotency, auth, schema versions, observability).
    plugin = YagniViolationPluginLoader().load(f"{__name__}:YagniOnlyProvider")
    gw = CardGateway()
    first, retry = gw.charge("req-1", Decimal("10")), gw.charge("req-1", Decimal("10"))
    return (
        f"YAGNI violation: {plugin.charge(Decimal('10'))} via dynamic import\n"
        f"YAGNI fix:       {first} retry_same={first == retry} charges={len(gw.processed)}"
    )


# ===== 2.4 Separation of Concerns =====


def soc_violation_handle(raw: str, sql_log: list[str]) -> str:
    """Parsing, business rule, SQL and logging tangled together."""
    order_id, amount_s = raw.split(",")
    amount = Decimal(amount_s.strip())
    if amount >= 100:
        amount *= Decimal("0.9")
    sql_log.append(f"INSERT INTO orders VALUES ('{order_id}', {amount})")  # string SQL: injectable
    print(f"handled {order_id}")
    return f"{order_id}={amount}"


@dataclass(frozen=True)
class OrderRequest:
    id: str
    amount: Decimal


def parse_order(raw: str) -> OrderRequest:
    """Parsing concern only."""
    parts = raw.split(",")
    if len(parts) != 2:
        raise ValueError(f"expected 'id,amount' but got {raw!r}")
    return OrderRequest(parts[0].strip(), Decimal(parts[1].strip()))


class DiscountRule:
    """Business concern only: testable with plain values."""

    def apply(self, amount: Decimal) -> Decimal:
        return amount * Decimal("0.9") if amount >= 100 else amount


class OrderSink(Protocol):
    def save(self, order_id: str, amount: Decimal) -> None: ...


@dataclass
class ListSink:
    rows: list[str] = field(default_factory=list)

    def save(self, order_id: str, amount: Decimal) -> None:
        self.rows.append(f"{order_id}={amount}")


@dataclass
class SocOrderHandler:
    """Coordinator: wires concerns, owns none of their rules."""

    discount: DiscountRule
    sink: OrderSink

    def handle(self, raw: str) -> str:
        req = parse_order(raw)
        amount = self.discount.apply(req.amount)
        self.sink.save(req.id, amount)
        return f"{req.id}={amount}"


def soc_demo() -> str:
    # Shows identical results; only the fix lets you test the discount alone.
    # Use whenever a unit mixes input format, rules and storage.
    # Catch: layers alone scatter one feature; package by feature, cross-cutting via decorators/middleware.
    sql: list[str] = []
    bad = soc_violation_handle("o-1, 120", sql)
    sink = ListSink()
    good = SocOrderHandler(DiscountRule(), sink).handle("o-1, 120")
    return f"SoC violation: {bad} sql={sql}\nSoC fix:       {good} rows={sink.rows}"


# ===== 2.5 High cohesion / low coupling =====


@dataclass(frozen=True)
class Address:
    street: str
    zip: str


@dataclass(frozen=True)
class Customer:
    id: str
    address: Address


@dataclass(frozen=True)
class ShipOrder:
    id: str
    customer: Customer

    def shipping_zip(self) -> str:
        """Hides where the zip lives; callers ask for what they need."""
        return self.customer.address.zip


class CohesionViolationUtils:
    """Grab-bag of unrelated helpers; shipping_cost knows the full Order -> Customer -> Address shape."""

    @staticmethod
    def format_date(iso: str) -> str:
        return iso[:10]

    @staticmethod
    def slack_message(text: str) -> str:
        return f":package: {text}"

    @staticmethod
    def shipping_cost(order: ShipOrder) -> Decimal:
        return Decimal("15") if order.customer.address.zip.startswith("9") else Decimal("8")


@dataclass(frozen=True)
class ShippingQuote:
    """Cohesive: everything here is about quoting shipping."""

    west_coast: Decimal
    standard: Decimal

    def quote_for(self, order: ShipOrder) -> Decimal:
        return self.west_coast if order.shipping_zip().startswith("9") else self.standard


def cohesion_demo() -> str:
    # Shows the same quote; in the fix an Address refactor touches ShipOrder only.
    # Use co-change history (git log) to decide what belongs together.
    # Catch: swapping typed calls for dicts/events hides coupling instead of removing it.
    order = ShipOrder("o-1", Customer("c-1", Address("1 Main", "94105")))
    return (
        f"Cohesion violation: shipping_cost={CohesionViolationUtils.shipping_cost(order)}\n"
        f"Cohesion fix:       quote_for={ShippingQuote(Decimal('15'), Decimal('8')).quote_for(order)}"
    )


# ===== 2.6 Composition over inheritance =====


class CompositionViolationEmail:
    def send(self, to: str, msg: str) -> str:
        return f"email to {to}: {msg}"


class CompositionViolationRetryingEmail(CompositionViolationEmail):
    """Retry welded to email; SMS would need its own retrying subclass."""

    def send(self, to: str, msg: str) -> str:
        return call_with_retry(lambda: super(CompositionViolationRetryingEmail, self).send(to, msg),
                               lambda e: True, max_attempts=3, base=0.001, cap=0.005)


class CompositionViolationLoggingRetryingEmail(CompositionViolationRetryingEmail):
    """Third level: depends on both parents' behavior (fragile base class)."""

    def __init__(self) -> None:
        self.log: list[str] = []

    def send(self, to: str, msg: str) -> str:
        self.log.append(f"send {to}")
        return super().send(to, msg)


class Notifier(Protocol):
    def send(self, to: str, msg: str) -> str: ...


@dataclass
class FlakyEmail:
    """Fails the first N calls so retries are visible."""

    failures: int
    calls: int = 0

    def send(self, to: str, msg: str) -> str:
        self.calls += 1
        if self.failures > 0:
            self.failures -= 1
            raise TimeoutError("smtp timeout")
        return f"email to {to}: {msg}"


@dataclass
class RetryingNotifier:
    """Retry decorator using the shared full-jitter helper; only for idempotent sends."""

    inner: Notifier
    max_attempts: int = 3

    def send(self, to: str, msg: str) -> str:
        return call_with_retry(lambda: self.inner.send(to, msg), lambda e: isinstance(e, TimeoutError),
                               max_attempts=self.max_attempts, base=0.001, cap=0.005)


@dataclass
class LoggingNotifier:
    inner: Notifier
    log: list[str] = field(default_factory=list)

    def send(self, to: str, msg: str) -> str:
        self.log.append(f"send {to}")
        return self.inner.send(to, msg)


def composition_demo() -> str:
    # Shows the same parts in two orders: log lines count requests vs attempts.
    # Use when features combine freely (retry, logging, metrics, rate limits).
    # Catch: decorator order is a contract; inheritance is still right for bases designed for extension.
    tree = CompositionViolationLoggingRetryingEmail()
    bad = tree.send("a@example.com", "hi")
    e1 = FlakyEmail(failures=2)
    outer = LoggingNotifier(RetryingNotifier(e1))
    r1 = outer.send("a@example.com", "hi")
    e2 = FlakyEmail(failures=2)
    inner = LoggingNotifier(e2)
    RetryingNotifier(inner).send("a@example.com", "hi")
    return (
        f"Composition violation: {bad} (class per combination)\n"
        f"Composition fix:       {r1}\n"
        f"  Logging(Retrying(email)) log lines={len(outer.log)} (requests), email calls={e1.calls}\n"
        f"  Retrying(Logging(email)) log lines={len(inner.log)} (attempts)"
    )


# ===== 2.7 Program to an interface =====


@dataclass(frozen=True)
class AmountOrder:
    customer_id: str
    amount: Decimal


def total_of_violation(orders: list[AmountOrder]) -> dict[str, Decimal]:
    """Demands a list although it only iterates; tuples, sets and generators need a copy."""
    totals: dict[str, Decimal] = {}
    for o in orders:
        totals[o.customer_id] = totals.get(o.customer_id, Decimal("0")) + o.amount
    return totals


def total_of(orders: Iterable[AmountOrder]) -> Mapping[str, Decimal]:
    """Widest input it can handle; read-only Mapping output leaves the implementation free."""
    totals: dict[str, Decimal] = {}
    for o in orders:
        totals[o.customer_id] = totals.get(o.customer_id, Decimal("0")) + o.amount
    return totals


def interface_demo() -> str:
    # Shows a generator accepted by the fix with no copy.
    # Use for every public function signature.
    # Catch: protocols don't state cost; an Iterable may be single-pass (a generator), so don't iterate twice.
    orders = (AmountOrder("c-1", Decimal(n)) for n in ("1", "10"))
    return (
        f"Interface violation: {total_of_violation([AmountOrder('c-1', Decimal('11'))])} (needed list(...))\n"
        f"Interface fix:       {dict(total_of(orders))} from a generator"
    )


# ===== 2.8 Encapsulate what varies =====


def checkout_fee_violation(region: str, amount: Decimal) -> Decimal:
    """Volatile region rules inline in the stable checkout flow."""
    if region == "US":
        return amount * Decimal("0.03")
    if region == "EU":
        return amount * Decimal("0.02") + Decimal("0.25")
    return Decimal("1.00")


class FeePolicy(Protocol):
    def fee(self, amount: Decimal) -> Decimal: ...


@dataclass(frozen=True)
class PercentFee:
    """Data, not code: rates can come from config."""

    rate: Decimal
    fixed: Decimal = Decimal("0")

    def fee(self, amount: Decimal) -> Decimal:
        return amount * self.rate + self.fixed


FEE_POLICIES: dict[str, FeePolicy] = {
    "US": PercentFee(Decimal("0.03")),
    "EU": PercentFee(Decimal("0.02"), Decimal("0.25")),
}
FALLBACK_FEE: FeePolicy = PercentFee(Decimal("0"), Decimal("1.00"))


def checkout_fee(region: str, amount: Decimal, policies: Mapping[str, FeePolicy] = FEE_POLICIES) -> Decimal:
    """Stable part: unchanged when fees change."""
    return policies.get(region, FALLBACK_FEE).fee(amount)


def encapsulate_demo() -> str:
    # Shows the same fees; the fix moves the volatile part behind FeePolicy.
    # Use when one part changes on a different schedule than the rest.
    # Catch: guessing the axis of change creates abstractions around stable code.
    amt = Decimal("100")
    return (
        f"Encapsulate violation: EU={checkout_fee_violation('EU', amt)}\n"
        f"Encapsulate fix:       EU={checkout_fee('EU', amt)} APAC={checkout_fee('APAC', amt)}"
    )


# ===== 2.9 Law of Demeter =====


@dataclass(frozen=True)
class LodWallet:
    balance: Decimal

    def covers(self, amount: Decimal) -> bool:
        return self.balance >= amount


@dataclass(frozen=True)
class LodCustomer:
    wallet: LodWallet

    def can_afford(self, amount: Decimal) -> bool:
        return self.wallet.covers(amount)


@dataclass(frozen=True)
class LodOrder:
    customer: LodCustomer

    def can_pay(self, amount: Decimal) -> bool:
        """Callers ask the order; the path to the wallet can change freely."""
        return self.customer.can_afford(amount)


def lod_violation_can_pay(order: LodOrder, amount: Decimal) -> bool:
    """Reaches through three objects; a wallet refactor breaks every such caller."""
    return order.customer.wallet.balance >= amount


def lod_demo() -> str:
    # Shows the same answer with and without reaching through objects.
    # Use for behavior-rich domain objects.
    # Catch: chains over plain data and fluent APIs are fine; strict LoD grows forwarding methods.
    order = LodOrder(LodCustomer(LodWallet(Decimal("50"))))
    return (
        f"LoD violation: {lod_violation_can_pay(order, Decimal('20'))} via order.customer.wallet.balance\n"
        f"LoD fix:       {order.can_pay(Decimal('20'))} via order.can_pay(amount)"
    )


# ===== 2.10 Tell, don't ask =====


@dataclass
class AnemicWallet:
    balance: Decimal


def tda_violation_charge(wallet: AnemicWallet, amount: Decimal) -> bool:
    """The overdraft rule lives in the caller and must be copied everywhere."""
    if wallet.balance >= amount:
        wallet.balance -= amount
        return True
    return False


class InsufficientFunds(Exception):
    pass


class Wallet:
    """Invariant guarded next to the data; the lock makes check + write one step."""

    def __init__(self, balance: Decimal) -> None:
        self._balance = balance
        self._lock = threading.Lock()

    def debit(self, amount: Decimal) -> None:
        if amount <= 0:
            raise ValueError("amount must be > 0")
        with self._lock:
            if self._balance < amount:
                raise InsufficientFunds(f"balance {self._balance} < {amount}")
            self._balance -= amount

    @property
    def balance(self) -> Decimal:
        """A query for display is fine (CQS)."""
        return self._balance


def tda_demo() -> str:
    # Shows the rule moving into the wallet; the bypass via attribute writes is gone.
    # Use for stateful domain objects with invariants.
    # Catch: Spark/Databricks transforms are functions over plain data; tell-don't-ask does not apply there.
    anemic = AnemicWallet(Decimal("10"))
    tda_violation_charge(anemic, Decimal("4"))
    anemic.balance = Decimal("-100")  # nothing stops this
    wallet = Wallet(Decimal("10"))
    wallet.debit(Decimal("4"))
    try:
        wallet.debit(Decimal("100"))
        overdraft = "allowed"
    except InsufficientFunds as e:
        overdraft = f"rejected: {e}"
    return f"TDA violation: balance={anemic.balance}\nTDA fix:       balance={wallet.balance} overdraft {overdraft}"


# ===== 2.11 CQS =====


class CqsViolationNumbers:
    def __init__(self) -> None:
        self._next = 1

    def next_order_number(self) -> int:
        """Reads like a query; every call (log, debugger, retry) burns a number."""
        n = self._next
        self._next += 1
        return n


class CqsOrderNumbers:
    def __init__(self) -> None:
        self._next = 1
        self._lock = threading.Lock()

    def peek_next(self) -> int:
        """Query: safe to repeat."""
        return self._next

    def advance(self) -> None:
        """Command: changes state, returns nothing."""
        with self._lock:
            self._next += 1

    def reserve_number(self) -> int:
        """Justified exception: atomic reserve-and-return (like INSERT ... RETURNING id)."""
        with self._lock:
            n = self._next
            self._next += 1
            return n


def cqs_demo() -> str:
    # Shows a "getter" burning numbers vs a safe query, then the atomic exception.
    # Use for any API callers might retry, log or cache.
    # Catch: peek_next() + advance() from two threads can hand out the same number.
    bad = CqsViolationNumbers()
    bad.next_order_number()
    lost = bad.next_order_number()
    good = CqsOrderNumbers()
    good.peek_next()
    good.peek_next()
    reserved = good.reserve_number()
    return (
        f"CQS violation: second 'read' returned {lost} (number 1 lost)\n"
        f"CQS fix:       peek twice then reserve -> {reserved}, next={good.peek_next()}"
    )


# ===== 2.12 Fail fast =====


@dataclass(frozen=True)
class FailFastViolationOrder:
    id: str
    amount: Decimal
    currency: str | None


@dataclass(frozen=True)
class FailFastOrder:
    id: str
    amount: Decimal
    currency: str

    def __post_init__(self) -> None:
        """Invalid objects cannot exist; explicit raises survive `python -O` (asserts don't)."""
        if self.amount <= 0:
            raise ValueError(f"amount must be > 0, got {self.amount}")
        if not isinstance(self.currency, str) or len(self.currency) != 3:
            raise ValueError(f"currency must be ISO-4217, got {self.currency!r}")


@dataclass
class BatchResult:
    accepted: list[FailFastOrder]
    quarantined: list[str]


def validate_batch(rows: Iterable[tuple[str, str, str]]) -> BatchResult:
    """Per-record fail fast: reject with a reason, continue the batch (Databricks job, Kafka consumer)."""
    result = BatchResult([], [])
    for row in rows:
        try:
            result.accepted.append(FailFastOrder(row[0], Decimal(row[1]), row[2]))
        except (ValueError, ArithmeticError) as e:
            result.quarantined.append(f"{','.join(row)} -> {e}")
    return result


def failfast_demo() -> str:
    # Shows invalid data accepted silently vs rejected at construction, plus per-record batch handling.
    # Use at every trust boundary (HTTP, files, config).
    # Catch: fail fast per record, not per system; alert on the quarantine rate.
    silent = FailFastViolationOrder("o-1", Decimal("-5"), None)
    try:
        FailFastOrder("o-1", Decimal("-5"), "USD")
        rejected = "accepted"
    except ValueError as e:
        rejected = str(e)
    batch = validate_batch([("o-1", "10", "USD"), ("o-2", "-1", "USD"), ("o-3", "7", "EURO")])
    return (
        f"FailFast violation: accepted {silent}\n"
        f"FailFast fix:       {rejected}\n"
        f"batch:              accepted={len(batch.accepted)} quarantined={batch.quarantined}"
    )


# ===== 2.13 Principle of least astonishment =====


def pola_violation_add(item: str, items: list[str] = []) -> list[str]:  # noqa: B006 - the point of the demo
    """Mutable default is created once, so every call without `items` shares one list."""
    items.append(item)
    return items


def pola_add(item: str, items: list[str] | None = None) -> list[str]:
    """None default: a fresh list per call, as readers expect."""
    result = [] if items is None else items
    result.append(item)
    return result


def pola_demo() -> str:
    # Shows the shared-default surprise and the idiomatic fix.
    # Use when naming functions and choosing defaults.
    # Catch: astonishment is audience-relative; follow the ecosystem's conventions.
    pola_violation_add("a")
    shared = pola_violation_add("b")
    pola_add("a")
    fresh = pola_add("b")
    return f"POLA violation: second call returned {shared}\nPOLA fix:       second call returned {fresh}"
