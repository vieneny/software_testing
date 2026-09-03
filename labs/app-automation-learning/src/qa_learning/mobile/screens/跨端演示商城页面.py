"""Page objects for Sauce Labs' public My Demo App binaries."""

from __future__ import annotations

import re

from appium.webdriver.common.appiumby import AppiumBy

from qa_learning.mobile.screens.移动端基础页面 import BaseScreen


class AndroidMyDemoApp(BaseScreen):
    """One stable Android catalog-to-cart journey using resource IDs."""

    PACKAGE = "com.saucelabs.mydemoapp.android"
    TITLE = (AppiumBy.ID, f"{PACKAGE}:id/productTV")
    PRODUCT_IMAGES = (AppiumBy.ID, f"{PACKAGE}:id/productIV")
    ADD_TO_CART = (AppiumBy.ACCESSIBILITY_ID, "Tap to add product to cart")
    CART_BUTTON = (AppiumBy.ID, f"{PACKAGE}:id/cartRL")
    CART_BADGE = (AppiumBy.ID, f"{PACKAGE}:id/cartTV")
    CART_CONTENT = (AppiumBy.ID, f"{PACKAGE}:id/cartCL")
    CART_ITEMS = (AppiumBy.ID, f"{PACKAGE}:id/productRV")
    CART_COUNT = (AppiumBy.ID, f"{PACKAGE}:id/itemsTV")
    CART_TOTAL = (AppiumBy.ID, f"{PACKAGE}:id/totalPriceTV")

    def wait_for_catalog(self) -> None:
        self.wait_visible(self.TITLE)
        self.wait_visible(self.PRODUCT_IMAGES)

    def open_first_product(self) -> None:
        self.wait_visible(self.PRODUCT_IMAGES)
        self.driver.find_elements(*self.PRODUCT_IMAGES)[0].click()
        self.wait_visible(self.ADD_TO_CART)

    def add_one_to_cart(self) -> None:
        self.tap(self.ADD_TO_CART)
        self.wait_visible(self.CART_BADGE)

    def open_cart(self) -> None:
        self.tap(self.CART_BUTTON)
        self.wait_visible(self.CART_CONTENT)
        self.wait_visible(self.CART_TOTAL)

    def cart_has_item(self) -> bool:
        if not self.is_visible(self.CART_ITEMS, timeout=5):
            return False
        count = re.search(r"\d+", self.text(self.CART_COUNT))
        return count is not None and int(count.group()) > 0


class IosMyDemoApp(BaseScreen):
    """Pinned 2.2.2 journey using identifiers from upstream UI tests."""

    CATALOG_SCREEN = (AppiumBy.ACCESSIBILITY_ID, "Catalog-screen")
    FIRST_PRODUCT = (AppiumBy.ACCESSIBILITY_ID, "Product Name")
    PRODUCT_DETAILS_SCREEN = (AppiumBy.ACCESSIBILITY_ID, "ProductDetails-screen")
    ADD_TO_CART = (AppiumBy.ACCESSIBILITY_ID, "Add To Cart")
    CART_BUTTON = (AppiumBy.ACCESSIBILITY_ID, "Cart-tab-item")
    CART_SCREEN = (AppiumBy.ACCESSIBILITY_ID, "Cart-screen")
    BACKPACK_IN_CART = (AppiumBy.ACCESSIBILITY_ID, "Sauce Labs Backpack - Black")

    def wait_for_catalog(self) -> None:
        self.wait_visible(self.CATALOG_SCREEN)
        self.wait_visible(self.FIRST_PRODUCT)

    def add_backpack_to_cart(self) -> None:
        self.tap(self.FIRST_PRODUCT)
        self.wait_visible(self.PRODUCT_DETAILS_SCREEN)
        self.tap(self.ADD_TO_CART)
        self.tap(self.CART_BUTTON)
        self.wait_visible(self.CART_SCREEN)

    def cart_contains_backpack(self) -> bool:
        return self.is_visible(self.BACKPACK_IN_CART, timeout=8)
