"""Mobile learning entry points.

The real Appium symbols are loaded only when they are requested.  Importing
``qa_learning.mobile.mock`` therefore remains possible with the base project
dependencies alone: an offline lesson must not require the Appium client just
because both implementations share this parent package.
"""

from __future__ import annotations

from typing import Any

__all__ = ["MobileConfigurationError", "create_mobile_driver"]


def __getattr__(name: str) -> Any:
    """Lazily expose real-device helpers without coupling Mock to Appium."""

    if name in __all__:
        from qa_learning.mobile.移动端驱动工厂 import (
            MobileConfigurationError,
            create_mobile_driver,
        )

        exports = {
            "MobileConfigurationError": MobileConfigurationError,
            "create_mobile_driver": create_mobile_driver,
        }
        return exports[name]
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
