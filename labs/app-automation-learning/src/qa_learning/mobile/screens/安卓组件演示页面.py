"""Page object for Appium's Apache-2.0 Android ApiDemos app."""

from appium.webdriver.common.appiumby import AppiumBy

from qa_learning.mobile.screens.移动端基础页面 import BaseScreen


class ApiDemosHomeScreen(BaseScreen):
    APP = (AppiumBy.ACCESSIBILITY_ID, "App")
    ACTIVITY = (AppiumBy.ACCESSIBILITY_ID, "Activity")

    def wait_until_loaded(self) -> None:
        self.wait_visible(self.APP)

    def open_activity_examples(self) -> None:
        self.tap(self.APP)
        self.tap(self.ACTIVITY)

    def activity_examples_are_visible(self) -> bool:
        return self.is_visible((AppiumBy.ACCESSIBILITY_ID, "Custom Title"), timeout=5)
