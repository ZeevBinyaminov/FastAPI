"""drop image columns from request_history

Revision ID: 0004_drop_image_columns
Revises: 0003_drop_sc_addr
Create Date: 2025-12-29 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0004_drop_image_columns"
down_revision: Union[str, None] = "0003_drop_sc_addr"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        """
        ALTER TABLE request_history
            DROP COLUMN IF EXISTS image_width,
            DROP COLUMN IF EXISTS image_height,
            DROP COLUMN IF EXISTS image_bytes;
        """
    )


def downgrade() -> None:
    op.execute(
        """
        ALTER TABLE request_history
            ADD COLUMN IF NOT EXISTS image_width INTEGER,
            ADD COLUMN IF NOT EXISTS image_height INTEGER,
            ADD COLUMN IF NOT EXISTS image_bytes INTEGER;
        """
    )
