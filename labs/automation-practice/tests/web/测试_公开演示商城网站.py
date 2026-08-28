"""Opt-in, low-frequency business-flow exercises against SauceDemo."""

from __future__ import annotations

import re

import pytest
from playwright.sync_api import Page, expect

from qa_learning.web.flows import CheckoutCustomer, SauceCheckoutFlow
from qa_learning.web.pages import (
    SauceCartPage,
    SauceCheckoutPage,
    SauceInventoryPage,
    SauceLoginPage,
)
from qa_learning.web.浏览器练习目标 import SauceDemoTarget
from qa_learning.运行配置 import Settings

pytestmark = [pytest.mark.web, pytest.mark.external]


@pytest.fixture(scope="session")
def sauce_target(settings: Settings) -> SauceDemoTarget:
    return SauceDemoTarget(
        base_url=settings.sauce_demo_url,
        standard_username=settings.sauce_username,
        password=settings.sauce_password,
    )


@pytest.mark.smoke
def test_locked_user_cannot_login(
    page: Page,
    public_web_guard: None,
    sauce_target: SauceDemoTarget,
) -> None:
    login = SauceLoginPage(page, sauce_target)
    login.open()

    login.login(sauce_target.locked_username, sauce_target.password)

    expect(login.error).to_contain_text("Sorry, this user has been locked out.")
    expect(page).to_have_url(re.compile(r"saucedemo\.com/?$"))


@pytest.mark.challenge
def test_products_can_be_sorted_by_price(
    page: Page,
    public_web_guard: None,
    sauce_target: SauceDemoTarget,
) -> None:
    login = SauceLoginPage(page, sauce_target)
    inventory = SauceInventoryPage(page)
    login.open()
    login.login(sauce_target.standard_username, sauce_target.password)
    inventory.wait_until_loaded()

    inventory.sort_by("lohi")
    ascending_prices = inventory.visible_prices()
    assert ascending_prices == sorted(ascending_prices)

    inventory.sort_by("hilo")
    descending_prices = inventory.visible_prices()
    assert descending_prices == sorted(descending_prices, reverse=True)


@pytest.mark.challenge
def test_checkout_requires_first_name(
    page: Page,
    public_web_guard: None,
    sauce_target: SauceDemoTarget,
) -> None:
    flow = SauceCheckoutFlow(page, sauce_target)
    flow.login_as_standard_user()
    flow.inventory_page.add_to_cart("Sauce Labs Backpack")
    flow.inventory_page.open_cart()

    cart = SauceCartPage(page)
    cart.wait_until_loaded()
    cart.checkout()

    checkout = SauceCheckoutPage(page)
    checkout.wait_for_customer_form()
    checkout.continue_to_summary()

    expect(checkout.error).to_contain_text("First Name is required")
    expect(page).to_have_url(re.compile(r"/checkout-step-one\.html$"))


@pytest.mark.e2e
def test_standard_user_completes_two_product_checkout(
    page: Page,
    public_web_guard: None,
    sauce_target: SauceDemoTarget,
) -> None:
    """The framework's representative cross-page, end-to-end journey."""

    flow = SauceCheckoutFlow(page, sauce_target)
    flow.purchase(
        [
            "Sauce Labs Backpack",
            "Sauce Labs Bike Light",
        ],
        CheckoutCustomer(
            first_name="Learning",
            last_name="Tester",
            postal_code="000000",
        ),
    )

    expect(flow.checkout_page.item_total).to_contain_text("$39.98")
    expect(flow.checkout_page.tax).to_contain_text("Tax:")
    expect(flow.checkout_page.total).to_contain_text("Total:")

    flow.finish()
    expect(flow.checkout_page.complete_header).to_have_text("Thank you for your order!")
