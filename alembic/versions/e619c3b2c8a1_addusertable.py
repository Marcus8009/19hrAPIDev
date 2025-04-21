"""addusertable

Revision ID: e619c3b2c8a1
Revises: a9acf067a142
Create Date: 2025-04-20 21:15:00.828914

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e619c3b2c8a1'
down_revision = 'a9acf067a142'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('users',
                    sa.Column('id', sa.Integer(), nullable=False, primary_key=True),
                    sa.Column('email', sa.String(), nullable=False, unique=True),
                    sa.Column('password', sa.String(), nullable=False),
                    sa.Column('created_at', sa.TIMESTAMP(timezone=True),
                               server_default=sa.func.now(), nullable=False),
                    sa.PrimaryKeyConstraint('id'),
                    sa.UniqueConstraint('email')
                    )
    pass

def downgrade():
    op.drop_table('users')
    pass
