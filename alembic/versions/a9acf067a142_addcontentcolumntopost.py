"""addcontentcolumntopost

Revision ID: a9acf067a142
Revises: ba9643c6e99e
Create Date: 2025-04-20 21:09:19.741005

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a9acf067a142'
down_revision = 'ba9643c6e99e'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('posts', sa.Column('content', sa.String(), nullable=False))
    pass


def downgrade():
    op.drop_column('posts', 'content')
    pass
