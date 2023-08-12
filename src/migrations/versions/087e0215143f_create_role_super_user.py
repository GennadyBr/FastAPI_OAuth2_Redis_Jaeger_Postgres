"""create role super_user

Revision ID: 087e0215143f
Revises: 7c4f75442606
Create Date: 2023-08-11 11:38:05.505805

"""
import uuid

from alembic import op

# revision identifiers, used by Alembic.
revision = '087e0215143f'
down_revision = '7c4f75442606'
branch_labels = None
depends_on = None


def upgrade() -> None:
    from sqlalchemy.sql import insert, table, column
    from sqlalchemy import orm

    # перечисляем таблицы с полями, которые будем заполнять
    role = table('role', column('uuid'), column('name'))

    # создаем коннекшн к базе данных
    bind = op.get_bind()
    session = orm.Session(bind=bind)

    # создаем РОЛЬ супер пользователя
    data = {"uuid": uuid.uuid4(), "name": "super_user", }
    session.execute(insert(role).values(data))
    session.commit()
    session.close()

def downgrade() -> None:
    pass
