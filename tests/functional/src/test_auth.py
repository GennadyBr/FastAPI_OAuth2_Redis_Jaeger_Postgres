from http import HTTPStatus

import pytest
from jose import jwt


@pytest.mark.parametrize(
    'query_data, expected_answer',
    [
        (
                {
                    "login": "new_user_",
                    "name": "John",
                    "surname": "Doe",
                    "email": "johndoe@example.com",
                    "password": "123qwe"
                },
                {'status': HTTPStatus.OK, 'body': {
                    "login": "new_user_",
                    "name": "John",
                    "surname": "Doe",
                    "email": "johndoe@example.com",
                }}
        )
    ]
)
@pytest.mark.asyncio
async def test_register(make_post_request, query_data, expected_answer):
    status, body, _ = await make_post_request(api_postfix="/api/v1/auth",
                                              endpoint="/register",
                                              query_data=query_data)
    assert status == expected_answer['status']
    assert body == expected_answer['body']


@pytest.mark.parametrize(
    'query_data, expected_answer',
    [
        (
                {
                    "login": "new_user_",
                    "password": "123qwe"
                },
                {'status': HTTPStatus.OK, 'payload_user': "new_user_"}
        )
    ]
)
@pytest.mark.asyncio
async def test_login(make_post_request, query_data, expected_answer, request):
    status_login, token, refresh_token = await make_post_request(api_postfix="/api/v1/auth",
                                                                 endpoint="/login",
                                                                 query_data=query_data)
    assert status_login == expected_answer['status']
    payload = jwt.decode(
        token,
        "qwe",
        algorithms=["HS256"],
        options={"verify_exp": False, },
    )
    assert payload['login'] == expected_answer["payload_user"]
    request.config.cache.set('access_token', token)
    request.config.cache.set('refresh_token', refresh_token)


@pytest.mark.parametrize(
    'query_data, expected_answer',
    [
        (
                {
                    "login": "new_user_",
                    "password": "123qwe"
                },
                {'status': HTTPStatus.OK, 'body': {
                    "login": "new_user_",
                    "name": "John",
                    "surname": "Doe",
                    "email": "johndoe@example.com",
                }}
        )
    ]
)
@pytest.mark.asyncio
async def test_me(make_get_request, query_data, expected_answer, request):
    token = request.config.cache.get('access_token', None)
    status, body = await make_get_request(api_postfix="/api/v1/auth",
                                          endpoint="/me",
                                          token=token)
    assert status == expected_answer['status']
    assert body == expected_answer['body']


@pytest.mark.parametrize(
    'query_data, expected_answer',
    [
        (
                {
                    "login": "new_user_",
                    "password": "123qwe"
                },
                {'status': HTTPStatus.OK, 'len_body': 1}
        )
    ]
)
@pytest.mark.asyncio
async def test_entries(make_get_request, query_data, expected_answer, request):
    token = request.config.cache.get('access_token', None)
    status, body = await make_get_request(api_postfix="/api/v1/auth",
                                          endpoint="/entries",
                                          token=token)
    assert status == expected_answer['status']
    assert len(body) == expected_answer['len_body']


@pytest.mark.parametrize(
    'query_data, expected_answer',
    [
        (
                {
                    "login": "new_user_",
                    "password": "123qwe"
                },
                {'status': HTTPStatus.OK, 'body': []}
        )
    ]
)
@pytest.mark.asyncio
async def test_role(make_get_request, query_data, expected_answer, request):
    token = request.config.cache.get('access_token', None)
    status, body = await make_get_request(api_postfix="/api/v1/auth",
                                          endpoint="/role",
                                          token=token)
    assert status == expected_answer['status']
    assert body == expected_answer['body']


@pytest.mark.parametrize(
    'query_data, expected_answer',
    [
        (
                {
                    "login": "new_login",
                    "name": "John",
                    "surname": "Doe",
                    "email": "johndoe@example.com"
                },
                {'status': HTTPStatus.OK,
                 'body': {
                     'email': 'johndoe@example.com',
                     'login': 'new_login',
                     'name': 'John',
                     'surname': 'Doe'
                 }
                 }
        )
    ]
)
@pytest.mark.asyncio
async def test_change_user_data(make_post_request, query_data, expected_answer, request):
    access_token = request.config.cache.get('access_token', None)
    refresh_token = request.config.cache.get('refresh_token', None)
    status, body, _ = await make_post_request(api_postfix="/api/v1/auth",
                                              endpoint="/change_user_data",
                                              query_data=query_data,
                                              access_token=access_token,
                                              refresh_token=refresh_token)
    assert status == expected_answer['status']
    assert body == expected_answer['body']


@pytest.mark.parametrize(
    'query_data, expected_answer',
    [
        (
                {
                    "login": "new_login",
                    "password": "123qwe"
                },
                {'status': HTTPStatus.OK, 'body': None}
        )
    ]
)
@pytest.mark.asyncio
async def test_logout(make_get_request, query_data, expected_answer, request):
    token = request.config.cache.get('access_token', None)
    status, body = await make_get_request(api_postfix="/api/v1/auth",
                                          endpoint="/logout",
                                          token=token)
    assert status == expected_answer['status']
    assert body == expected_answer['body']


@pytest.mark.parametrize(
    'credentials, expected_answer',
    [
        (
                {
                    "login": "new_login",
                    "password": "123qwe"
                },
                {'status': HTTPStatus.OK, 'body': None}
        )
    ]
)
@pytest.mark.asyncio
async def test_logout_all(make_get_request, make_post_request, credentials, expected_answer):
    status_login, token, _ = await make_post_request(api_postfix="/api/v1/auth",
                                                     endpoint="/login",
                                                     query_data=credentials)
    assert status_login == HTTPStatus.OK
    status, body = await make_get_request(api_postfix="/api/v1/auth",
                                          endpoint="/logout_all",
                                          token=token)
    assert status == expected_answer['status']
    assert body == expected_answer['body']


@pytest.mark.parametrize(
    'credentials, query_data, expected_answer',
    [
        (
                {
                    "login": "new_login",
                    "password": "123qwe"
                },
                {
                    "old_password": "123qwe",
                    "new_password": "qwe123",
                    "new_password_repeat": "qwe123"
                },
                {'status': HTTPStatus.OK, 'body': None}
        )
    ]
)
@pytest.mark.asyncio
async def test_change_pwd(make_post_request, credentials, query_data, expected_answer):
    status_login, token, refresh_token = await make_post_request(api_postfix="/api/v1/auth",
                                                                 endpoint="/login",
                                                                 query_data=credentials)
    assert status_login == HTTPStatus.OK
    assert refresh_token is not None

    status, body, _ = await make_post_request(api_postfix="/api/v1/auth",
                                              endpoint="/change_pwd",
                                              query_data=query_data,
                                              access_token=token,
                                              refresh_token=refresh_token)
    assert status == expected_answer['status']
    assert body == expected_answer['body']


@pytest.mark.parametrize(
    'credentials, expected_answer',
    [
        (
                {
                    "login": "new_login",
                    "password": "qwe123"
                },
                {'status': HTTPStatus.OK, 'body': None}
        )
    ]
)
@pytest.mark.asyncio
async def test_deactivate_user(make_post_request, credentials, expected_answer):
    status_login, token, _ = await make_post_request(api_postfix="/api/v1/auth",
                                                     endpoint="/login",
                                                     query_data=credentials)
    assert status_login == HTTPStatus.OK
    status, body, _ = await make_post_request(api_postfix="/api/v1/auth",
                                              endpoint="/deactivate_user",
                                              access_token=token)
    assert status == expected_answer['status']
    assert body == expected_answer['body']
