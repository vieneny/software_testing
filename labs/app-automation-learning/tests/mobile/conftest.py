"""Collection and lifecycle safety for opt-in real-device tests.

Only tests marked ``device`` are guarded by ``--run-mobile``.  This distinction
is intentional: offline Mock/contract tests are mobile tests too, but they must
remain runnable without Appium, a server, or an attached phone.
"""

from __future__ import annotations

from collections.abc import Callable, Iterator
from typing import TYPE_CHECKING

import pytest

from qa_learning.运行配置 import Settings

if TYPE_CHECKING:
    from appium.webdriver.webdriver import WebDriver


def pytest_collection_modifyitems(
    config: pytest.Config,
    items: list[pytest.Item],
) -> None:
    if config.getoption("--run-mobile"):
        return

    skip_device = pytest.mark.skip(
        reason="real-device tests require the explicit --run-mobile switch"
    )
    for item in items:
        if item.get_closest_marker("device") is not None:
            item.add_marker(skip_device)


@pytest.fixture
def mobile_driver_factory(
    mobile_guard: None,
    settings: Settings,
) -> Iterator[Callable[[], WebDriver]]:
    """Create on demand so a platform mismatch can skip before device access."""

    drivers: list[WebDriver] = []

    def factory() -> WebDriver:
        from qa_learning.mobile import create_mobile_driver

        driver = create_mobile_driver(settings)
        drivers.append(driver)
        return driver

    yield factory

    cleanup_errors: list[Exception] = []
    for driver in reversed(drivers):
        try:
            driver.quit()
        except Exception as exc:  # pragma: no cover - requires a broken external driver
            # One bad Appium session must not prevent the remaining sessions from closing.
            cleanup_errors.append(exc)
    if cleanup_errors:
        raise RuntimeError(
            f"{len(cleanup_errors)} mobile session(s) failed to close; "
            f"first error: {cleanup_errors[0]}"
        ) from cleanup_errors[0]
