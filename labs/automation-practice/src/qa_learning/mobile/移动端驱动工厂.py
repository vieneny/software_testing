"""Create Appium 3 sessions from the repository's explicit mobile settings.

The factory deliberately accepts only the three public learning profiles used
by this repository.  It never scans attached devices and never guesses an app
from the current directory.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import TypeAlias

from appium import webdriver
from appium.options.android import UiAutomator2Options
from appium.options.ios import XCUITestOptions
from appium.webdriver.webdriver import WebDriver

from qa_learning.运行配置 import Settings

MobileOptions: TypeAlias = UiAutomator2Options | XCUITestOptions

ANDROID_API_DEMOS_PACKAGE = "io.appium.android.apis"
ANDROID_API_DEMOS_ACTIVITY = "io.appium.android.apis.ApiDemos"
IOS_UIKIT_CATALOG_BUNDLE_ID = "com.example.apple-samplecode.UICatalog"

_PROFILES_BY_PLATFORM = {
    "android": {"api_demos", "my_demo_app"},
    "ios": {"my_demo_app", "uikit_catalog"},
}


class MobileConfigurationError(ValueError):
    """Raised before Appium is contacted when mobile settings are unsafe."""


def _validated_app_path(settings: Settings) -> Path:
    raw_app = os.getenv("MOBILE_APP")
    if raw_app and not Path(raw_app).expanduser().is_absolute():
        raise MobileConfigurationError(
            "MOBILE_APP must be an absolute path; relative app paths are refused"
        )

    app = settings.mobile_app
    if app is None:
        raise MobileConfigurationError(
            "MOBILE_APP is required and must point to the selected public demo build"
        )
    if not app.is_absolute():
        raise MobileConfigurationError(
            "MOBILE_APP must be an absolute path; relative app paths are refused"
        )
    if not app.exists():
        raise MobileConfigurationError(f"MOBILE_APP does not exist: {app}")
    return app


def _validate_target(settings: Settings) -> tuple[str, str, Path]:
    platform = settings.mobile_platform.strip().lower()
    profile = settings.mobile_app_profile.strip().lower()
    if platform not in _PROFILES_BY_PLATFORM:
        raise MobileConfigurationError(
            f"unsupported MOBILE_PLATFORM={platform!r}; choose 'android' or 'ios'"
        )
    if profile not in _PROFILES_BY_PLATFORM[platform]:
        supported = ", ".join(sorted(_PROFILES_BY_PLATFORM[platform]))
        raise MobileConfigurationError(
            f"profile {profile!r} is not supported on {platform}; choose: {supported}"
        )

    app = _validated_app_path(settings)
    suffixes = "".join(app.suffixes).lower()
    if platform == "android" and not suffixes.endswith(".apk"):
        raise MobileConfigurationError("Android MOBILE_APP must be an .apk file")
    if platform == "ios" and not suffixes.endswith((".app", ".app.zip", ".zip", ".ipa")):
        raise MobileConfigurationError(
            "iOS MOBILE_APP must be an .app, .app.zip, .zip or .ipa build"
        )
    return platform, profile, app


def build_mobile_options(settings: Settings) -> MobileOptions:
    """Build platform options without opening a network or device session."""

    platform, profile, app = _validate_target(settings)
    if platform == "android":
        if not settings.mobile_udid:
            raise MobileConfigurationError(
                "Android real-device runs require MOBILE_UDID; deviceName does not select a device"
            )
        options = UiAutomator2Options()
        package, activity = (
            (ANDROID_API_DEMOS_PACKAGE, ANDROID_API_DEMOS_ACTIVITY)
            if profile == "api_demos"
            else (settings.android_app_package, settings.android_app_activity)
        )
        capabilities: dict[str, object] = {
            "platformName": "Android",
            "deviceName": settings.mobile_device_name,
            "udid": settings.mobile_udid,
            "app": str(app),
            "appPackage": package,
            "appActivity": activity,
            "autoGrantPermissions": False,
            "noReset": False,
            "newCommandTimeout": 120,
        }
    else:
        options = XCUITestOptions()
        capabilities = {
            "platformName": "iOS",
            "deviceName": settings.ios_device_name or settings.mobile_device_name,
            "app": str(app),
            "bundleId": (
                IOS_UIKIT_CATALOG_BUNDLE_ID
                if profile == "uikit_catalog"
                else settings.ios_bundle_id
            ),
            "autoAcceptAlerts": False,
            "noReset": False,
            "newCommandTimeout": 120,
            "shouldTerminateApp": True,
        }
        if settings.mobile_udid:
            capabilities["udid"] = settings.mobile_udid

    if settings.mobile_platform_version:
        capabilities["platformVersion"] = settings.mobile_platform_version
    options.load_capabilities(capabilities)
    return options


def create_mobile_driver(settings: Settings) -> WebDriver:
    """Validate settings, then create exactly one Appium session."""

    return webdriver.Remote(
        command_executor=settings.appium_server_url,
        options=build_mobile_options(settings),
    )
