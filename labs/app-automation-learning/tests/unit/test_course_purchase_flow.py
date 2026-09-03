from decimal import Decimal

import pytest

from qa_learning.mobile.course_project import (
    AuthenticationError,
    InvalidFlowStateError,
    ProductNotFoundError,
    PurchaseFlow,
    PurchaseRequest,
    SyntheticCommerceApp,
)


def request(**overrides: object) -> PurchaseRequest:
    values = {
        "username": "learner@example.test",
        "password": "demo-pass",
        "keyword": "毛巾",
        "quantity": 2,
        "idempotency_key": "case-purchase-001",
    }
    values.update(overrides)
    return PurchaseRequest(**values)  # type: ignore[arg-type]


def test_full_login_search_cart_checkout_flow() -> None:
    app = SyntheticCommerceApp()

    result = PurchaseFlow(app).execute(request())

    assert result.order_id == "SYN-0001"
    assert result.product_id == "learning-towel"
    assert result.total == Decimal("59.80")
    assert app.events == [
        "login:accepted",
        "search:毛巾:1",
        "cart:learning-towel:2",
        "checkout:created:case-purchase-001",
    ]


def test_login_failure_stops_before_search() -> None:
    app = SyntheticCommerceApp()

    with pytest.raises(AuthenticationError):
        PurchaseFlow(app).execute(request(password="wrong"))

    assert app.events == ["login:rejected"]


def test_empty_search_has_an_observable_failure() -> None:
    app = SyntheticCommerceApp()

    with pytest.raises(ProductNotFoundError):
        PurchaseFlow(app).execute(request(keyword="不存在的商品"))

    assert app.events[-1] == "search:不存在的商品:0"


@pytest.mark.parametrize("quantity", [0, 6])
def test_cart_quantity_respects_stock_boundaries(quantity: int) -> None:
    app = SyntheticCommerceApp()

    with pytest.raises(ValueError, match="1..5"):
        PurchaseFlow(app).execute(request(quantity=quantity))


def test_checkout_reuses_the_same_idempotency_key() -> None:
    app = SyntheticCommerceApp()
    flow = PurchaseFlow(app)

    first = flow.execute(request())
    second = app.checkout("case-purchase-001")

    assert second == first
    assert len(app.orders) == 1
    assert app.events[-1] == "checkout:reused:case-purchase-001"


def test_checkout_cannot_skip_required_screen_states() -> None:
    app = SyntheticCommerceApp()

    with pytest.raises(InvalidFlowStateError, match="购物车"):
        app.checkout("case-purchase-002")
