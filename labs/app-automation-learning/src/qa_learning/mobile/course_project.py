"""Deterministic commerce flow used to learn App project boundaries."""

from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal
from enum import StrEnum
from typing import Protocol


class FlowState(StrEnum):
    STARTED = "started"
    AUTHENTICATED = "authenticated"
    SEARCHED = "searched"
    CART_READY = "cart_ready"
    ORDERED = "ordered"


class FlowError(RuntimeError):
    """Base error for an observable business-flow failure."""


class AuthenticationError(FlowError):
    pass


class ProductNotFoundError(FlowError):
    pass


class InvalidFlowStateError(FlowError):
    pass


@dataclass(frozen=True, slots=True)
class Product:
    product_id: str
    name: str
    price: Decimal
    stock: int


@dataclass(frozen=True, slots=True)
class PurchaseRequest:
    username: str
    password: str
    keyword: str
    quantity: int
    idempotency_key: str


@dataclass(frozen=True, slots=True)
class PurchaseResult:
    order_id: str
    product_id: str
    quantity: int
    total: Decimal
    state: FlowState


class CommerceScreenGateway(Protocol):
    """Behaviors implemented by a synthetic adapter or real Screen/Flow layer."""

    def login(self, username: str, password: str) -> None: ...

    def search(self, keyword: str) -> list[Product]: ...

    def add_to_cart(self, product_id: str, quantity: int) -> None: ...

    def checkout(self, idempotency_key: str) -> PurchaseResult: ...


@dataclass(slots=True)
class SyntheticCommerceApp:
    """In-memory adapter with the same business checkpoints as the UI flow."""

    products: tuple[Product, ...] = (
        Product("learning-towel", "自动化学习毛巾", Decimal("29.90"), 5),
        Product("learning-bag", "移动测试练习包", Decimal("88.00"), 2),
    )
    state: FlowState = FlowState.STARTED
    selected: Product | None = None
    quantity: int = 0
    orders: dict[str, PurchaseResult] = field(default_factory=dict)
    events: list[str] = field(default_factory=list)

    def login(self, username: str, password: str) -> None:
        if username != "learner@example.test" or password != "demo-pass":
            self.events.append("login:rejected")
            raise AuthenticationError("合成账号或密码不匹配")
        self.state = FlowState.AUTHENTICATED
        self.events.append("login:accepted")

    def search(self, keyword: str) -> list[Product]:
        if self.state is not FlowState.AUTHENTICATED:
            raise InvalidFlowStateError("搜索前必须完成登录")
        normalized = keyword.strip().casefold()
        matches = [item for item in self.products if normalized in item.name.casefold()]
        self.events.append(f"search:{normalized}:{len(matches)}")
        if not matches:
            raise ProductNotFoundError(f"没有找到合成商品：{keyword}")
        self.selected = matches[0]
        self.state = FlowState.SEARCHED
        return matches

    def add_to_cart(self, product_id: str, quantity: int) -> None:
        if self.state is not FlowState.SEARCHED or self.selected is None:
            raise InvalidFlowStateError("加购前必须先得到搜索结果")
        if product_id != self.selected.product_id:
            raise ProductNotFoundError(product_id)
        if quantity < 1 or quantity > self.selected.stock:
            raise ValueError(f"数量必须在 1..{self.selected.stock} 之间")
        self.quantity = quantity
        self.state = FlowState.CART_READY
        self.events.append(f"cart:{product_id}:{quantity}")

    def checkout(self, idempotency_key: str) -> PurchaseResult:
        if idempotency_key in self.orders:
            self.events.append(f"checkout:reused:{idempotency_key}")
            return self.orders[idempotency_key]
        if self.state is not FlowState.CART_READY or self.selected is None:
            raise InvalidFlowStateError("结算前购物车必须存在有效商品")
        if not idempotency_key.strip():
            raise ValueError("幂等键不能为空")
        result = PurchaseResult(
            order_id=f"SYN-{len(self.orders) + 1:04d}",
            product_id=self.selected.product_id,
            quantity=self.quantity,
            total=self.selected.price * self.quantity,
            state=FlowState.ORDERED,
        )
        self.orders[idempotency_key] = result
        self.state = FlowState.ORDERED
        self.events.append(f"checkout:created:{idempotency_key}")
        return result


class PurchaseFlow:
    """Orchestrate screens while leaving assertions visible to the test."""

    def __init__(self, gateway: CommerceScreenGateway) -> None:
        self.gateway = gateway

    def execute(self, request: PurchaseRequest) -> PurchaseResult:
        self.gateway.login(request.username, request.password)
        product = self.gateway.search(request.keyword)[0]
        self.gateway.add_to_cart(product.product_id, request.quantity)
        return self.gateway.checkout(request.idempotency_key)
