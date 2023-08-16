from http import HTTPStatus
from uuid import uuid4

import pytest
from sqlalchemy import select
from sqlalchemy import MetaData, create_engine
from sqlalchemy.ext.automap import automap_base

from settings import user_db_settings

metadata = MetaData()
engine = create_engine(user_db_settings.url, echo=False)
metadata.reflect(engine)
Base = automap_base(metadata=metadata)
Base.prepare()
Role = Base.classes.role
UserRole = Base.classes.user_role
User = Base.classes.users


# тест 1: добавление новой роли
@pytest.mark.parametrize(
    'test_data, query_data, expected_answer',
    [
        # несуществующая роль
        (
                {},
                {'name': 'premium'},
                {'status_code': HTTPStatus.OK, 
                 'body': {
                     'name': 'premium',
                     }, 
                 }
        ),
        
        # # существующая роль
        # (
        #         {
        #             'uuid': uuid4(),
        #             'name': 'premium'
        #             },
        #         {'name': 'premium'},
        #         {'status_code': HTTPStatus.FORBIDDEN, 
        #          'body': {'Role is not created'}, 
        #          }
        # ),
        
    ]
)
@pytest.mark.asyncio
async def test_add_new_role(db_session, make_post_request, 
                            test_data: dict, 
                            query_data: dict, 
                            expected_answer: dict,
                            ):
    """Тесты добавления новой роли"""

    try:
    
        if test_data:
            new_role = Role(**test_data)
            db_session.add(new_role)
            db_session.commit()

        status, body = await make_post_request(api_postfix='/api/v1/role',
                                            endpoint='/new',
                                            query_data=query_data)
    
        assert status == expected_answer['status_code']
        assert body['name'] == expected_answer['body']['name']
        
        if status == HTTPStatus.OK:
        
            query = select(Role).where(Role.name == query_data['name'])
            res = db_session.execute(query)
            db_record = res.scalars().one()
            
            assert db_record.name == body['name']
            assert str(db_record.uuid) == str(body['uuid'])
            
        
    finally:

        db_session.query(Role).delete()
        db_session.commit()


# тест 2: обновление роли
@pytest.mark.parametrize(
    'test_data, query_params, query_data, expected_answer',
    [
        # существующая роль
        (
                {
                    'uuid': 'ac58efef-be6f-410f-add8-d3ce339739f0',
                    'name': 'premium'
                    },
                {'role_id': 'ac58efef-be6f-410f-add8-d3ce339739f0'},
                {'name': 'super premium'},
                {'status_code': HTTPStatus.OK, 
                 'body': {
                     'uuid': 'ac58efef-be6f-410f-add8-d3ce339739f0',
                     'name': 'super premium'
                 }, 
                 }
        ),
        # несуществующая роль
        (
                {},
                {'role_id': 'ac58efef-be6f-410f-add8-d3ce339739f0'},
                {'name': 'super premium'},
                {'status_code': HTTPStatus.NOT_FOUND, 
                 'body': {'detail': 'Role does not exist'}, 
                 }
        ),
    ]
)
@pytest.mark.asyncio
async def test_update_role(db_session, make_patch_request, 
                           test_data: dict, 
                           query_params: dict, 
                           query_data: dict, 
                           expected_answer: dict,
                           ):
    """Тесты обновления существующей роли"""
   
    try:

        if test_data:
            new_role = Role(**test_data)
            db_session.add(new_role)
            db_session.commit()

        status, body = await make_patch_request(api_postfix='/api/v1/role', 
                                            endpoint='/update',
                                            query_data=query_data, 
                                            params=query_params,
                                            )
        
        assert status == expected_answer['status_code']
        assert body == expected_answer['body']

        if status == HTTPStatus.OK:
        
            query = select(Role).where(Role.name == query_data['name'])
            db_session.execute(query)
            res = db_session.execute(query)
            db_record = res.scalars().one()
            
            assert db_record.name == body['name']
            assert str(db_record.uuid) == str(body['uuid'])
    
    finally:

        db_session.query(Role).delete()
        db_session.commit()


