from __future__ import annotations

import pytest

from qa_learning.运行配置 import Settings


def pytest_addoption(parser: pytest.Parser) -> None:
    parser.getgroup("mobile-learning").addoption(
        "--run-mobile",
        action="store_true",
        default=False,
        help="control the explicitly configured mobile target",
    )


@pytest.fixture(scope="session")
def settings() -> Settings:
    return Settings.from_env()
