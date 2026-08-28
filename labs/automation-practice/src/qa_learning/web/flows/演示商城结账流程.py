"""A readable cross-page checkout flow for SauceDemo."""

from __future__ import annotations

from dataclasses import dataclass

from playwright.sync_api import Page, expect

from qa_learning.web.pages.演示商城页面 import (
    SauceCartPage,
    SauceCheckoutPage,
    SauceInventoryPage,
    SauceLoginPage,
)
from qa_learning.web.浏览器练习目标 import SauceDemoTarget


@dataclass(frozen=True, slots=True)
class CheckoutCustomer:
    """Clearly synthetic checkout data; no real identity is needed."""

    first_name: str
    last_name: str
    postal_code: str


class SauceCheckoutFlow:
    """Orchestrate a business journey while pages own page-level behavior."""

    def __init__(
        self,
        page: Page,
        target: SauceDemoTarget | None = None,
    ) -> None:
        self.page = page
        self.target = target or SauceDemoTarget()
        self.login_page = SauceLoginPage(page, self.target)
        self.inventory_page = SauceInventoryPage(page)
        self.cart_page = SauceCartPage(page)
        self.checkout_page = SauceCheckoutPage(page)

    def login_as_standard_user(self) -> None:
        self.login_page.open()
        self.login_page.login(
            self.target.standard_username,
            self.target.password,
        )
        self.inventory_page.wait_until_loaded()

    def purchase(
        self,
        product_names: list[str],
        customer: CheckoutCustomer,
    ) -> None:
        if not product_names:
            raise ValueError("checkout requires at least one product")

        self.login_as_standard_user()

        for expected_count, product_name in enumerate(product_names, start=1):
            self.inventory_page.add_to_cart(product_name)
            expect(self.inventory_page.cart_badge).to_have_text(str(expected_count))

        self.inventory_page.open_cart()
        self.cart_page.wait_until_loaded()
        for product_name in product_names:
            expect(self.cart_page.item(product_name)).to_be_visible()

        self.cart_page.checkout()
        self.checkout_page.wait_for_customer_form()
        self.checkout_page.enter_customer(
            first_name=customer.first_name,
            last_name=customer.last_name,
            postal_code=customer.postal_code,
        )
        self.checkout_page.continue_to_summary()
        self.checkout_page.wait_for_summary()

    def finish(self) -> None:
        self.checkout_page.finish()
        self.checkout_page.wait_for_confirmation()
