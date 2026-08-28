"""Reusable API automation building blocks for the public learning labs."""

from qa_learning.api.公开占位文章接口 import JsonPlaceholderApi
from qa_learning.api.公开预订服务接口 import RestfulBookerApi
from qa_learning.api.接口客户端 import ApiClient
from qa_learning.api.本地演示商城接口 import DemoShopApi

__all__ = [
    "ApiClient",
    "DemoShopApi",
    "JsonPlaceholderApi",
    "RestfulBookerApi",
]
