"""create request history

Revision ID: 0001_create_request_history
Revises: 
Create Date: 2024-01-01 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "0001_create_request_history"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "request_history",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("smart_contract_address", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("request_headers", sa.JSON(), nullable=True),
        sa.Column("response_status", sa.String(), nullable=True),
        sa.Column("response_data", sa.JSON(), nullable=True),
        sa.Column("processing_time_ms", sa.Integer(), nullable=True),
        sa.Column("input_text_length", sa.Integer(), nullable=True),
        sa.Column("input_token_count", sa.Integer(), nullable=True),
        sa.Column("timestamp", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_request_history_id", "request_history", ["id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_request_history_id", table_name="request_history")
    op.drop_table("request_history")
