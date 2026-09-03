"""Minimal deterministic smoke test for Appium's UIKitCatalog."""

from collections.abc import Callable

import pytest

from qa_learning.运行配置 import Settings

pytestmark = [pytest.mark.mobile, pytest.mark.ios, pytest.mark.device]


@pytest.mark.smoke
def test_uikit_catalog_opens_buttons_example(
    mobile_guard: None,
    settings: Settings,
    mobile_driver_factory: Callable[[], object],
) -> None:
    if settings.mobile_platform != "ios" or settings.mobile_app_profile != "uikit_catalog":
        pytest.skip("requires MOBILE_PLATFORM=ios and MOBILE_APP_PROFILE=uikit_catalog")

    pytest.importorskip("appium", reason="install the mobile extra to run device tests")
    from qa_learning.mobile.screens import UIKitCatalogScreen

    catalog = UIKitCatalogScreen(mobile_driver_factory())
    catalog.wait_until_loaded()
    catalog.open_buttons()

    assert catalog.buttons_example_is_visible()
