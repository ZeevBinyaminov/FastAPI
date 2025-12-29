"""add missing request_history columns

Revision ID: 0002_add_request_history_columns
Revises: 0001_create_request_history
Create Date: 2025-12-29 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0002_add_request_history_columns"
down_revision: Union[str, None] = "0001_create_request_history"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        """
        ALTER TABLE request_history
            ADD COLUMN IF NOT EXISTS created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT NOW(),
            ADD COLUMN IF NOT EXISTS request_headers JSON,
            ADD COLUMN IF NOT EXISTS response_status VARCHAR,
            ADD COLUMN IF NOT EXISTS response_data JSON,
            ADD COLUMN IF NOT EXISTS processing_time_ms INTEGER,
            ADD COLUMN IF NOT EXISTS bytecode_length INTEGER,
            ADD COLUMN IF NOT EXISTS timestamp TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT NOW();
        """
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_request_history_id ON request_history (id);"
    )


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS ix_request_history_id;")
    op.execute(
        """
        ALTER TABLE request_history
            DROP COLUMN IF EXISTS timestamp,
            DROP COLUMN IF EXISTS bytecode_length,
            DROP COLUMN IF EXISTS processing_time_ms,
            DROP COLUMN IF EXISTS response_data,
            DROP COLUMN IF EXISTS response_status,
            DROP COLUMN IF EXISTS request_headers,
            DROP COLUMN IF EXISTS created_at;
        """
    )
