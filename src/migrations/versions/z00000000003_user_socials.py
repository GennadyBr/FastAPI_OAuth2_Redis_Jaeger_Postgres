"""create role super_user

Revision ID: z00000000003
Revises: 7c4f75442607
Create Date: 2023-08-29 20:06:05.505805

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from sqlalchemy.engine.reflection import Inspector

#making list of existing tables
conn = op.get_bind()
inspector = Inspector.from_engine(conn)
tables = inspector.get_table_names()


# revision identifiers, used by Alembic.
revision = 'z00000000003'
down_revision = '087e0215143f'
branch_labels = None
depends_on = None


def upgrade() -> None:
    if 'user_socials' not in tables:
        op.create_table('user_socials',
        sa.Column('uuid', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('sub_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('provider', sa.String(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.uuid'], ),
        sa.PrimaryKeyConstraint('uuid')
        )

def downgrade() -> None:
    pass
