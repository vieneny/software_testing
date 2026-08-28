from __future__ import annotations

from uuid import uuid4

import pytest

from qa_learning.api.公开占位文章接口 import JsonPlaceholderApi
from qa_learning.api.响应数据契约 import (
    JSONPLACEHOLDER_POST_LIST_SCHEMA,
    JSONPLACEHOLDER_POST_SCHEMA,
)
from qa_learning.api.接口客户端 import ApiClient
from qa_learning.运行配置 import Settings


@pytest.mark.api
@pytest.mark.external
@pytest.mark.smoke
def test_jsonplaceholder_filters_posts_for_one_user(
    settings: Settings,
    public_api_guard: None,
) -> None:
    with ApiClient(settings.jsonplaceholder_url) as client:
        api = JsonPlaceholderApi(client)

        response = api.list_posts(user_id=1)

        client.assert_status(response, 200)
        posts = client.assert_json_schema(
            response,
            JSONPLACEHOLDER_POST_LIST_SCHEMA,
        )
        assert posts
        assert {post["userId"] for post in posts} == {1}


@pytest.mark.api
@pytest.mark.external
@pytest.mark.challenge
def test_jsonplaceholder_create_is_only_a_simulated_write(
    settings: Settings,
    public_api_guard: None,
) -> None:
    synthetic_title = f"qa-learning-{uuid4().hex[:10]}"

    with ApiClient(settings.jsonplaceholder_url) as client:
        api = JsonPlaceholderApi(client)

        create_response = api.create_post(
            user_id=1,
            title=synthetic_title,
            body="This is synthetic public learning data.",
        )
        client.assert_status(create_response, 201)
        created = client.assert_json_schema(
            create_response,
            JSONPLACEHOLDER_POST_SCHEMA,
        )
        assert created["title"] == synthetic_title

        query_response = api.get_post(created["id"])
        client.assert_status(query_response, 404)
