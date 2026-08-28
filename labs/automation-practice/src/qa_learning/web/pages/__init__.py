"""Page objects for the public Web automation exercises."""

from qa_learning.web.pages.待办事项页面 import TodoMVCPage
from qa_learning.web.pages.演示商城页面 import (
    SauceCartPage,
    SauceCheckoutPage,
    SauceInventoryPage,
    SauceLoginPage,
)

__all__ = [
    "SauceCartPage",
    "SauceCheckoutPage",
    "SauceInventoryPage",
    "SauceLoginPage",
    "TodoMVCPage",
]
