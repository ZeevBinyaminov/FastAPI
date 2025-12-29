"""create contracts tables

Revision ID: 0005_contracts_tables
Revises: 0004_drop_image_columns
Create Date: 2025-12-29 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "0005_contracts_tables"
down_revision: Union[str, None] = "0004_drop_image_columns"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS contracts (
            id SERIAL PRIMARY KEY,
            bytecode TEXT NOT NULL,
            prediction INTEGER NOT NULL,
            processing_time_ms INTEGER,
            created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL
        );
        """
    )
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS contract_metadata (
            id SERIAL PRIMARY KEY,
            contract_id INTEGER NOT NULL UNIQUE REFERENCES contracts(id) ON DELETE CASCADE,
            total_instructions INTEGER NOT NULL,
            unique_instructions INTEGER NOT NULL,
            block_dependent_count INTEGER NOT NULL,
            block_dependency_index DOUBLE PRECISION NOT NULL,
            has_TIMESTAMP INTEGER NOT NULL,
            has_NUMBER INTEGER NOT NULL,
            has_DIFFICULTY INTEGER NOT NULL,
            has_GASLIMIT INTEGER NOT NULL,
            has_COINBASE INTEGER NOT NULL,
            has_BLOCKHASH INTEGER NOT NULL,
            environmental_instructions_count INTEGER NOT NULL,
            environmental_ratio DOUBLE PRECISION NOT NULL,
            unique_environmental_ops INTEGER NOT NULL,
            environmental_complexity DOUBLE PRECISION NOT NULL,
            balance_operations INTEGER NOT NULL,
            address_operations INTEGER NOT NULL,
            caller_operations INTEGER NOT NULL,
            origin_operations INTEGER NOT NULL,
            callvalue_operations INTEGER NOT NULL,
            external_dependency_index DOUBLE PRECISION NOT NULL,
            calldata_size_ops INTEGER NOT NULL,
            calldata_load_ops INTEGER NOT NULL,
            calldata_copy_ops INTEGER NOT NULL,
            total_calldata_ops INTEGER NOT NULL,
            calldata_density DOUBLE PRECISION NOT NULL,
            external_call_count INTEGER NOT NULL,
            has_external_calls INTEGER NOT NULL,
            call_value_ops INTEGER NOT NULL,
            call_gas_limit_ops INTEGER NOT NULL,
            potential_reentrancy_pattern INTEGER NOT NULL,
            reads_from_memory INTEGER NOT NULL,
            writes_to_memory INTEGER NOT NULL,
            memory_access_ratio DOUBLE PRECISION NOT NULL,
            pushes INTEGER NOT NULL,
            pops INTEGER NOT NULL,
            stack_imbalance INTEGER NOT NULL,
            stack_operations_ratio DOUBLE PRECISION NOT NULL,
            stack_underflow_risk INTEGER NOT NULL,
            total_gas_cost DOUBLE PRECISION NOT NULL,
            avg_gas_per_instruction DOUBLE PRECISION NOT NULL,
            max_gas_instruction DOUBLE PRECISION NOT NULL,
            high_gas_instructions INTEGER NOT NULL,
            gas_dos_risk_index DOUBLE PRECISION NOT NULL,
            arithmetic_ops_count INTEGER NOT NULL,
            arithmetic_density DOUBLE PRECISION NOT NULL,
            unsafe_arithmetic_pattern INTEGER NOT NULL,
            control_flow_ops INTEGER NOT NULL,
            jumpi_count INTEGER NOT NULL,
            conditional_branching_ratio DOUBLE PRECISION NOT NULL,
            control_flow_complexity DOUBLE PRECISION NOT NULL,
            caller_based_checks INTEGER NOT NULL,
            origin_usage INTEGER NOT NULL,
            access_control_ratio DOUBLE PRECISION NOT NULL,
            uses_origin_instead_caller INTEGER NOT NULL,
            balance_before_external_call INTEGER NOT NULL,
            randomness_ops_count INTEGER NOT NULL,
            has_bad_randomness_pattern INTEGER NOT NULL,
            dangerous_ops_count INTEGER NOT NULL,
            dangerous_ops_density DOUBLE PRECISION NOT NULL,
            opcode_entropy DOUBLE PRECISION NOT NULL,
            reentrancy_risk_score DOUBLE PRECISION NOT NULL,
            frontrunning_risk_score DOUBLE PRECISION NOT NULL,
            dos_risk_score DOUBLE PRECISION NOT NULL,
            arithmetic_risk_score DOUBLE PRECISION NOT NULL,
            overall_security_risk_score DOUBLE PRECISION NOT NULL,
            has_reentrancy_indicators INTEGER NOT NULL,
            has_unchecked_external_calls INTEGER NOT NULL,
            has_arithmetic_vulnerabilities INTEGER NOT NULL,
            has_access_control_issues INTEGER NOT NULL,
            has_dos_vulnerabilities INTEGER NOT NULL
        );
        """
    )


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS contract_metadata;")
    op.execute("DROP TABLE IF EXISTS contracts;")
