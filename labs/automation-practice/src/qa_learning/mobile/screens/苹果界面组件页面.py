"""Page object for Appium's Apache-2.0 UIKitCatalog sample."""

from appium.webdriver.common.appiumby import AppiumBy

from qa_learning.mobile.screens.移动端基础页面 import BaseScreen


class UIKitCatalogScreen(BaseScreen):
    BUTTONS = (AppiumBy.ACCESSIBILITY_ID, "Buttons")
    BUTTONS_NAVIGATION_BAR = (
        AppiumBy.IOS_PREDICATE,
        "type == 'XCUIElementTypeNavigationBar' AND name == 'Buttons'",
    )

    def wait_until_loaded(self) -> None:
        self.wait_visible(self.BUTTONS)

    def open_buttons(self) -> None:
        self.tap(self.BUTTONS)

    def buttons_example_is_visible(self) -> bool:
        return self.is_visible(self.BUTTONS_NAVIGATION_BAR, timeout=8)
