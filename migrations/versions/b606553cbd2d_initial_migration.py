"""Initial migration

Revision ID: b606553cbd2d
Revises: 
Create Date: 2025-01-07 00:08:38.935419

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b606553cbd2d'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('roles',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=20), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )
    op.create_index(op.f('ix_roles_id'), 'roles', ['id'], unique=False)
    op.create_table('tags',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('name', sa.String(length=50), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )
    op.create_table('users',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('first_name', sa.String(length=50), nullable=False),
    sa.Column('last_name', sa.String(length=50), nullable=False),
    sa.Column('phone', sa.String(length=15), nullable=False),
    sa.Column('email', sa.String(length=70), nullable=False),
    sa.Column('username', sa.String(length=50), nullable=False),
    sa.Column('avatar_url', sa.String(length=255), nullable=True),
    sa.Column('role_id', sa.Integer(), nullable=False),
    sa.Column('password', sa.String(length=255), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.Column('is_banned', sa.Boolean(), nullable=False),
    sa.Column('is_confirmed', sa.Boolean(), nullable=False),
    sa.ForeignKeyConstraint(['role_id'], ['roles.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)
    op.create_index(op.f('ix_users_username'), 'users', ['username'], unique=True)
    op.create_table('posts',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('original_image_url', sa.String(length=500), nullable=False),
    sa.Column('image_url', sa.String(length=500), nullable=False),
    sa.Column('description', sa.String(length=500), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('tokens',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('access_token', sa.String(length=450), nullable=False),
    sa.Column('refresh_token', sa.String(length=450), nullable=False),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_tokens_access_token'), 'tokens', ['access_token'], unique=False)
    op.create_index(op.f('ix_tokens_id'), 'tokens', ['id'], unique=False)
    op.create_index(op.f('ix_tokens_user_id'), 'tokens', ['user_id'], unique=False)
    op.create_table('comments',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('post_id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('comment', sa.String(length=300), nullable=False),
    sa.Column('is_update', sa.Boolean(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['post_id'], ['posts.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('edited_images',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('post_id', sa.Integer(), nullable=False),
    sa.Column('image_url', sa.String(length=300), nullable=False),
    sa.Column('image_filter', sa.String(length=100), nullable=False),
    sa.ForeignKeyConstraint(['post_id'], ['posts.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('post_tag',
    sa.Column('post_id', sa.Integer(), nullable=False),
    sa.Column('tag_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['post_id'], ['posts.id'], ),
    sa.ForeignKeyConstraint(['tag_id'], ['tags.id'], ),
    sa.PrimaryKeyConstraint('post_id', 'tag_id')
    )
    op.create_table('scores',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('post_id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('score', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['post_id'], ['posts.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )

    # Fill values for the table 'roles'
    op.execute("INSERT INTO  roles (name) VALUES ('admin')")
    op.execute("INSERT INTO  roles (name) VALUES ('moderator')")
    op.execute("INSERT INTO  roles (name) VALUES ('user')")
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('scores')
    op.drop_table('post_tag')
    op.drop_table('edited_images')
    op.drop_table('comments')
    op.drop_index(op.f('ix_tokens_user_id'), table_name='tokens')
    op.drop_index(op.f('ix_tokens_id'), table_name='tokens')
    op.drop_index(op.f('ix_tokens_access_token'), table_name='tokens')
    op.drop_table('tokens')
    op.drop_table('posts')
    op.drop_index(op.f('ix_users_username'), table_name='users')
    op.drop_index(op.f('ix_users_id'), table_name='users')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_table('users')
    op.drop_table('tags')
    op.drop_index(op.f('ix_roles_id'), table_name='roles')
    op.drop_table('roles')
    # ### end Alembic commands ###
