"""dump_db

Revision ID: 123456789ab1
Revises: 087e0215143f
Create Date: 2023-08-11 23:01:05.505805

"""
import uuid

from alembic import op
import sqlalchemy as sa
from datetime import datetime
from db.models import User, Role

# revision identifiers, used by Alembic.
revision = '123456789ab1'
down_revision = '087e0215143f'
branch_labels = None
depends_on = None


def upgrade() -> None:
    from sqlalchemy.sql import insert, table, column
    from sqlalchemy import orm

    # перечисляем таблицы с полями, которые будем заполнять
    role = table('role', column('uuid'), column('name'))
    users = table('users', column('uuid'), column('name'), column('surname'), column('login'), column('email'),
                  column('is_active'), column('password'))
    entry = table('entry', column('uuid'), column('user_id'), column('user_agent'), column('date_time'),
                  column('refresh_token'), column('is_active'))
    user_role = table('user_role', column('uuid'), column('user_id'), column('role_id'))

    # создаем коннекшн к базе данных
    bind = op.get_bind()
    session = orm.Session(bind=bind)

    # создаем РОЛИ
    data = {"uuid": uuid.uuid4(), "name": "vip_user", }
    session.execute(insert(role).values(data))
    # session.commit()

    data = {"uuid": uuid.uuid4(), "name": "premium_user", }
    session.execute(insert(role).values(data))
    # session.commit()

    # создаем пользователей
    data = {"uuid": uuid.uuid4(), 'name': "Mark", 'surname': "Markov", 'login': "mark_markov",
            'email': 'mark_markov@email.com', 'is_active': True, 'password': "pass1", }
    session.execute(insert(users).values(data))
    # session.commit()

    data = {"uuid": uuid.uuid4(), 'name': "Grisha", 'surname': "Grishin", 'login': "grisha_grishin",
            'email': 'grisha_grishin@email.com', 'is_active': True, 'password': "pass2", }
    session.execute(insert(users).values(data))
    # session.commit()

    data = {"uuid": uuid.uuid4(), 'name': "Victor", 'surname': "Vitin", 'login': "victor_vitin",
            'email': 'victor_vitin@email.com', 'is_active': True, 'password': "pass3", }
    session.execute(insert(users).values(data))
    # session.commit()


    # создаем список uuid пользователей сгенерированных на предыдущем шаге
    user_id_list = [uuid_value for uuid_value in session.query(User.uuid)]#.distinct()]
    # session.commit()

    # создаем историю входов в базу
    data = {"uuid": uuid.uuid4(), 'user_id': user_id_list[0][0], 'user_agent': "agent1", 'date_time': datetime.utcnow(),
            'refresh_token': "refresh1", 'is_active': True, }
    session.execute(insert(entry).values(data))
    # session.commit()

    data = {"uuid": uuid.uuid4(), 'user_id': user_id_list[1][0], 'user_agent': "agent2", 'date_time': datetime.utcnow(),
            'refresh_token': "refresh2", 'is_active': True, }
    session.execute(insert(entry).values(data))
    # session.commit()

    data = {"uuid": uuid.uuid4(), 'user_id': user_id_list[2][0], 'user_agent': "agent3", 'date_time': datetime.utcnow(),
            'refresh_token': "refresh3", 'is_active': True, }
    session.execute(insert(entry).values(data))
    # session.commit()

    # создаем список uuid ролей сгенерированных на предыдущем шаге
    role_id_list = [uuid_value for uuid_value in session.query(Role.uuid)]#.distinct()]

    # создаем базу связей ролей и пользователей
    data = {"uuid": uuid.uuid4(), 'user_id': user_id_list[0][0], 'role_id': role_id_list[0][0],}
    session.execute(insert(user_role).values(data))
    # session.commit()

    data = {"uuid": uuid.uuid4(), 'user_id': user_id_list[1][0], 'role_id': role_id_list[1][0],}
    session.execute(insert(user_role).values(data))
    # session.commit()

    data = {"uuid": uuid.uuid4(), 'user_id': user_id_list[2][0], 'role_id': role_id_list[2][0],}
    session.execute(insert(user_role).values(data))
    session.commit()


def downgrade() -> None:
    pass
