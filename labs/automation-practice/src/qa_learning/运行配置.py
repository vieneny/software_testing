from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv


@dataclass(frozen=True)
class Settings:
    """Environment-backed settings for the API and Web practice targets."""

    jsonplaceholder_url: str
    restful_booker_url: str
    todo_mvc_url: str
    sauce_demo_url: str
    sauce_username: str
    sauce_password: str

    @classmethod
    def from_env(cls) -> Settings:
        load_dotenv()
        return cls(
            jsonplaceholder_url=os.getenv(
                "JSONPLACEHOLDER_URL", "https://jsonplaceholder.typicode.com"
            ).rstrip("/"),
            restful_booker_url=os.getenv(
                "RESTFUL_BOOKER_URL", "https://restful-booker.herokuapp.com"
            ).rstrip("/"),
            todo_mvc_url=os.getenv("TODO_MVC_URL", "https://demo.playwright.dev/todomvc/"),
            sauce_demo_url=os.getenv("SAUCE_DEMO_URL", "https://www.saucedemo.com/"),
            sauce_username=os.getenv("SAUCE_USERNAME", "standard_user"),
            sauce_password=os.getenv("SAUCE_PASSWORD", "secret_sauce"),
        )
