"""addforeignkeytoPosts

Revision ID: 6840ecc523ec
Revises: e619c3b2c8a1
Create Date: 2025-04-20 21:23:42.622597

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6840ecc523ec'
down_revision = 'e619c3b2c8a1'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('posts', sa.Column('owner_id', sa.Integer(), nullable=False))
    op.create_foreign_key('post_users_fk', source_table='posts', referent_table="users",
                           local_cols =['owner_id'], remote_cols=['id'], ondelete="CASCADE")
    pass


def downgrade():
    op.drop_constraint('post_users_fk', table_name='posts')
    op.drop_column('posts', 'owner_id')
    pass