# тест 3: получение информации о существующей роли
@pytest.mark.parametrize(
    'test_data, query_params, expected_answer',
    [
        # существующая роль
        (
                {
                    'uuid': 'ac58efef-be6f-410f-add8-d3ce339739f0',
                    'name': 'premium'
                    },
                {'role_id': 'ac58efef-be6f-410f-add8-d3ce339739f0'},
                {'status_code': HTTPStatus.OK, 
                 'body': {
                     'uuid': 'ac58efef-be6f-410f-add8-d3ce339739f0',
                     'name': 'premium'
                 }, 
                 }
        ),
        # несуществующая роль
        (
                {},
                {'role_id': 'ac58efef-be6f-410f-add8-d3ce339739f0'},
                {'status_code': HTTPStatus.NOT_FOUND, 
                 'body': {'detail': 'Role does not exist'}, 
                 }
        ),
    ]
)
@pytest.mark.asyncio
async def test_get_role(db_session, make_get_request, 
                           test_data: dict, 
                           query_params: dict, 
                           expected_answer: dict,
                           ):
    """Тесты получения информации о роли"""

    try:

        if test_data:
            new_role = Role(**test_data)
            db_session.add(new_role)
            db_session.commit()

        status, body = await make_get_request(api_postfix='/api/v1/role', 
                                            endpoint='/',
                                            query_data=query_params,
                                            )
        
        assert status == expected_answer['status_code']
        assert body == expected_answer['body']

        if status == HTTPStatus.OK:
        
            query = select(Role).where(Role.name == test_data['name'])
            res = db_session.execute(query)
            db_record = res.scalars().one()
            
            assert db_record.name == body['name']
            assert str(db_record.uuid) == str(body['uuid'])
    
    finally:

        db_session.query(Role).delete()
        db_session.commit()


# тест 4: удаление роли
@pytest.mark.parametrize(
    'test_data, query_params, expected_answer',
    [
        # существующая роль
        (
                {
                    'uuid': 'ac58efef-be6f-410f-add8-d3ce339739f0',
                    'name': 'premium'
                    },
                {'role_id': 'ac58efef-be6f-410f-add8-d3ce339739f0'},
                {'status_code': HTTPStatus.OK, 
                #  'body': {True}, 
                 }
        ),
        # # несуществующая роль
        # (
        #         {},
        #         {'role_id': 'ac58efef-be6f-410f-add8-d3ce339739f0'},
        #         {'status_code': HTTPStatus.NOT_FOUND, 
        #          'body': {'Role is not found for deleting'}, 
        #          }
        # ),
    ]
)
@pytest.mark.asyncio
async def test_delete_role(db_session, make_delete_request, 
                           test_data: dict, 
                           query_params: dict, 
                           expected_answer: dict,
                           ):
    """Тесты удаления роли"""
    
    try:
        if test_data:
            new_role = Role(**test_data)
            db_session.add(new_role)
            db_session.commit()

        status, body = await make_delete_request(api_postfix='/api/v1/role', 
                                            endpoint='/',
                                            params=query_params,
                                            )

        assert status == expected_answer['status_code']
        
        if status != HTTPStatus.OK:
            assert body == expected_answer['body']

        if status == HTTPStatus.OK:
        
            query = select(Role).where(Role.name == test_data['name'])
            res = db_session.execute(query)
            db_record = res.scalars().first()
            
            assert db_record is None
    
    finally:

        db_session.query(Role).delete()
        db_session.commit()


