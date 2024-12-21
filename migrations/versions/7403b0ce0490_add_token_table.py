"""add Token table

Revision ID: 7403b0ce0490
Revises: 
Create Date: 2024-12-21 14:38:53.261459

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7403b0ce0490'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('token',
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('access_token', sa.String(length=450), nullable=False),
    sa.Column('refresh_toke', sa.String(length=450), nullable=False),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('access_token')
    )
    op.drop_table('scores')
    op.add_column('posts', sa.Column('original_image_url', sa.String(length=500), nullable=False))
    op.add_column('posts', sa.Column('image_url', sa.String(length=500), nullable=False))
    op.drop_column('posts', 'score_result')
    op.create_unique_constraint(None, 'tags', ['name'])
    op.drop_column('users', 'refresh_token')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('refresh_token', sa.VARCHAR(length=255), autoincrement=False, nullable=True))
    op.drop_constraint(None, 'tags', type_='unique')
    op.add_column('posts', sa.Column('score_result', sa.DOUBLE_PRECISION(precision=53), autoincrement=False, nullable=True))
    op.drop_column('posts', 'image_url')
    op.drop_column('posts', 'original_image_url')
    op.create_table('scores',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('post_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('user_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('score', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.ForeignKeyConstraint(['post_id'], ['posts.id'], name='scores_post_id_fkey'),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], name='scores_user_id_fkey'),
    sa.PrimaryKeyConstraint('id', name='scores_pkey')
    )
    op.drop_table('token')
    # ### end Alembic commands ###
