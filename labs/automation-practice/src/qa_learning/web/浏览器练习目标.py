"""Configuration for public Web practice targets.

Only intentionally public demo credentials are represented here.  Environment
variables let learners point the same framework at a self-hosted copy without
editing test code.  Do not put private credentials in this module.
"""

from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class TodoMVCTarget:
    """Microsoft Playwright's public TodoMVC demonstration."""

    base_url: str = os.getenv(
        "TODO_MVC_URL",
        os.getenv(
            "TODO_MVC_BASE_URL",
            "https://demo.playwright.dev/todomvc/",
        ),
    )


@dataclass(frozen=True, slots=True)
class SauceDemoTarget:
    """Sauce Labs' public shopping demonstration."""

    base_url: str = os.getenv(
        "SAUCE_DEMO_URL",
        os.getenv(
            "SAUCE_DEMO_BASE_URL",
            "https://www.saucedemo.com/",
        ),
    )
    standard_username: str = os.getenv(
        "SAUCE_USERNAME",
        os.getenv(
            "SAUCE_DEMO_STANDARD_USERNAME",
            "standard_user",
        ),
    )
    locked_username: str = os.getenv(
        "SAUCE_DEMO_LOCKED_USERNAME",
        "locked_out_user",
    )
    password: str = os.getenv(
        "SAUCE_PASSWORD",
        os.getenv(
            "SAUCE_DEMO_PASSWORD",
            "secret_sauce",
        ),
    )
