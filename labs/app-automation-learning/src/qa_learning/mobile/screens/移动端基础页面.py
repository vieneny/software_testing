"""Stable synchronization, gestures and evidence helpers for mobile screens."""

from __future__ import annotations

from pathlib import Path
from typing import TypeAlias

from appium.webdriver.webdriver import WebDriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait

Locator: TypeAlias = tuple[str, str]


class BaseScreen:
    """Small Page Object base that avoids sleeps and unbounded scrolling."""

    def __init__(self, driver: WebDriver, timeout: float = 15) -> None:
        self.driver = driver
        self.timeout = timeout

    def wait_visible(self, locator: Locator, timeout: float | None = None) -> WebElement:
        return WebDriverWait(self.driver, timeout or self.timeout).until(
            ec.visibility_of_element_located(locator)
        )

    def wait_clickable(self, locator: Locator, timeout: float | None = None) -> WebElement:
        return WebDriverWait(self.driver, timeout or self.timeout).until(
            ec.element_to_be_clickable(locator)
        )

    def tap(self, locator: Locator) -> None:
        self.wait_clickable(locator).click()

    def text(self, locator: Locator) -> str:
        return self.wait_visible(locator).text

    def type_text(self, locator: Locator, value: str) -> None:
        field = self.wait_visible(locator)
        field.clear()
        field.send_keys(value)

    def is_visible(self, locator: Locator, timeout: float = 2) -> bool:
        try:
            self.wait_visible(locator, timeout)
        except TimeoutException:
            return False
        return True

    def wait_until_gone(self, locator: Locator, timeout: float | None = None) -> None:
        WebDriverWait(self.driver, timeout or self.timeout).until(
            ec.invisibility_of_element_located(locator)
        )

    def scroll_until_visible(
        self,
        locator: Locator,
        *,
        direction: str = "down",
        max_swipes: int = 5,
    ) -> WebElement:
        """Find an element with a bounded, platform-native swipe loop."""

        if max_swipes < 0:
            raise ValueError("max_swipes must be zero or greater")
        for attempt in range(max_swipes + 1):
            try:
                return self.wait_visible(locator, timeout=1.5)
            except TimeoutException:
                if attempt == max_swipes:
                    break
                self._swipe(direction)
        raise TimeoutException(f"{locator!r} was not visible after {max_swipes} {direction} swipes")

    def _swipe(self, direction: str) -> None:
        if direction not in {"up", "down", "left", "right"}:
            raise ValueError(f"unsupported swipe direction: {direction}")
        platform = str(self.driver.capabilities.get("platformName", "")).lower()
        if platform == "android":
            rect = self.driver.get_window_rect()
            self.driver.execute_script(
                "mobile: swipeGesture",
                {
                    "left": int(rect["width"] * 0.1),
                    "top": int(rect["height"] * 0.15),
                    "width": int(rect["width"] * 0.8),
                    "height": int(rect["height"] * 0.7),
                    "direction": direction,
                    "percent": 0.7,
                },
            )
            return
        self.driver.execute_script("mobile: swipe", {"direction": direction})

    def save_screenshot(self, target: Path) -> Path:
        """Save a screenshot only to the caller's explicit artifact path."""

        path = target.expanduser().resolve()
        path.parent.mkdir(parents=True, exist_ok=True)
        if not self.driver.save_screenshot(str(path)):
            raise RuntimeError(f"Appium could not save screenshot to {path}")
        return path
