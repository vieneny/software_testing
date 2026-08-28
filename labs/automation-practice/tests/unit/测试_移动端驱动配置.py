from __future__ import annotations

from dataclasses import replace
from pathlib import Path

import pytest

# 这组测试验证真实 Appium Options；未安装 mobile extra 时跳过整个模块。
# 离线 Mock/Contract 测试不能因为同目录存在真实适配器测试而被阻断。
pytest.importorskip("appium", reason="install the mobile extra to test real Appium options")

from qa_learning.mobile.移动端驱动工厂 import (
    ANDROID_API_DEMOS_ACTIVITY,
    ANDROID_API_DEMOS_PACKAGE,
    IOS_UIKIT_CATALOG_BUNDLE_ID,
    MobileConfigurationError,
    build_mobile_options,
)
from qa_learning.运行配置 import Settings


def test_android_api_demos_profile_builds_explicit_capabilities(tmp_path) -> None:
    apk = tmp_path / "ApiDemos.apk"
    apk.touch()
    settings = replace(
        Settings.from_env(),
        mobile_platform="android",
        mobile_app_profile="api_demos",
        mobile_app=apk,
        mobile_udid="synthetic-device-id",
    )

    capabilities = build_mobile_options(settings).to_capabilities()

    assert capabilities["platformName"] == "Android"
    assert capabilities["automationName"].lower() == "uiautomator2"
    assert capabilities["appium:appPackage"] == ANDROID_API_DEMOS_PACKAGE
    assert capabilities["appium:appActivity"] == ANDROID_API_DEMOS_ACTIVITY
    assert capabilities["appium:udid"] == "synthetic-device-id"


def test_android_real_device_requires_udid(tmp_path) -> None:
    apk = tmp_path / "ApiDemos.apk"
    apk.touch()
    settings = replace(
        Settings.from_env(),
        mobile_platform="android",
        mobile_app_profile="api_demos",
        mobile_app=apk,
        mobile_udid=None,
    )

    with pytest.raises(MobileConfigurationError, match="MOBILE_UDID"):
        build_mobile_options(settings)


def test_ios_uikit_catalog_profile_builds_simulator_capabilities(tmp_path) -> None:
    simulator_zip = tmp_path / "UIKitCatalog-iphonesimulator.zip"
    simulator_zip.touch()
    settings = replace(
        Settings.from_env(),
        mobile_platform="ios",
        mobile_app_profile="uikit_catalog",
        mobile_app=simulator_zip,
        mobile_udid="synthetic-simulator-id",
        mobile_platform_version="26.5",
    )

    capabilities = build_mobile_options(settings).to_capabilities()

    assert capabilities["platformName"] == "iOS"
    assert capabilities["automationName"] == "XCUITest"
    assert capabilities["appium:bundleId"] == IOS_UIKIT_CATALOG_BUNDLE_ID
    assert capabilities["appium:udid"] == "synthetic-simulator-id"
    assert capabilities["appium:platformVersion"] == "26.5"


def test_relative_mobile_app_path_is_rejected(tmp_path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("MOBILE_APP", raising=False)
    settings = replace(
        Settings.from_env(),
        mobile_platform="android",
        mobile_app_profile="api_demos",
        mobile_app=Path("relative.apk"),
        mobile_udid="synthetic-device-id",
    )

    with pytest.raises(MobileConfigurationError, match="absolute path"):
        build_mobile_options(settings)