# тест 5: получение ролей пользователя
@pytest.mark.parametrize(
    'test_data, query_params, expected_answer',
    [
        # существующий пользователь
        (
                {
                    'role': {
                        'uuid': 'ac58efef-be6f-410f-add8-d3ce339739f0',
                        'name': 'premium',
                    },
                    'user': {
                        'uuid': '124151a3-f1ea-45bf-9b19-3e90eeed1f9b',
                        'name': 'Testname',
                        'surname': 'Testsurname',
                        'login': 'iamtest',
                        'email': 'test@example.com',
                        'is_active': True,
                        'password': '',
                    },
                    },
                {'user_id': '124151a3-f1ea-45bf-9b19-3e90eeed1f9b'},
                {'status_code': HTTPStatus.OK, 
                 'body': [
                     {
                         'uuid': 'ac58efef-be6f-410f-add8-d3ce339739f0',
                         'name': 'premium',
                         }
                 ]   
                 }
        ),
        # несуществующий пользователь
        (
                {},
                {'user_id': '124151a3-f1ea-45bf-9b19-3e90eeed1f9b'},
                {'status_code': HTTPStatus.NOT_FOUND, 
                 'body': {'detail': 'User does not exist'}, 
                 }
        ),
    ]
)
@pytest.mark.asyncio
async def test_get_user_role(db_session, make_get_request, 
                           test_data: dict, 
                           query_params: dict, 
                           expected_answer: dict,
                           ):
    """Тесты получения ролей пользователя"""

    try:

        if test_data:
            new_role = Role(**test_data['role'])
            db_session.add(new_role)

            new_user = User(**test_data['user'])
            db_session.add(new_user)

            new_user_role = UserRole(
                uuid=uuid4(),
                user_id=test_data['user']['uuid'],
                role_id=test_data['role']['uuid'],
                )
            db_session.add(new_user_role)

            db_session.commit()

        status, body = await make_get_request(api_postfix='/api/v1/role', 
                                            endpoint='/user',
                                            query_data=query_params,
                                            )
    
        assert status == expected_answer['status_code']
        assert body == expected_answer['body']

        if status == HTTPStatus.OK:

            query = select(Role). \
                join(UserRole, Role.uuid == UserRole.role_id). \
                join(User, UserRole.user_id == User.uuid). \
                where(UserRole.user_id == test_data['user']['uuid'])
            res = db_session.execute(query)
            roles = res.scalars().all()
            
            db_roles = [{'uuid': str(role.uuid), 'name': role.name} for role in roles]
            assert db_roles == body

    finally:

        db_session.query(UserRole).delete()
        db_session.query(User).delete()
        db_session.query(Role).delete()
        db_session.commit()


# тест 6: назначение роли пользователю
@pytest.mark.parametrize(
    'test_data, query_data, expected_answer',
    [
        # существующий пользователь
        (
                {
                    'role': {
                        'uuid': 'ac58efef-be6f-410f-add8-d3ce339739f0',
                        'name': 'premium',
                    },
                    'user': {
                        'uuid': '124151a3-f1ea-45bf-9b19-3e90eeed1f9b',
                        'name': 'Testname',
                        'surname': 'Testsurname',
                        'login': 'iamtest',
                        'email': 'test@example.com',
                        'is_active': True,
                        'password': '',
                    },
                    },
                {
                    'user_id': '124151a3-f1ea-45bf-9b19-3e90eeed1f9b',
                    'role_id': 'ac58efef-be6f-410f-add8-d3ce339739f0'
                    },
                {'status_code': HTTPStatus.OK, 
                 'body': True,
                 }
        ),
        # несуществующий пользователь
        (
                {
                    'role': {
                        'uuid': 'ac58efef-be6f-410f-add8-d3ce339739f0',
                        'name': 'premium',
                    },
                },
                {
                    'user_id': '124151a3-f1ea-45bf-9b19-3e90eeed1f9b',
                    'role_id': 'ac58efef-be6f-410f-add8-d3ce339739f0'
                    },
                {'status_code': HTTPStatus.NOT_FOUND, 
                 'body': {'detail': 'User does not exist'}, 
                 }
        ),
        # несуществующая роль
        (
                {
                    'user': {
                        'uuid': '124151a3-f1ea-45bf-9b19-3e90eeed1f9b',
                        'name': 'Testname',
                        'surname': 'Testsurname',
                        'login': 'iamtest',
                        'email': 'test@example.com',
                        'is_active': True,
                        'password': '',
                    },
                    },
                {
                    'user_id': '124151a3-f1ea-45bf-9b19-3e90eeed1f9b',
                    'role_id': 'ac58efef-be6f-410f-add8-d3ce339739f0'
                    },
                {'status_code': HTTPStatus.NOT_FOUND, 
                 'body': {'detail': 'Role does not exist'}, 
                 }
        ),
    ]
)
@pytest.mark.asyncio
async def test_add_role_to_user(db_session, make_post_request, 
                           test_data: dict, 
                           query_data: dict, 
                           expected_answer: dict,
                           ):
    """Тесты добавления ролей пользователю"""

    try:

        if test_data:
            if test_data.get('role', None):
                new_role = Role(**test_data['role'])
                db_session.add(new_role)

            if test_data.get('user', None):
                new_user = User(**test_data['user'])
                db_session.add(new_user)

            db_session.commit()

        status, body = await make_post_request(api_postfix='/api/v1/role', 
                                            endpoint='/role-to-user',
                                            query_data=query_data, 
                                            )
    
        assert status == expected_answer['status_code']
        assert body == expected_answer['body']

        if status == HTTPStatus.OK:

            query = select(Role). \
                join(UserRole, Role.uuid == UserRole.role_id). \
                join(User, UserRole.user_id == User.uuid). \
                where(UserRole.user_id == test_data['user']['uuid'])
            res = db_session.execute(query)
            roles = res.scalars().all()
            
            db_roles = [str(role.uuid) for role in roles]
            assert len(db_roles) != 0
    
    finally:

        db_session.query(UserRole).delete()
        db_session.query(User).delete()
        db_session.query(Role).delete()
        db_session.commit()


