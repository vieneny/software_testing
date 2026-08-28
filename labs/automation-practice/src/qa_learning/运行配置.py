from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


def _optional_path(value: str | None) -> Path | None:
    if not value:
        return None
    return Path(value).expanduser().resolve()


@dataclass(frozen=True)
class Settings:
    """Environment-backed settings with safe public defaults."""

    jsonplaceholder_url: str
    restful_booker_url: str
    todo_mvc_url: str
    sauce_demo_url: str
    sauce_username: str
    sauce_password: str
    appium_server_url: str
    mobile_platform: str
    mobile_app_profile: str
    mobile_device_name: str
    mobile_udid: str | None
    mobile_platform_version: str | None
    mobile_app: Path | None
    android_app_package: str
    android_app_activity: str
    ios_bundle_id: str
    ios_device_name: str

    @classmethod
    def from_env(cls) -> Settings:
        load_dotenv()
        return cls(
            jsonplaceholder_url=os.getenv(
                "JSONPLACEHOLDER_URL", "https://jsonplaceholder.typicode.com"
            ).rstrip("/"),
            restful_booker_url=os.getenv(
                "RESTFUL_BOOKER_URL", "https://restful-booker.herokuapp.com"
            ).rstrip("/"),
            todo_mvc_url=os.getenv("TODO_MVC_URL", "https://demo.playwright.dev/todomvc/"),
            sauce_demo_url=os.getenv("SAUCE_DEMO_URL", "https://www.saucedemo.com/"),
            sauce_username=os.getenv("SAUCE_USERNAME", "standard_user"),
            sauce_password=os.getenv("SAUCE_PASSWORD", "secret_sauce"),
            appium_server_url=os.getenv("APPIUM_SERVER_URL", "http://127.0.0.1:4723"),
            mobile_platform=os.getenv("MOBILE_PLATFORM", "android").strip().lower(),
            mobile_app_profile=os.getenv("MOBILE_APP_PROFILE", "api_demos").strip().lower(),
            mobile_device_name=os.getenv("MOBILE_DEVICE_NAME", "Android"),
            mobile_udid=os.getenv("MOBILE_UDID") or None,
            mobile_platform_version=os.getenv("MOBILE_PLATFORM_VERSION") or None,
            mobile_app=_optional_path(os.getenv("MOBILE_APP")),
            android_app_package=os.getenv("ANDROID_APP_PACKAGE", "com.saucelabs.mydemoapp.android"),
            android_app_activity=os.getenv(
                "ANDROID_APP_ACTIVITY",
                "com.saucelabs.mydemoapp.android.view.activities.SplashActivity",
            ),
            ios_bundle_id=os.getenv("IOS_BUNDLE_ID", "com.saucelabs.mydemo.app.ios"),
            ios_device_name=os.getenv("IOS_DEVICE_NAME", "iPhone 17 Pro"),
        )
