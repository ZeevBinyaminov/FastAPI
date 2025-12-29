"""remove smart_contract_address from request_history

Revision ID: 0003_drop_sc_addr
Revises: 0002_add_request_history_columns
Create Date: 2025-12-29 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0003_drop_sc_addr"
down_revision: Union[str, None] = "0002_add_request_history_columns"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        "ALTER TABLE request_history DROP COLUMN IF EXISTS smart_contract_address;"
    )


def downgrade() -> None:
    op.execute(
        "ALTER TABLE request_history ADD COLUMN IF NOT EXISTS smart_contract_address VARCHAR NOT NULL DEFAULT 'unknown';"
    )
