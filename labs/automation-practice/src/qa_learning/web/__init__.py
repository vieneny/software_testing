"""Reusable Playwright page objects and flows for public Web practice sites.

The public-site tests that use this package are opt-in.  Importing the package
does not access the network.
"""

from qa_learning.web.浏览器练习目标 import SauceDemoTarget, TodoMVCTarget

__all__ = ["SauceDemoTarget", "TodoMVCTarget"]