# тест 7: удаление роли у пользователя
@pytest.mark.parametrize(
    'test_data, query_data, expected_answer',
    [
        # существующий пользователь
        (
                {
                    'role': {
                        'uuid': 'ac58efef-be6f-410f-add8-d3ce339739f0',
                        'name': 'premium',
                    },
                    'user': {
                        'uuid': '124151a3-f1ea-45bf-9b19-3e90eeed1f9b',
                        'name': 'Testname',
                        'surname': 'Testsurname',
                        'login': 'iamtest',
                        'email': 'test@example.com',
                        'is_active': True,
                        'password': '',
                    },
                    },
                {
                    'user_id': '124151a3-f1ea-45bf-9b19-3e90eeed1f9b',
                    'role_id': 'ac58efef-be6f-410f-add8-d3ce339739f0'
                    },
                {'status_code': HTTPStatus.OK, 
                 'body': True
                 }
        ),
        # несуществующий пользователь
        (
                {
                    'role': {
                        'uuid': 'ac58efef-be6f-410f-add8-d3ce339739f0',
                        'name': 'premium',
                    },
                },
                {
                    'user_id': '124151a3-f1ea-45bf-9b19-3e90eeed1f9b',
                    'role_id': 'ac58efef-be6f-410f-add8-d3ce339739f0'
                    },
                {'status_code': HTTPStatus.NOT_FOUND, 
                 'body': {'detail': 'User does not exist'}, 
                 }
        ),
        # несуществующая роль
        (
                {
                    'user': {
                        'uuid': '124151a3-f1ea-45bf-9b19-3e90eeed1f9b',
                        'name': 'Testname',
                        'surname': 'Testsurname',
                        'login': 'iamtest',
                        'email': 'test@example.com',
                        'is_active': True,
                        'password': '',
                    },
                    },
                {
                    'user_id': '124151a3-f1ea-45bf-9b19-3e90eeed1f9b',
                    'role_id': '3cd8a1df-4d27-4abb-81e9-b2e820e7d7a1'
                    },
                {'status_code': HTTPStatus.NOT_FOUND, 
                 'body': {'detail': 'Role does not exist'}, 
                 }
        ),
    ]
)
@pytest.mark.asyncio
async def test_delete_role_from_user(db_session, make_delete_request, 
                           test_data: dict, 
                           query_data: dict, 
                           expected_answer: dict,
                           ):
    """Тесты удаления ролей пользователя"""

    try:

        if test_data:
            if test_data.get('role', None):
                new_role = Role(**test_data['role'])
                db_session.add(new_role)

            if test_data.get('user', None):
                new_user = User(**test_data['user'])
                db_session.add(new_user)

            if test_data.get('role', None) and test_data.get('user', None):
                new_user_role = UserRole(
                    uuid=uuid4(),
                    user_id=test_data['user']['uuid'],
                    role_id=test_data['role']['uuid'],
                    )
                db_session.add(new_user_role)

            db_session.commit()

        status, body = await make_delete_request(api_postfix='/api/v1/role', 
                                            endpoint='/role-to-user',
                                            query_data=query_data,
                                            )
    
        assert status == expected_answer['status_code']
        assert body == expected_answer['body']
        
        if status == HTTPStatus.OK:

            query = select(Role). \
                join(UserRole, Role.uuid == UserRole.role_id). \
                join(User, UserRole.user_id == User.uuid). \
                where(UserRole.user_id == query_data['user_id'])
            res = db_session.execute(query)
            roles = res.scalars().all()
            
            assert len(roles) == 0

    finally:

        db_session.query(UserRole).delete()
        db_session.query(User).delete()
        db_session.query(Role).delete()
        db_session.commit()
