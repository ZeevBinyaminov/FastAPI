"""replace text/token lengths with bytecode length

Revision ID: 0006_bytecode_length
Revises: 0005_contracts_tables
Create Date: 2025-12-29 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0006_bytecode_length"
down_revision: Union[str, None] = "0005_contracts_tables"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        """
        ALTER TABLE request_history
            DROP COLUMN IF EXISTS input_text_length,
            DROP COLUMN IF EXISTS input_token_count,
            ADD COLUMN IF NOT EXISTS bytecode_length INTEGER;
        """
    )


def downgrade() -> None:
    op.execute(
        """
        ALTER TABLE request_history
            DROP COLUMN IF EXISTS bytecode_length,
            ADD COLUMN IF NOT EXISTS input_text_length INTEGER,
            ADD COLUMN IF NOT EXISTS input_token_count INTEGER;
        """
    )
