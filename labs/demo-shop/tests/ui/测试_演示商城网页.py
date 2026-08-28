from __future__ import annotations

import os
import re

import pytest
from playwright.sync_api import Page, expect


@pytest.mark.ui
def test_user_can_buy_first_product(page: Page) -> None:
    base_url = os.getenv("DEMO_BASE_URL", "http://127.0.0.1:8000")

    page.goto(base_url)

    expect(page.get_by_role("heading", name="Demo Shop")).to_be_visible()
    expect(page.get_by_role("status")).to_contain_text("已加载")
    page.get_by_role("button", name=re.compile(r"^购买 ")).first.click()
    expect(page.get_by_role("status")).to_contain_text("订单创建成功")
