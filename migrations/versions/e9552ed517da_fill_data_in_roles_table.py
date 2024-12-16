"""fill data in roles table

Revision ID: e9552ed517da
Revises: 2b3b02582ecf
Create Date: 2024-12-16 21:43:26.748993

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e9552ed517da'
down_revision: Union[str, None] = '2b3b02582ecf'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Fill values for table roles
    op.execute("INSERT INTO  roles (name) VALUES ('admin')")
    op.execute("INSERT INTO  roles (name) VALUES ('moderator')")
    op.execute("INSERT INTO  roles (name) VALUES ('user')")


def downgrade() -> None:
    # Delete inserted values
    op.execute("DELETE FROM roles WHERE name IN ('admin', 'moderator', 'user')")
    # ### end Alembic commands ###
