"""Page object for the Playwright TodoMVC demonstration."""

from __future__ import annotations

import re
from collections.abc import Iterable

from playwright.sync_api import Locator, Page, expect

from qa_learning.web.浏览器练习目标 import TodoMVCTarget


class TodoMVCPage:
    """Express TodoMVC behavior without hiding Playwright's locators.

    The methods model user intent (add, edit, complete, filter) rather than
    exposing generic ``click(selector)`` wrappers.  Assertions that describe a
    test's expected business result remain in the tests.
    """

    def __init__(
        self,
        page: Page,
        target: TodoMVCTarget | None = None,
    ) -> None:
        self.page = page
        self.target = target or TodoMVCTarget()
        self.new_todo = page.get_by_placeholder("What needs to be done?")
        self.items = page.get_by_test_id("todo-item")
        self.titles = page.get_by_test_id("todo-title")
        self.remaining_count = page.get_by_test_id("todo-count")

    def open(self) -> None:
        self.page.goto(
            self.target.base_url,
            wait_until="domcontentloaded",
        )
        expect(self.page.get_by_role("heading", name="todos")).to_be_visible()
        expect(self.new_todo).to_be_editable()

    def add(self, text: str) -> None:
        self.new_todo.fill(text)
        self.new_todo.press("Enter")

    def add_many(self, titles: Iterable[str]) -> None:
        for title in titles:
            self.add(title)

    def item(self, title: str) -> Locator:
        exact_title = re.compile(rf"^{re.escape(title)}$")
        title_locator = self.page.get_by_test_id("todo-title").filter(has_text=exact_title)
        return self.items.filter(has=title_locator)

    def complete(self, title: str) -> None:
        self.item(title).get_by_label("Toggle Todo").check()

    def reopen(self, title: str) -> None:
        self.item(title).get_by_label("Toggle Todo").uncheck()

    def edit(self, old_title: str, new_title: str) -> None:
        item = self.item(old_title)
        item.get_by_test_id("todo-title").dblclick()
        editor = item.locator("input.edit")
        expect(editor).to_be_visible()
        editor.fill(new_title)
        editor.press("Enter")

    def cancel_edit(self, title: str, draft: str) -> None:
        item = self.item(title)
        item.get_by_test_id("todo-title").dblclick()
        editor = item.locator("input.edit")
        expect(editor).to_be_visible()
        editor.fill(draft)
        editor.press("Escape")

    def delete(self, title: str) -> None:
        item = self.item(title)
        item.hover()
        item.get_by_label("Delete").click()

    def filter_by(self, name: str) -> None:
        if name not in {"All", "Active", "Completed"}:
            raise ValueError(f"unsupported TodoMVC filter: {name}")
        self.page.get_by_role("link", name=name, exact=True).click()

    def mark_all_complete(self) -> None:
        self.page.get_by_label("Mark all as complete").check()

    def clear_completed(self) -> None:
        self.page.get_by_role("button", name="Clear completed").click()
