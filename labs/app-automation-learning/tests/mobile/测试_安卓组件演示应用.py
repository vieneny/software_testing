"""Minimal deterministic smoke test for Appium's Android ApiDemos."""

from collections.abc import Callable

import pytest

from qa_learning.运行配置 import Settings

pytestmark = [pytest.mark.mobile, pytest.mark.android, pytest.mark.device]


@pytest.mark.smoke
def test_api_demos_opens_activity_examples(
    mobile_guard: None,
    settings: Settings,
    mobile_driver_factory: Callable[[], object],
) -> None:
    if settings.mobile_platform != "android" or settings.mobile_app_profile != "api_demos":
        pytest.skip("requires MOBILE_PLATFORM=android and MOBILE_APP_PROFILE=api_demos")

    pytest.importorskip("appium", reason="install the mobile extra to run device tests")
    from qa_learning.mobile.screens import ApiDemosHomeScreen

    home = ApiDemosHomeScreen(mobile_driver_factory())
    home.wait_until_loaded()
    home.open_activity_examples()

    assert home.activity_examples_are_visible()
