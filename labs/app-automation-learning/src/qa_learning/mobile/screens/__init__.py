"""Page objects for public Android and iOS learning applications."""

from qa_learning.mobile.screens.安卓组件演示页面 import ApiDemosHomeScreen
from qa_learning.mobile.screens.苹果界面组件页面 import UIKitCatalogScreen
from qa_learning.mobile.screens.跨端演示商城页面 import (
    AndroidMyDemoApp,
    IosMyDemoApp,
)

__all__ = [
    "AndroidMyDemoApp",
    "ApiDemosHomeScreen",
    "IosMyDemoApp",
    "UIKitCatalogScreen",
]
