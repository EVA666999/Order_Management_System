"""Initial migration

Revision ID: c0d5dfb75db6
Revises: 76d85563e657
Create Date: 2025-04-02 20:37:14.935115

"""

from typing import Sequence, Union


# revision identifiers, used by Alembic.
revision: str = "c0d5dfb75db6"
down_revision: Union[str, None] = "76d85563e657"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    # ### end Alembic commands ###
