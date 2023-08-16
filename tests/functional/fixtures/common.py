import asyncio
import os
import sys
from typing import Optional

import aiohttp
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
import pytest

current = os.path.dirname(os.path.realpath(__file__))
sys.path.append(current)

from settings import test_settings, user_db_settings


@pytest.fixture(scope='session', autouse=True)
def event_loop():
    """Overrides pytest default function scoped event loop"""
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope='function', autouse=True)
def db_engine():
    engine = create_engine(user_db_settings.url, echo=False)

    yield engine

    engine.dispose()


@pytest.fixture(scope='function', autouse=True)
def db_session_factory(db_engine):
    return scoped_session(sessionmaker(bind=db_engine))


@pytest.fixture(scope='function', autouse=True)
def db_session(db_session_factory):
    session = db_session_factory()

    yield session

    session.rollback()
    session.close()


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
        try:
            async with session.get(url, params=query_data) as response:
                body = await response.json()
                status = response.status

        finally:
            await session.close()
        return status, body

    return inner


@pytest.fixture(scope='session', autouse=True)
def make_post_request():
    async def inner(api_postfix: str,
                    endpoint: Optional[str] = None,
                    query_data: Optional[dict] = None,
                    access_token: Optional[str] = None,
                    refresh_token: Optional[str] = None):
        headers = dict()
        if access_token:
            headers.update({"Authorization": f"Bearer {access_token}"})
        if refresh_token:
            headers.update({"Cookie": f"refresh_token={refresh_token}"})
        if headers:
            session = aiohttp.ClientSession(headers=headers)
        else:
            session = aiohttp.ClientSession()
        url = test_settings.service_url + api_postfix + (endpoint or '')
        try:
            async with session.post(url, json=query_data) as response:
                body = await response.json()
                status = response.status
                if response.cookies:
                    refresh_token = response.cookies.get("refresh_token")
                    return status, body, refresh_token.value

        finally:
            await session.close()
        return status, body, None

    return inner


@pytest.fixture(scope='session', autouse=True)
def make_patch_request():
    async def inner(api_postfix: str,
                    endpoint: Optional[str] = None,
                    query_data: Optional[dict] = None,
                    params: Optional[dict] = None,
                    token: Optional[str] = None):
        if token:
            headers = {"Authorization": f"Bearer {token}"}
            session = aiohttp.ClientSession(headers=headers)
        else:
            session = aiohttp.ClientSession()
        url = test_settings.service_url + api_postfix + (endpoint or '')
        try:
            async with session.patch(url, json=query_data, params=params) as response:
                body = await response.json()
                status = response.status

        finally:
            await session.close()
        return status, body

    return inner


@pytest.fixture(scope='session', autouse=True)
def make_delete_request():
    async def inner(api_postfix: str,
                    endpoint: Optional[str] = None,
                    query_data: Optional[dict] = None,
                    params: Optional[dict] = None,
                    token: Optional[str] = None):
        if token:
            headers = {"Authorization": f"Bearer {token}"}
            session = aiohttp.ClientSession(headers=headers)
        else:
            session = aiohttp.ClientSession()
        url = test_settings.service_url + api_postfix + (endpoint or '')
        try:
            async with session.delete(url, params=params, json=query_data) as response:
                body = await response.json()
                status = response.status

        finally:
            await session.close()
        return status, body

    return inner
