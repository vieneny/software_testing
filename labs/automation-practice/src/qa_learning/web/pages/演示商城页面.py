"""Page objects for Sauce Labs' public SauceDemo application."""

from __future__ import annotations

import re

from playwright.sync_api import Locator, Page, expect

from qa_learning.web.浏览器练习目标 import SauceDemoTarget


class SauceLoginPage:
    def __init__(
        self,
        page: Page,
        target: SauceDemoTarget | None = None,
    ) -> None:
        self.page = page
        self.target = target or SauceDemoTarget()
        self.username = page.locator("[data-test='username']")
        self.password = page.locator("[data-test='password']")
        self.submit = page.locator("[data-test='login-button']")
        self.error = page.locator("[data-test='error']")

    def open(self) -> None:
        self.page.goto(
            self.target.base_url,
            wait_until="domcontentloaded",
        )
        expect(self.username).to_be_editable()
        expect(self.submit).to_be_enabled()

    def login(self, username: str, password: str) -> None:
        self.username.fill(username)
        self.password.fill(password)
        self.submit.click()


class SauceInventoryPage:
    def __init__(self, page: Page) -> None:
        self.page = page
        self.container = page.locator("[data-test='inventory-container']")
        self.items = page.locator("[data-test='inventory-item']")
        self.names = page.locator("[data-test='inventory-item-name']")
        self.prices = page.locator("[data-test='inventory-item-price']")
        self.sort_select = page.locator("[data-test='product-sort-container']")
        self.cart_link = page.locator("[data-test='shopping-cart-link']")
        self.cart_badge = page.locator("[data-test='shopping-cart-badge']")

    def wait_until_loaded(self) -> None:
        expect(self.page).to_have_url(re.compile(r"/inventory\.html$"))
        expect(self.container).to_be_visible()
        expect(self.items.first).to_be_visible()

    def item(self, product_name: str) -> Locator:
        exact_name = re.compile(rf"^{re.escape(product_name)}$")
        name_locator = self.page.locator("[data-test='inventory-item-name']").filter(
            has_text=exact_name
        )
        return self.items.filter(has=name_locator)

    def add_to_cart(self, product_name: str) -> None:
        item = self.item(product_name)
        expect(item).to_be_visible()
        item.get_by_role("button", name="Add to cart").click()

    def remove_from_cart(self, product_name: str) -> None:
        item = self.item(product_name)
        expect(item).to_be_visible()
        item.get_by_role("button", name="Remove").click()

    def sort_by(self, value: str) -> None:
        """Sort with SauceDemo's documented select values.

        Values are ``az``, ``za``, ``lohi`` and ``hilo``.
        """

        if value not in {"az", "za", "lohi", "hilo"}:
            raise ValueError(f"unsupported SauceDemo sort value: {value}")
        self.sort_select.select_option(value)

    def open_cart(self) -> None:
        self.cart_link.click()

    def visible_prices(self) -> list[float]:
        return [float(text.replace("$", "")) for text in self.prices.all_text_contents()]


class SauceCartPage:
    def __init__(self, page: Page) -> None:
        self.page = page
        self.items = page.locator("[data-test='inventory-item']")
        self.checkout_button = page.locator("[data-test='checkout']")

    def wait_until_loaded(self) -> None:
        expect(self.page).to_have_url(re.compile(r"/cart\.html$"))
        expect(self.checkout_button).to_be_visible()

    def item(self, product_name: str) -> Locator:
        exact_name = re.compile(rf"^{re.escape(product_name)}$")
        name_locator = self.page.locator("[data-test='inventory-item-name']").filter(
            has_text=exact_name
        )
        return self.items.filter(has=name_locator)

    def checkout(self) -> None:
        self.checkout_button.click()


class SauceCheckoutPage:
    def __init__(self, page: Page) -> None:
        self.page = page
        self.first_name = page.locator("[data-test='firstName']")
        self.last_name = page.locator("[data-test='lastName']")
        self.postal_code = page.locator("[data-test='postalCode']")
        self.continue_button = page.locator("[data-test='continue']")
        self.error = page.locator("[data-test='error']")
        self.summary = page.locator("[data-test='checkout-summary-container']")
        self.item_total = page.locator("[data-test='subtotal-label']")
        self.tax = page.locator("[data-test='tax-label']")
        self.total = page.locator("[data-test='total-label']")
        self.finish_button = page.locator("[data-test='finish']")
        self.complete_header = page.locator("[data-test='complete-header']")

    def wait_for_customer_form(self) -> None:
        expect(self.page).to_have_url(re.compile(r"/checkout-step-one\.html$"))
        expect(self.first_name).to_be_editable()

    def enter_customer(
        self,
        *,
        first_name: str,
        last_name: str,
        postal_code: str,
    ) -> None:
        self.first_name.fill(first_name)
        self.last_name.fill(last_name)
        self.postal_code.fill(postal_code)

    def continue_to_summary(self) -> None:
        self.continue_button.click()

    def wait_for_summary(self) -> None:
        expect(self.page).to_have_url(re.compile(r"/checkout-step-two\.html$"))
        expect(self.summary).to_be_visible()
        expect(self.item_total).to_contain_text("Item total:")
        expect(self.total).to_contain_text("Total:")

    def finish(self) -> None:
        self.finish_button.click()

    def wait_for_confirmation(self) -> None:
        expect(self.page).to_have_url(re.compile(r"/checkout-complete\.html$"))
        expect(self.complete_header).to_have_text("Thank you for your order!")
