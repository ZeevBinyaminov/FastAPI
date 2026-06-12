"""change contracts.prediction from integer to json

Revision ID: 0007_prediction_to_json
Revises: 0006_bytecode_length
Create Date: 2026-06-10 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op

revision: str = "0007_prediction_to_json"
down_revision: Union[str, None] = "0006_bytecode_length"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        """
        ALTER TABLE contracts
            ALTER COLUMN prediction TYPE JSONB
            USING to_jsonb(ARRAY[]::text[]);
        """
    )


def downgrade() -> None:
    op.execute(
        """
        ALTER TABLE contracts
            ALTER COLUMN prediction TYPE INTEGER
            USING 0;
        """
    )
