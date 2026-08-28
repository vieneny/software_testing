"""Opt-in, low-frequency exercises against Playwright's TodoMVC demo."""

from __future__ import annotations

import re

import pytest
from playwright.sync_api import Browser, Page, expect

from qa_learning.web.pages import TodoMVCPage
from qa_learning.web.浏览器练习目标 import TodoMVCTarget
from qa_learning.运行配置 import Settings

pytestmark = [pytest.mark.web, pytest.mark.external]


@pytest.fixture(scope="session")
def todo_target(settings: Settings) -> TodoMVCTarget:
    return TodoMVCTarget(base_url=settings.todo_mvc_url)


@pytest.mark.challenge
def test_todo_crud_journey(
    page: Page,
    public_web_guard: None,
    todo_target: TodoMVCTarget,
) -> None:
    """Progress from raw interactions to a behavior-oriented page object."""

    todos = TodoMVCPage(page, todo_target)
    todos.open()

    todos.add("学习 Playwright")
    expect(todos.titles).to_have_text(["学习 Playwright"])

    todos.edit("学习 Playwright", "完成 Playwright Page Object")
    expect(todos.titles).to_have_text(["完成 Playwright Page Object"])

    todos.delete("完成 Playwright Page Object")
    expect(todos.items).to_have_count(0)


@pytest.mark.parametrize(
    "invalid_title",
    [
        pytest.param("", id="empty"),
        pytest.param("   ", id="whitespace-only"),
    ],
)
@pytest.mark.challenge
def test_empty_todo_is_not_created(
    page: Page,
    public_web_guard: None,
    todo_target: TodoMVCTarget,
    invalid_title: str,
) -> None:
    todos = TodoMVCPage(page, todo_target)
    todos.open()

    todos.add(invalid_title)

    expect(todos.items).to_have_count(0)


@pytest.mark.smoke
def test_todo_filters_and_remaining_count(
    page: Page,
    public_web_guard: None,
    todo_target: TodoMVCTarget,
) -> None:
    todos = TodoMVCPage(page, todo_target)
    todos.open()
    todos.add_many(
        [
            "学习语义化定位",
            "学习自动等待",
            "查看失败 Trace",
        ]
    )

    todos.complete("学习自动等待")
    expect(todos.remaining_count).to_have_text(re.compile(r"^2 items? left$"))

    todos.filter_by("Completed")
    expect(todos.titles).to_have_text(["学习自动等待"])

    todos.filter_by("Active")
    expect(todos.titles).to_have_text(["学习语义化定位", "查看失败 Trace"])

    todos.filter_by("All")
    expect(todos.titles).to_have_text(["学习语义化定位", "学习自动等待", "查看失败 Trace"])


@pytest.mark.challenge
def test_mark_all_and_clear_completed(
    page: Page,
    public_web_guard: None,
    todo_target: TodoMVCTarget,
) -> None:
    todos = TodoMVCPage(page, todo_target)
    todos.open()
    todos.add_many(["任务一", "任务二", "任务三"])

    todos.mark_all_complete()
    expect(todos.remaining_count).to_have_text(re.compile(r"^0 items? left$"))

    todos.clear_completed()
    expect(todos.items).to_have_count(0)


@pytest.mark.challenge
def test_storage_persists_on_reload_but_not_across_contexts(
    browser: Browser,
    public_web_guard: None,
    todo_target: TodoMVCTarget,
) -> None:
    """A reload keeps localStorage; a fresh BrowserContext must not."""

    first_context = browser.new_context()
    second_context = browser.new_context()
    try:
        first_page = first_context.new_page()
        first_todos = TodoMVCPage(first_page, todo_target)
        first_todos.open()
        first_todos.add("只属于第一个浏览器上下文")
        first_page.reload()
        expect(first_todos.titles).to_have_text(["只属于第一个浏览器上下文"])

        second_page = second_context.new_page()
        second_todos = TodoMVCPage(second_page, todo_target)
        second_todos.open()
        expect(second_todos.items).to_have_count(0)
    finally:
        first_context.close()
        second_context.close()
