"""Android cart smoke against Sauce Labs My Demo App."""

from collections.abc import Callable

import pytest

from qa_learning.运行配置 import Settings

pytestmark = [pytest.mark.mobile, pytest.mark.android, pytest.mark.device]


@pytest.mark.smoke
def test_android_user_adds_first_product_to_cart(
    mobile_guard: None,
    settings: Settings,
    mobile_driver_factory: Callable[[], object],
) -> None:
    if settings.mobile_platform != "android" or settings.mobile_app_profile != "my_demo_app":
        pytest.skip("requires MOBILE_PLATFORM=android and MOBILE_APP_PROFILE=my_demo_app")

    pytest.importorskip("appium", reason="install the mobile extra to run device tests")
    from qa_learning.mobile.screens import AndroidMyDemoApp

    app = AndroidMyDemoApp(mobile_driver_factory())
    app.wait_for_catalog()
    app.open_first_product()
    app.add_one_to_cart()
    app.open_cart()

    assert app.cart_has_item()
