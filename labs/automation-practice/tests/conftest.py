from __future__ import annotations

import pytest

from qa_learning.运行配置 import Settings


def pytest_addoption(parser: pytest.Parser) -> None:
    group = parser.getgroup("public-learning-targets")
    group.addoption(
        "--run-public-api",
        action="store_true",
        default=False,
        help="allow low-frequency tests against public API learning services",
    )
    group.addoption(
        "--run-public-web",
        action="store_true",
        default=False,
        help="allow low-frequency tests against public Web learning services",
    )
    group.addoption(
        "--run-mobile",
        action="store_true",
        default=False,
        help="allow tests to control the explicitly configured test device/simulator",
    )


@pytest.fixture(scope="session")
def settings() -> Settings:
    return Settings.from_env()


@pytest.fixture(scope="session")
def public_api_guard(request: pytest.FixtureRequest) -> None:
    if not request.config.getoption("--run-public-api"):
        pytest.skip("public API tests require the explicit --run-public-api switch")


@pytest.fixture(scope="session")
def public_web_guard(request: pytest.FixtureRequest) -> None:
    if not request.config.getoption("--run-public-web"):
        pytest.skip("public Web tests require the explicit --run-public-web switch")


@pytest.fixture(scope="session")
def mobile_guard(request: pytest.FixtureRequest) -> None:
    if not request.config.getoption("--run-mobile"):
        pytest.skip("mobile tests require the explicit --run-mobile switch")
