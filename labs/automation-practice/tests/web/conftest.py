"""Collection-time safety guard for public Web exercises.

The root ``public_web_guard`` fixture remains the explicit runtime contract.
Adding the skip marker during collection also prevents pytest-playwright from
launching a browser before a same-scoped guard fixture gets a chance to skip.
"""

from __future__ import annotations

from pathlib import Path

import pytest


def pytest_collection_modifyitems(
    config: pytest.Config,
    items: list[pytest.Item],
) -> None:
    if config.getoption("--run-public-web"):
        return

    skip_public_web = pytest.mark.skip(
        reason="public Web tests require the explicit --run-public-web switch"
    )
    web_tests = Path(__file__).parent.resolve()
    for item in items:
        if Path(str(item.path)).resolve().is_relative_to(web_tests):
            item.add_marker(skip_public_web)
