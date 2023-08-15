import asyncio
import os
import sys
from http import HTTPStatus
from typing import Optional

import aiohttp
import pytest

current = os.path.dirname(os.path.realpath(__file__))
sys.path.append(current)

from settings import test_settings


@pytest.fixture(scope='session', autouse=True)
def event_loop():
    """Overrides pytest default function scoped event loop"""
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope='session', autouse=True)
def make_get_request():
    async def inner(api_postfix: str,
                    endpoint: Optional[str] = None,
                    query_data: Optional[dict] = None,
                    token: Optional[str] = None):
        if token:
            headers = {"Authorization": f"Bearer {token}"}
            session = aiohttp.ClientSession(headers=headers)
        else:
            session = aiohttp.ClientSession()
        url = test_settings.service_url + api_postfix + (endpoint or '')
        async with session.get(url, params=query_data) as response:
            body = await response.json()
            status = response.status

        await session.close()
        return status, body

    return inner


@pytest.fixture(scope='session', autouse=True)
def make_post_request():
    async def inner(api_postfix: str,
                    endpoint: Optional[str] = None,
                    query_data: Optional[dict] = None,
                    token: Optional[str] = None):
        if token:
            headers = {"Authorization": f"Bearer {token}"}
            session = aiohttp.ClientSession(headers=headers)
        else:
            session = aiohttp.ClientSession()
        url = test_settings.service_url + api_postfix + (endpoint or '')
        async with session.post(url, json=query_data) as response:
            body = await response.json()
            status = response.status

        await session.close()
        return status, body

    return inner


@pytest.fixture(scope="session", autouse=True)
def login_to_get_token():
    async def inner():
        status_login, token = await make_post_request(api_postfix="/api/v1/auth",
                                                      endpoint="/login",
                                                      query_data={
                                                          "login": "new_user_",
                                                          "password": "123qwe"
                                                      })
        assert status_login == HTTPStatus.OK
        return token

    return inner
